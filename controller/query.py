
from langchain_core.prompts import ChatPromptTemplate

from controller.database import DatabaseController
from controller.setting import SettingController

#=============================================================================#

class QueryController():

    def __init__(self):

        self.DatabaseController = DatabaseController()
        self.database           = self.DatabaseController.database

        self.SettingController = SettingController()
        self.query_num         = self.SettingController.setting['paramater']['query_num']
        self.prompt_templt     = self.SettingController.setting['paramater']['prompt']

#-----------------------------------------------------------------------------#

    def generate_results(self, query_text):
        
        retriever     = self.database.as_retriever(search_kwargs={"k": self.query_num})
        query_results = retriever.invoke(query_text, filter={"latest": True})

        sources = []
        for doc in query_results:

            source_name = doc.metadata['source'].split('.')[0] + '_v' + str(doc.metadata['version']) + '.' + doc.metadata['source'].split('.')[-1]

            sources.append(source_name)

        query_sources = list(set(sources))

        return query_results, query_sources

#-----------------------------------------------------------------------------#

    def generate_prompt(self, query_text, query_results):
        
        #context_list = [doc.page_content for doc in query_results] + [doc.metadata['raw_text'] for doc in query_results]
        context_list = [doc.metadata['raw_text'] for doc in query_results]
        context_text = "\n\n---\n\n".join(list(set(context_list)))

        prompt_template = ChatPromptTemplate.from_template(self.prompt_templt)
        prompt          = prompt_template.format(context=context_text, question=query_text)

        print(prompt)

        preview_text = {}
        for doc in query_results:
            if len(doc.metadata['image_text']):
                preview_text[doc.metadata['title']] = doc.metadata['image_text']
                
            else:
                preview_text[doc.metadata['title']] = doc.metadata['raw_text']

        return prompt, preview_text
