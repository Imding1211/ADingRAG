
from controller.setting import SettingController
from controller.model import ModelController

import streamlit as st

#=============================================================================#

SettingController  = SettingController()
selected_llm       = SettingController.setting['paramater']['llm_model']

ModelController      = ModelController()
ollama_info          = ModelController.ollama_to_dataframe()
list_llm_model       = ollama_info[ollama_info["family"] != "bert"]["model"].tolist()
list_embedding_model = ollama_info[ollama_info["family"] == "bert"]["model"].tolist()

#=============================================================================#

def change_llm_model():
    SettingController.change_llm_model("paramater", st.session_state.llm_model)

#=============================================================================#

st.set_page_config(layout="wide")

info_config = {
    "model": st.column_config.TextColumn(
        "模型名稱", 
        help="模型名稱", 
        max_chars=100, 
        width="small"
    ),
    "date": st.column_config.TextColumn(
        "建立日期", 
        help="模型建立日期", 
        max_chars=100, 
        width="small"
    ),
    "size": st.column_config.TextColumn(
        "模型大小", 
        help="模型大小", 
        max_chars=100, 
        width="small"
    ),
    "format": st.column_config.TextColumn(
        "模型格式", 
        help="模型格式", 
        max_chars=100, 
        width="small"
    ),
    "family": st.column_config.TextColumn(
        "模型家族", 
        help="模型家族", 
        max_chars=100, 
        width="small"
    ),
    "parameter_size": st.column_config.TextColumn(
        "模型參數量", 
        help="模型參數量", 
        max_chars=100, 
        width="small"
    ),
    "quantization_level": st.column_config.TextColumn(
        "量化等級", 
        help="量化等級", 
        max_chars=100, 
        width="small"
    ),
}

#=============================================================================#

st.header("語言模型")

#-----------------------------------------------------------------------------#

llm_warning = st.empty()

#-----------------------------------------------------------------------------#

if selected_llm in list_llm_model:
    index_llm = list_llm_model.index(selected_llm)
    
else:
    llm_warning.error(f'{selected_llm}語言模型不存在，請重新選擇。', icon="🚨")
    index_llm = None

st.selectbox("請選擇語言模型:", 
    list_llm_model, 
    on_change=change_llm_model, 
    key='llm_model', 
    index=index_llm,
    placeholder='語言模型不存在，請重新選擇。'
    )

st.dataframe(
    ollama_info[ollama_info["family"] != "bert"],
    column_config=info_config,
    use_container_width=True,
    hide_index=True
    )

