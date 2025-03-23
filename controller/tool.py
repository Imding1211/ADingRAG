
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
from llama_index.llms.ollama import Ollama

from controller.setting import SettingController

import os

#=============================================================================#

class ToolController():

    def __init__(self):

        self.SettingController  = SettingController()
        self.base_url           = self.SettingController.setting['server']['base_url']
        self.propositions_model = self.SettingController.setting['text_splitter']['llm_model']

        self.propositions_llm = Ollama(
            model=self.propositions_model, 
            request_timeout= 600.0, 
            base_url=self.base_url, 
            json_mode=True
            )

#-----------------------------------------------------------------------------#

    def generate_metedata(self, title, raw_text, image_text, source, size, chunk_size, chunk_overlap, start_date, date, version, latest):
        
        metedata = {
            "title"         : title,
            "raw_text"      : raw_text,
            "image_text"    : image_text,
            "source"        : source,
            "size"          : size,
            "chunk_size"    : chunk_size,
            "chunk_overlap" : chunk_overlap,
            "start_date"    : start_date,
            "end_date"      : date,
            "version"       : version,
            "latest"        : latest
        }

        return metedata

#-----------------------------------------------------------------------------#

    def remove_temp_PDF(self, folder_path):
        
        if not os.path.exists(folder_path):
            print(f"資料夾 {folder_path} 不存在。")
            return
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                    os.remove(file_path)
                    print(f"已刪除檔案: {file_path}")
                    
            except Exception as e:
                print(f"無法刪除檔案 {file_path}，錯誤: {e}")

#-----------------------------------------------------------------------------#

    def get_propositions_response(self, type, title, raw_text):

        text_decompose_prompt = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="""
                    將「內容」分解為清晰且簡單的命題，確保這些命題在脫離上下文的情況下也能被理解。

                    1. 將複合句分割成簡單句，儘可能保留輸入中的原始措辭。

                    2. 如果命名實體附帶描述性資訊，將這些資訊拆分為獨立的命題。

                    3. 通過添加必要的修飾詞，使命題去脈絡化。例如，將代名詞（例如 "它"、"他"、"她"、"他們"、"這個"、"那個"）替換為它們所指代的完整實體名稱。

                    4. 以 JSON 格式輸出結果，格式如下：: {"propositions": ["句子1", "句子2", "句子3"]}"""),
            ChatMessage(
                role=MessageRole.USER,
                content="""
                    請使用繁體中文分解以下內容:

                    Title: 晨間運動的好處 

                    Content: 開始一天時進行運動，對身體與心理健康會產生深遠的影響。

                    晨間運動能提升精力、改善心情，並提高一天的專注力。

                    身體活動會刺激內啡肽的釋放，減輕壓力並帶來幸福感。

                    此外，早晨運動有助於建立規律的生活習慣，使保持持續性變得更容易。

                    還能通過調節身體的自然時鐘來改善睡眠品質。

                    無論是快走、瑜伽課，還是健身房運動，甚至只需要20到30分鐘，也能帶來顯著的效果。

                    養成晨間運動的習慣，將體驗到更有成效且更健康的生活方式。

                    這是一個小小的改變，卻能帶來顯著且持久的益處。"""),
            ChatMessage(
                role=MessageRole.ASSISTANT ,
                content="""
                    propositions=[
                        '晨間運動的好處。',
                        '開始一天時進行運動，能對你的身體與心理健康產生深遠的影響。',
                        '參與晨間運動可以提升你的精力、改善心情，並提高一天的專注力。',
                        '身體活動會刺激內啡肽的釋放，減輕壓力並促進幸福感。',
                        '此外，早晨運動有助於建立規律的生活習慣，使保持持續性變得更容易。',
                        '它還能通過調節身體的自然時鐘來改善睡眠品質。',
                        '無論是快走、瑜伽課還是健身房運動，甚至只需20到30分鐘，也能帶來顯著的效果。',
                        '養成晨間運動的習慣，將讓你體驗到更有成效且更健康的生活方式。',
                        '這是一個小小的改變，卻能帶來顯著且持久的益處。']"""),
            ChatMessage(
                role=MessageRole.USER,
                content="""
                    請使用繁體中文分解以下內容:Title:{title} Content:{content}"""),
            ]

        table_decompose_prompt = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="""
                    分析表格並基於表格內容撰寫摘要。

                    1. 提供清晰且簡潔的描述，描述每一行中的關鍵資訊，避免冗長或不必要的細節。

                    2. 摘要需突出主要數據點與重要特徵，針對數值型數據，強調極值（例如最大值或最小值）、趨勢或明顯的異常。

                    3. 若為分類型數據，則重點說明具代表性或高頻的類別。

                    4. 若某些列的內容相似度極高，可合併處理並概括為一條命題。

                    5. 可在摘要的末尾加入簡短的總結，概述整體表格的核心意義或結論，例如「此表格展示了...的主要趨勢」。

                    6. 以 JSON 格式輸出結果，格式如下：: {"propositions": ["句子1", "句子2", "句子3"]}""" ),
            ChatMessage(
                role=MessageRole.USER,
                content="""
                    請使用繁體中文分析以下表格並基於表格內容撰寫摘要:

                    Table:| CPU                          | Pentium 4 1.8 GHz         |
                          |------------------------------|---------------------------|
                          | OS                           | Redhat 7.3 (Linux 2.4.18) |
                          | Main-memory size             | 1 GB RDRAM                |
                          | Trace Cache                  | 12 K micro-ops            |
                          | ITLB                         | 128 entries               |
                          | L1 data cache size           | 16 KB                     |
                          | L1 data cacheline size       | 64 bytes                  |
                          | L2 cache size                | 256 KB                    |
                          | L2 cacheline size            | 128 bytes                 |
                          | Trace Cache miss latency     | > 27 cycles               |
                          | L1 data miss latency         | 18 cycles                 |
                          | L2 miss latency              | 276 cycles                |
                          | Branch misprediction latency | > 20 cycles               |
                          | Hardware prefetch            | Yes                       |
                          | C Compiler                   | GNU's gcc 3.2             |"""),
            ChatMessage(
                role=MessageRole.ASSISTANT ,
                content="""
                    propositions=[
                        '此表格提供了一個計算系統的規格，詳細列出 CPU、記憶體、快取及效能特性：',
                        'CPU：使用 Pentium 4 1.8 GHz 處理器。',
                        '操作系統：運行於 Redhat 7.3，採用 Linux 核心版本 2.4.18。',
                        '記憶體：配備 1 GB 的 RDRAM。',
                        '指令追蹤快取（Trace Cache）：容量為 12K 微操作（micro-ops）。',
                        '指令 TLB：包含 128 個條目。',
                        'L1 資料快取：大小為 16 KB，快取線大小為 64 字節。',
                        'L2 快取：大小為 256 KB，快取線大小為 128 字節。',
                        '指令追蹤快取未命中：延遲超過 27 個週期。',
                        'L1 資料快取未命中：延遲為 18 個週期。',
                        'L2 快取未命中：延遲為 276 個週期。',
                        '分支預測錯誤：懲罰超過 20 個週期。',
                        '硬體預取（Hardware Prefetch）：已啟用。',
                        '編譯器：使用 GNU 的 gcc 版本 3.2。']"""),
            ChatMessage(
                role=MessageRole.USER,
                content="""
                    請使用繁體中文分析以下表格並基於表格內容撰寫摘要:Table:{table}"""),
            ]

        text_decompose_template = ChatPromptTemplate(message_templates=text_decompose_prompt)

        table_decompose_template = ChatPromptTemplate(message_templates=table_decompose_prompt)

        if type == "Text":
            messages = text_decompose_template.format_messages(title=title, content=raw_text)

        elif type == "Table":
            messages = table_decompose_template.format_messages(table=raw_text)

        response = self.propositions_llm.chat(messages)

        return response
    