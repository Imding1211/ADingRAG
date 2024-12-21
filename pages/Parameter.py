
from controller.setting import SettingController

import streamlit as st

#=============================================================================#

SettingController      = SettingController()
selected_prompt        = SettingController.setting['paramater']['prompt']
selected_query_num     = SettingController.setting['paramater']['query_num']
selected_database      = SettingController.setting['database']['selected']
selected_chunk_size    = SettingController.setting['text_splitter']['chunk_size']
selected_chunk_overlap = SettingController.setting['text_splitter']['chunk_overlap']
selected_base_url      = SettingController.setting['server']['base_url']

#=============================================================================#

def change_query_num():
	SettingController.change_query_num(st.session_state.query_num)
	
#=============================================================================#

st.set_page_config(layout="wide")

#=============================================================================#

st.header("參數")

#-----------------------------------------------------------------------------#

query_num_container = st.container(border=True)

query_num_container.slider("資料檢索數量",
	1, 10, selected_query_num, 
	on_change=change_query_num,
	key="query_num",
	)

#-----------------------------------------------------------------------------#

text_splitter_container = st.container(border=True)

text_splitter_container.text_input("文章切割長度", 
	selected_chunk_size,
	key="chunk_size",
	)

text_splitter_container.text_input("區塊重疊長度", 
	selected_chunk_overlap,
	key="chunk_overlap",
	)

text_splitter_warning = text_splitter_container.empty()

if text_splitter_container.button("確認", key=2):
	if int(st.session_state.chunk_size) <= int(st.session_state.chunk_overlap):
		text_splitter_warning.warning('文章重疊大小必須小於文章切割大小。', icon="⚠️")

	else:
		SettingController.change_text_splitter(st.session_state.chunk_size, st.session_state.chunk_overlap)
		st.toast('文章切割設定已更新。')

#-----------------------------------------------------------------------------#

prompt_container = st.container(border=True)

prompt_container.text_area("自訂提示詞", 
	selected_prompt,
	height=200,
	key="prompt",
	)

prompt_warning = prompt_container.empty()

if prompt_container.button("確認", key=3):
	
	if "{context}" not in st.session_state.prompt and "{question}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{context}與{question}。', icon="⚠️")

	elif "{context}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{context}。', icon="⚠️")

	elif "{question}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{question}。', icon="⚠️")

	else:
		SettingController.change_prompt(st.session_state.prompt)
		st.toast('提示詞已更新。')

#-----------------------------------------------------------------------------#

base_url_container = st.container(border=True)

base_url_container.text_input("URL", 
	selected_base_url,
	key="base_url",
	)

if base_url_container.button("確認", key=4):
	SettingController.change_base_url(st.session_state.base_url)
	st.toast('URL已更新。')
