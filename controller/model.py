
from langchain_ollama import OllamaLLM
from typing import Dict, Generator
from ollama import Client

from controller.setting import SettingController

import pandas as pd
import humanize

#=============================================================================#

class ModelController():

    def __init__(self):

        self.SettingController = SettingController()
        self.llm_model         = self.SettingController.setting['paramater']['llm_model']
        self.base_url          = self.SettingController.setting['server']['base_url']
        self.llm               = OllamaLLM(model=self.llm_model, base_url=self.base_url)
        self.client            = Client(host=self.base_url)

#-----------------------------------------------------------------------------#

    def generate_response(self, messages: Dict) -> Generator:
        
        for chunk in self.llm.stream(messages):
            yield chunk

#-----------------------------------------------------------------------------#

    def ollama_to_dataframe(self):

        json_info = self.client.list()

        df_info = pd.DataFrame({
            'name'              : [info['name'] for info in json_info['models']],
            'model'             : [info['model'] for info in json_info['models']],
            'date'              : [info['modified_at'].split("T")[0]+" "+info['modified_at'].split("T")[1].split(".")[0] for info in json_info['models']],
            'size'              : [humanize.naturalsize(info['size'], binary=True) for info in json_info['models']],
            'format'            : [info['details']['format'] for info in json_info['models']],
            'family'            : [info['details']['family'] for info in json_info['models']],
            'parameter_size'    : [info['details']['parameter_size'] for info in json_info['models']],
            'quantization_level': [info['details']['quantization_level'] for info in json_info['models']]
            })

        return df_info