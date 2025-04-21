
from langchain_ollama import ChatOllama
from typing import Dict
from ollama import Client

from controller.setting import SettingController

import pandas as pd
import requests
import humanize
import re

#=============================================================================#

class ModelController():

    def __init__(self):

        self.SettingController = SettingController()
        self.llm_model         = self.SettingController.setting['paramater']['llm_model']
        self.base_url          = self.SettingController.setting['server']['base_url']
        self.llm               = ChatOllama(model=self.llm_model, base_url=self.base_url)
        self.client            = Client(host=self.base_url)

#-----------------------------------------------------------------------------#

    def generate_response(self, messages: list) -> dict:

        response = self.llm.invoke([(item['role'], item['response_content']) for item in messages])

        match = re.search(r"<think>(.*?)</think>\s*(.*)", response.content, re.DOTALL)

        if match:
            think_content    = match.group(1).strip()
            response_content = match.group(2).strip()

            return {"think_content": think_content, "response_content": response_content}

        else:
            return {"think_content": "", "response_content": response.content}

#-----------------------------------------------------------------------------#

    def ollama_to_dataframe(self):

        json_info = self.client.list()

        df_info = pd.DataFrame({
            'model'             : [info['model'] for info in json_info['models']],
            'date'              : [info['modified_at'].strftime("%Y-%m-%d %H:%M:%S") for info in json_info['models']],
            'size'              : [humanize.naturalsize(info['size'], binary=True) for info in json_info['models']],
            'format'            : [info['details']['format'] for info in json_info['models']],
            'family'            : [info['details']['family'] for info in json_info['models']],
            'parameter_size'    : [info['details']['parameter_size'] for info in json_info['models']],
            'quantization_level': [info['details']['quantization_level'] for info in json_info['models']]
            })

        return df_info

#-----------------------------------------------------------------------------#

    def get_running_models(self):
        
        url = self.base_url + "api/ps"
        
        try:
            response = requests.get(url, timeout=10)

            response.raise_for_status()

            models = response.json()

            return models

        except requests.exceptions.RequestException as e:

            print(f"API 請求錯誤: {e}")

            return None

#-----------------------------------------------------------------------------#

    def unload_running_model(self, model_name):
        
        url = self.base_url + "api/generate"
        
        payload = {"model": model_name, "keep_alive": 0}
        
        try:
            response = requests.post(url, json=payload, timeout=10)

            response.raise_for_status()

            return response.json()
        
        except requests.exceptions.RequestException as e:

            print(f"API 請求錯誤: {e}")

            return None

#-----------------------------------------------------------------------------#

    def unload_all_running_models(self):

        models = self.get_running_models()
        
        for model in models['models']:

            response = self.unload_running_model(model['name'])

            print(response)