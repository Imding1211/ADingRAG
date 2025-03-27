
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from controller.setting import SettingController
from controller.tool import ToolController

from pathlib import Path

import pandas as pd
import chromadb
import tempfile
import datetime
import humanize
import PyPDF2
import shutil
import base64
import uuid
import json
import re
import os

#=============================================================================#

class DatabaseController():

    def __init__(self):

        chromadb.api.client.SharedSystemClient.clear_system_cache()

        self.SettingController = SettingController()
        self.chunk_size        = self.SettingController.setting['text_splitter']['chunk_size']
        self.chunk_overlap     = self.SettingController.setting['text_splitter']['chunk_overlap']
        self.base_url          = self.SettingController.setting['server']['base_url']

        self.database_name      = self.SettingController.setting['database']['selected']
        self.database_path      = self.SettingController.setting['database'][self.database_name]['path']
        self.database_embedding = self.SettingController.setting['database'][self.database_name]['embedding_model']

        self.database = Chroma(
            persist_directory  = self.database_path, 
            embedding_function = OllamaEmbeddings(base_url=self.base_url, model=self.database_embedding)
            )

        self.ToolController = ToolController()

        self.time_zone = datetime.timezone(datetime.timedelta(hours=8))
        self.time_now  = datetime.datetime.now(tz=self.time_zone)
        self.time_end  = datetime.datetime(9999, 12, 31, 0, 0, 0, tzinfo=self.time_zone)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size         = self.chunk_size,
            chunk_overlap      = self.chunk_overlap,
            length_function    = len,
            is_separator_regex = False
            )

        self.remove_propositions_list = ['晨間運動的好處。',
            '開始一天時進行運動，能對你的身體與心理健康產生深遠的影響。', 
            '參與晨間運動可以提升你的精力、改善心情，並提高一天的專注力。', 
            '身體活動會刺激內啡肽的釋放，減輕壓力並促進幸福感。', 
            '此外，早晨運動有助於建立規律的生活習慣，使保持持續性變得更容易。', 
            '它還能通過調節身體的自然時鐘來改善睡眠品質。', 
            '無論是快走、瑜伽課還是健身房運動，甚至只需20到30分鐘，也能帶來顯著的效果。', 
            '養成晨間運動的習慣，將讓你體驗到更有成效且更健康的生活方式。', 
            '這是一個小小的改變，卻能帶來顯著且持久的益處。']

#-----------------------------------------------------------------------------#

    def calculate_existing_ids(self):

        existing_items = self.database.get(include=[])
        existing_ids   = set(existing_items["ids"])

        return existing_ids
            
#-----------------------------------------------------------------------------#

    def get_version_list(self, source):

        version_data = self.database.get(where={"source": source})["metadatas"]

        version_list = sorted(set(item['version'] for item in version_data), reverse=True)

        if not len(version_list):
            version_list = [0]

        return version_list

#-----------------------------------------------------------------------------#

    def database_to_dataframes(self):

        data = self.database.get()

        df = pd.DataFrame({
            'ids'           : data['ids'],
            'title'         : [meta['title'] for meta in data['metadatas']],
            'raw_text'      : [meta['raw_text'] for meta in data['metadatas']],
            'source'        : [meta['source'] for meta in data['metadatas']],
            'size'          : [humanize.naturalsize(meta['size'], binary=True) for meta in data['metadatas']],
            'chunk_size'    : [meta['chunk_size'] for meta in data['metadatas']],
            'chunk_overlap' : [meta['chunk_overlap'] for meta in data['metadatas']],
            'start_date'    : [meta['start_date'] for meta in data['metadatas']],
            'end_date'      : [meta['end_date'] for meta in data['metadatas']],
            'version'       : [meta['version'] for meta in data['metadatas']],
            'latest'        : [meta['latest'] for meta in data['metadatas']],
            'documents'     : data['documents']
        })

        return df

#-----------------------------------------------------------------------------#

    def add_chroma(self, pdf, start_date, end_date, current_version):

        PDF_name = pdf.stream.name.split('.')[0]

        print(PDF_name)

        markdown = self.load_markdown(PDF_name, current_version)

        PDF_info = self.markdown_to_section(PDF_name, markdown, current_version)

        PDF_info = self.create_propositions(PDF_name, PDF_info, current_version)

        #PDF_info = self.load_json(PDF_name, current_version)
        
        self.info_to_documents(PDF_info, pdf, start_date, end_date, current_version)

        print("Done!!")

#-----------------------------------------------------------------------------#

    def update_chroma(self, source_name, date, latest, current_version):

        old_documents = self.database.get(where={"source": source_name})

        new_documents = []
        new_ids       = []

        for ids, old_metadata, old_document in zip(old_documents["ids"], old_documents['metadatas'], old_documents['documents']):

            if old_metadata['version'] == current_version:

                updated_metedata = self.ToolController.generate_metedata(
                    old_metadata["title"],
                    old_metadata["raw_text"],
                    old_metadata["image_text"],
                    old_metadata['source'],
                    old_metadata['size'],
                    old_metadata['chunk_size'],
                    old_metadata['chunk_overlap'],
                    old_metadata['start_date'],
                    date,
                    old_metadata['version'],
                    latest
                    )

                new_documents.append(Document(page_content=old_document, metadata=updated_metedata))

                new_ids.append(ids)

        self.database.update_documents(ids=new_ids, documents=new_documents)

#-----------------------------------------------------------------------------#

    def add_database(self, files):

        start_date = self.time_now.strftime('%Y/%m/%d %H:%M:%S')
        end_date   = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

        for file in files:

            pdf = PyPDF2.PdfReader(file)

            current_version = self.get_version_list(pdf.stream.name)[0]

            if current_version > 0:
                self.update_chroma(pdf.stream.name, start_date, False, current_version)

            self.add_chroma(pdf, start_date, end_date, current_version)

#-----------------------------------------------------------------------------#

    def clear_database(self, delete_ids):

        if delete_ids:
            self.database.delete(ids=delete_ids)

#-----------------------------------------------------------------------------#

    def rollback_database(self, rollback_list):

        end_date = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

        for rollback_source, rollback_version in rollback_list:

            version_list = self.get_version_list(rollback_source)

            if rollback_version == version_list[0] and len(version_list) > 1:
                self.update_chroma(rollback_source, end_date, True, version_list[1])

#-----------------------------------------------------------------------------#

    def markdown_to_section(self, PDF_name, markdown, current_version):

        PDF_info = {
            "PDF_name" : PDF_name,
            "sections" :[]
        }

        section_id = 1

        table_list = [table[0] for table in re.findall(r'(\|.*\|\n(\|.*\|\n)+)', markdown)]

        for index, table in enumerate(table_list):

            section_info = {
                "ID"           : section_id,
                "type"         : "Table",
                "title"        : f"Table:{index+1}",
                "raw_text"     : re.sub(r'<br>', '', table),
                "propositions" : [],
                "image_text"   : "",
                "image"        : []
            }

            markdown = markdown.replace(table, '')

            PDF_info["sections"].append(section_info)
            section_id += 1

        markdown = re.sub(r"\\tag\{.*?\}", "", markdown)

        parsed_sections = self.parse_text(markdown)

        for section in parsed_sections:

            title    = section['title']
            raw_text = section['content']

            section_info = {
                "ID"           : section_id,
                "type"         : "Text",
                "title"        : title,
                "raw_text"     : raw_text,
                "propositions" : [f"PDF name:{PDF_name}, Title:{title}", f"檔案名稱:{PDF_name}, 段落標題:{title}"],
                "image_text"   : raw_text,
                "image"        : []
            }

            image_list = [match.group(1) for match in re.finditer(r'!\[\]\(([^)]+\.(?:jpeg|jpg|png|gif))\)', raw_text, re.IGNORECASE)]

            if len(image_list):

                for image in image_list:

                    image_md   = f"![]({image})"
                    image_name = image
                    image_path = f'storage/{self.database_name}/output_MD/{PDF_name}_v{current_version+1}/{image_name}'
                    
                    image_info = {
                        "name" : "",
                        "path" : ""
                    }

                    image_info["name"] = image_name
                    image_info["path"] = image_path

                    section_info["image"].append(image_info)

                    img_bytes = Path(image_path).read_bytes()
                    encoded   = base64.b64encode(img_bytes).decode()
                    img_html  = f'<img src="data:image/png;base64,{encoded}" alt="{image_name}" style="max-width: 100%;">'

                    section_info["raw_text"]   = section_info["raw_text"].replace(image_md, "")
                    section_info["image_text"] = section_info["image_text"].replace(image_md, img_html)

            else:
                section_info["image_text"] = ""

            PDF_info["sections"].append(section_info)
            section_id += 1

        self.save_json(PDF_name, PDF_info, current_version)

        return PDF_info

#-----------------------------------------------------------------------------#

    def create_propositions(self, PDF_name, PDF_info, current_version):

        for info in PDF_info["sections"]:

            response = self.ToolController.get_propositions_response(info["type"], info["title"], info["raw_text"])

            try:
                text_response_json = json.loads(response.message.content)

                for index, proposition in enumerate(text_response_json["propositions"], 1):
                    proposition = re.sub(r"\s+", "", proposition)
                    if len(proposition) and proposition not in self.remove_propositions_list:
                        info["propositions"].append(proposition)
                        print(proposition)

                print("Formatted output successful.")

            except:
                info["propositions"] = response.message.content

                print(response.message.content)

                print("Formatted output failed.")

        self.save_json(PDF_name, PDF_info, current_version)

        return PDF_info

#-----------------------------------------------------------------------------#

    def info_to_documents(self, PDF_info, pdf, start_date, end_date, current_version):

        for info in PDF_info["sections"]:

            metadata = self.ToolController.generate_metedata(
                info["title"],
                info["raw_text"],
                info["image_text"],
                pdf.stream.name, 
                pdf.stream.size,
                "",
                "",
                start_date,
                end_date,
                current_version + 1,
                True
            )

            documents = self.section_to_documents(info, metadata)

            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            if len(documents):
                self.database.add_documents(documents, ids=ids)

#-----------------------------------------------------------------------------#

    def section_to_documents(self, info, metadata):

        if isinstance(info["propositions"], list):

            info["propositions"] = [proposition for proposition in info["propositions"] if proposition.strip()]

            documents = []
            for proposition in info["propositions"]:
                document = Document(page_content=str(proposition), metadata=metadata)
                documents.append(document)

        else:

            metadata["chunk_size"]    = self.chunk_size
            metadata["chunk_overlap"] = self.chunk_overlap

            documents = self.text_splitter.create_documents([str(info["propositions"])], [metadata])

        return documents

#-----------------------------------------------------------------------------#

    def save_PDF(self, files):

        for file in files:

            save_path = f"storage/{self.database_name}/save_PDF/"
            temp_path = f"temp_PDF/"

            current_version = self.get_version_list(PyPDF2.PdfReader(file).stream.name)[0]+1

            save_pdf_name = file.name.split('.')[0] + '_v' + str(current_version) + '.pdf'

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf.write(file.getvalue())
                temp_pdf.seek(0)
                temp_pdf_name = temp_pdf.name

            shutil.move(temp_pdf_name, save_path+save_pdf_name)
            shutil.copy(save_path+save_pdf_name, temp_path)

#-----------------------------------------------------------------------------#

    def save_json(self, PDF_name, PDF_info, current_version):

        path = f"storage/{self.database_name}/output_json/"

        save_json_name = PDF_name + '_v' + str(current_version+1) + '.json'

        with open(path+save_json_name, 'w', encoding='utf-8') as file:
            file.write(json.dumps(PDF_info, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

    def load_json(self, json_name, current_version):

        path = f"storage/{self.database_name}/output_json/"

        load_json_name = json_name + '_v' + str(current_version+1) + '.json'

        with open(path+load_json_name, 'r', encoding='utf-8') as file:
            PDF_info = json.load(file)

        return PDF_info

#-----------------------------------------------------------------------------#

    def load_markdown(self, PDF_name, current_version):

        path = f"storage/{self.database_name}/output_MD/"

        markdown_folder = PDF_name + '_v' + str(current_version+1) + '/'

        markdown_name = PDF_name + '_v' + str(current_version+1) + '.md'
        
        with open(path+markdown_folder+markdown_name, 'r', encoding="utf-8") as file:
            markdown = file.read()
        
        return markdown

#-----------------------------------------------------------------------------#

    def parse_text(self, text):
        sections = []
        lines = text.split('\n')
        current_section = {"title": "", "content": ""}
        
        for line in lines:
            match = re.match(r'^(#+)\s*(.*)', line)
            if match:
                if current_section["title"]:
                    sections.append(current_section)
                    current_section = {"title": "", "content": ""}
                
                current_section["title"] = match.group(2)
            else:
                current_section["content"] += line + "\n"
        
        if current_section["title"]:
            sections.append(current_section)
        
        return sections
