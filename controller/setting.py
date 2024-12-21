
import datetime
import shutil
import json
import os

#=============================================================================#

class SettingController():

	def __init__(self):

		self.time_zone  = datetime.timezone(datetime.timedelta(hours=8))
		self.time_now   = datetime.datetime.now(tz=self.time_zone)
		self.start_date = self.time_now.strftime('%Y/%m/%d %H:%M:%S')

		self.default_setting = {
		    "paramater": {
		        "llm_model": "llama3.2-vision:latest",
		        "prompt": "{context}\n\n---\n\n根據以上資料用繁體中文回答問題: {question}\n",
		        "query_num": 2
		    },
		    "database": {
		        "selected": "default",
		        "default": {
		            "create_time": self.start_date,
		            "path": "storage/default/database",
		            "embedding_model": "all-minilm:latest",
		            "remarks": "Default database."
		        }
		    },
		    "text_splitter": {
		        "chunk_size": 150,
		        "chunk_overlap": 50
		    },
		    "server": {
		        "base_url": "http://localhost:11434/"
		    }
		}

		self.load_setting()

#-----------------------------------------------------------------------------#

	def load_setting(self):
		with open('setting.json', 'r', encoding='utf-8') as setting_file:
		    self.setting = json.load(setting_file)

#-----------------------------------------------------------------------------#

	def generate_setting(self, new_setting):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(new_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def generate_default_setting(self):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(self.default_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def change_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['paramater']['llm_model'] = model_name

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_embedding_model(self, database, model_name):

		if len(model_name) > 0:

			self.setting["database"][database]['embedding_model'] = model_name

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_prompt(self, prompt):

		self.setting['paramater']['prompt'] = prompt

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_query_num(self, query_num):

		self.setting['paramater']['query_num'] = query_num

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_database(self, database):

		self.setting['database']['selected'] = database

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_text_splitter(self, chunk_size, chunk_overlap):

		self.setting['text_splitter']['chunk_size'] = int(chunk_size)

		self.setting['text_splitter']['chunk_overlap'] = int(chunk_overlap)

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_base_url(self, base_url):

		self.setting['server']['base_url'] = base_url

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_remarks(self, database, remarks):

		if len(remarks) > 0:

			self.setting["database"][database]['remarks'] = remarks

			self.generate_setting(self.setting)
		
#-----------------------------------------------------------------------------#

	def add_database(self, database, model, remarks):

		if len(database) > 0:
			storage_path = f"storage/{database}/"

			new_database = {
			    "create_time": self.start_date,
			    "path": storage_path + "database",
			    "embedding_model": model,
			    "remarks": remarks
			}

			self.setting['database'][database] = new_database

			self.setting['database']['selected'] = database

			self.generate_setting(self.setting)
			
			for folder in ["database", "save_PDF", "output_json", "output_MD"]:

				folder_path = storage_path + folder

				if not os.path.exists(folder_path):
					os.makedirs(folder_path)
					print(f"{folder_path}已建立")
				else:
					print(f"{folder_path}已存在")

#-----------------------------------------------------------------------------#

	def remove_database(self, database):

		if database in self.setting["database"]:
			del self.setting["database"][database]

			self.setting['database']['selected'] = list(self.setting["database"].keys())[1]

			self.generate_setting(self.setting)

			storage_path = f"storage/{database}/"

			try:
			    shutil.rmtree(storage_path)
			    print(f"{database}資料庫已成功移除。")

			except FileNotFoundError:
			    print(f"{database}資料庫不存在。")

			except PermissionError:
			    print(f"沒有權限移除{database}資料庫。")

			except Exception as e:
			    print(f"移除{database}資料庫時發生錯誤: {e}")
