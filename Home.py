
from controller.database import DatabaseController
from controller.setting import SettingController
from controller.query import QueryController
from controller.model import ModelController

import streamlit as st
import time
import uuid

import torch
torch.classes.__path__ = []

#=============================================================================#

DatabaseController = DatabaseController()

SettingController  = SettingController()
selected_query_num = SettingController.setting['paramater']['query_num']
database_name      = SettingController.setting['database']['selected']

QueryController = QueryController()

ModelController = ModelController()

#=============================================================================#

def load_PDF(PDF_info):

    database = PDF_info.split(":")[0]
    PDF_name = PDF_info.split(":")[1]

    with open(f"storage/{database}/save_PDF/{PDF_name}", "rb") as PDF_file:
        PDF = PDF_file.read()

    return PDF

#-----------------------------------------------------------------------------#

def text_to_stream(text):

    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

#=============================================================================#

st.set_page_config(layout="wide")

if "messages" not in st.session_state or "memory" not in st.session_state:
    st.session_state.messages = [{"role": "system", "think_content": "", "response_content": "使用繁體中文回答問題", "source": [], "time": 0}]
    st.session_state.memory   = [{"role": "system", "think_content": "", "response_content": "使用繁體中文回答問題", "source": [], "time": 0}]

    if len(DatabaseController.calculate_existing_ids()) == 0:
        info = "👈 Hi~ 資料庫是空的，請先到Database頁面點選上傳資料。"
    else:
        info = "✋ Hi~ 請問想詢問什麼問題呢？"
    
    st.session_state.messages.append({"role": "assistant", "think_content": "", "response_content": info, "source": [], "time": 0})
    st.session_state.memory.append({"role": "assistant", "think_content": "", "response_content": info, "source": [], "time": 0})

if "preview" not in st.session_state:
    st.session_state.preview = {}

#=============================================================================#

st.header("資料查詢")

#-----------------------------------------------------------------------------#

col1, col2 = st.columns(2)

chat_container = col1.container(border=False, height=500)
text_container = col2.container(border=False, height=500)

#-----------------------------------------------------------------------------#

for message in st.session_state.messages[1:]:

    if message["role"] == "user":
        with chat_container.chat_message("user"):
            st.markdown(message["response_content"])

    else:
        with chat_container.chat_message("assistant"):

            if len(message["think_content"]):
                with st.expander("思考過程"):
                    st.write(message['think_content'])

            st.markdown(message["response_content"])

            if message["time"] > 0:
                st.caption(f"回應時間:{message['time']}")

            if len(message["source"]):
                st.caption("參考資料來源: " + ", ".join([source_name.split(":")[1] for source_name in message["source"]]))

                st.divider()

                st.caption("參考資料下載:")
                download_buttons = []
                for source in message["source"]:
                    source_name = source.split(":")[1]
                    download_buttons.append(st.download_button(key=uuid.uuid4(), label=source_name, data=load_PDF(source), file_name=source_name, mime='application/octet-stream'))

#-----------------------------------------------------------------------------#

if question := st.chat_input("輸入問題:"):

    with chat_container.chat_message("user"):
        st.markdown(question)

#-----------------------------------------------------------------------------#

    results, sources = QueryController.generate_results(question)

    sources = [f"{database_name}:{source}" for source in sources]

    prompt, preview_text = QueryController.generate_prompt(question, results)

    st.session_state.messages.append({"role": "user", "think_content": "", "response_content": question, "source": [], "time": 0})
    st.session_state.memory.append({"role": "user", "think_content": "", "response_content": prompt, "source": [], "time": 0})
    st.session_state.preview = preview_text



#-----------------------------------------------------------------------------#

    with chat_container.chat_message("assistant"):

        start_time = time.time()

        with st.spinner("思考中..."):
            response = ModelController.generate_response(st.session_state.memory)

        end_time = time.time()
    
        if len(response['think_content']):
            with st.expander("思考過程"):
                st.write(response['think_content'])

        st.write_stream(text_to_stream(response['response_content']))

        st.caption(f"回應時間:{round(end_time - start_time, 2)}")

        if len(sources):
            st.caption("參考資料來源: " + ", ".join([source_name.split(":")[1] for source_name in sources]))

            st.divider()

            st.caption("參考資料下載:")
            download_buttons = []
            for source in sources:
                source_name = source.split(":")[1]
                download_buttons.append(st.download_button(key=uuid.uuid4(), label=source_name, data=load_PDF(source), file_name=source_name, mime='application/octet-stream'))

    st.session_state.memory[-1]["response_content"] = question

    st.session_state.messages.append({"role": "assistant", "think_content": response['think_content'], "response_content": response['response_content'], "source": sources, "time": round(end_time - start_time, 2)})
    st.session_state.memory.append({"role": "assistant", "think_content": response['think_content'], "response_content": response['response_content'], "source": sources, "time": round(end_time - start_time, 2)})

#-----------------------------------------------------------------------------#

if len(st.session_state.preview):
    source_title = text_container.selectbox("參考資料預覽:", list(st.session_state.preview.keys()), index=0)
    text_container.markdown(st.session_state.preview[source_title], unsafe_allow_html=True)

