
from controller.database import DatabaseController
from controller.setting import SettingController
from controller.model import ModelController
from controller.tool import ToolController
from controller.convert import PDF_to_MD

import streamlit as st
import subprocess
import sys
import os

#=============================================================================#

DatabaseController       = DatabaseController()
embedding_model_disabled = True if len(DatabaseController.calculate_existing_ids()) != 0 else False

SettingController    = SettingController()
list_database        = list(SettingController.setting['database'].keys())[1:]
selected_database    = SettingController.setting['database']['selected']
selected_embedding   = SettingController.setting['database'][selected_database]['embedding_model']
create_time_database = SettingController.setting['database'][selected_database]['create_time']
remarks_database     = SettingController.setting['database'][selected_database]['remarks']
index_database       = list_database.index(selected_database)

ModelController      = ModelController()
ollama_info          = ModelController.ollama_to_dataframe()
list_embedding_model = ollama_info[ollama_info["family"] == "bert"]["name"].tolist()

ToolController = ToolController()

#=============================================================================#

def change_database():
    SettingController.change_database(st.session_state.database)

#-----------------------------------------------------------------------------#

def change_embedding_model():
    SettingController.change_embedding_model(selected_database, st.session_state.embedding_model)

#-----------------------------------------------------------------------------#

@st.dialog("編輯資料庫", width="large")
def edit_database():

    remarks = st.text_area("資料庫備注", remarks_database)

    if selected_embedding in list_embedding_model:
        index_embedding = list_embedding_model.index(selected_embedding)
    else:
        embedding_warning.error(f'{selected_embedding}嵌入模型不存在，請重新選擇。', icon="🚨")
        index_embedding = None

    st.selectbox("請選擇嵌入模型:", 
        list_embedding_model, 
        on_change=change_embedding_model, 
        key='embedding_model', 
        index=index_embedding,
        disabled=embedding_model_disabled,
        placeholder='嵌入模型不存在，請重新選擇。'
        )

    embedding_warning = st.empty()

    if embedding_model_disabled:
        embedding_warning.warning('資料庫有資料時無法更換嵌入模型。', icon="⚠️")

    st.dataframe(
        ollama_info[ollama_info["family"] == "bert"],
        column_config=info_config,
        use_container_width=True,
        hide_index=True
        )

    if st.button("確認", key=6):
        SettingController.change_embedding_model(selected_database, st.session_state.embedding_model)
        SettingController.change_remarks(selected_database, remarks)
        st.rerun()

#-----------------------------------------------------------------------------#

@st.dialog("新增資料庫")
def add_database():
    database = st.text_input("輸入資料庫名稱:")
    model    = st.selectbox("選擇嵌入模型:", list_embedding_model, index=None, placeholder="請選擇嵌入模型")
    remarks  = st.text_area("資料庫備注")

    if st.button("確認", key=7):
        SettingController.add_database(database, model, remarks)
        st.rerun()

#-----------------------------------------------------------------------------#

@st.dialog("移除資料庫")
def remove_database():
    database = st.selectbox("選擇資料庫:", list_database, index=None, placeholder="請選擇資料庫")

    if st.button("確認", key=8):
        SettingController.remove_database(database)
        st.rerun()

#=============================================================================#

working_dir = os.getcwd()

st.set_page_config(layout="wide")

event_config = {
    "source": st.column_config.TextColumn(
        "資料", 
        help="資料名稱", 
        max_chars=100, 
        width="small"
    ),
    "size": st.column_config.TextColumn(
        "大小", 
        help="資料大小", 
        max_chars=100, 
        width="small"
    ),
    "chunk_size": st.column_config.TextColumn(
        "切割長度", 
        help="文章切割長度", 
        max_chars=100, 
        width="small"
    ),
    "chunk_overlap": st.column_config.TextColumn(
        "重疊長度", 
        help="區塊重疊長度", 
        max_chars=100, 
        width="small"
    ),
    "start_date": st.column_config.TextColumn(
        "開始時間", 
        help="資料開始時間", 
        max_chars=100, 
        width="small"
    ),
    "end_date": st.column_config.TextColumn(
        "結束時間", 
        help="資料結束時間", 
        max_chars=100, 
        width="small"
    ),
    "version": st.column_config.TextColumn(
        "版本", 
        help="資料版本", 
        max_chars=100, 
        width="small"
    ),
    "latest": st.column_config.TextColumn(
        "最新資料", 
        help="資料內容是否為最新", 
        max_chars=100, 
        width="small"
    ),
}

selected_config = {
    "source": st.column_config.TextColumn(
        "資料", 
        help="資料名稱", 
        max_chars=100, 
        width="small"
    ),
    "documents": st.column_config.TextColumn(
        "內容", 
        help="資料內容", 
        max_chars=100, 
        width="small"
    ),
    "start_date": st.column_config.TextColumn(
        "開始時間", 
        help="資料開始時間", 
        max_chars=100, 
        width="small"
    ),
    "end_date": st.column_config.TextColumn(
        "結束時間", 
        help="資料結束時間", 
        max_chars=100, 
        width="small"
    ),
    "version": st.column_config.TextColumn(
        "版本", 
        help="資料版本", 
        max_chars=100, 
        width="small"
    ),
    "latest": st.column_config.TextColumn(
        "是否為最新資料", 
        help="資料內容是否為最新", 
        max_chars=100, 
        width="small"
    ),
}

info_config = {
    "name": st.column_config.TextColumn(
        "建立名稱", 
        help="建立模型時的名稱", 
        max_chars=100, 
        width="small"
    ),
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

st.header("資料庫")

#-----------------------------------------------------------------------------#

database_warning = st.empty()

st.selectbox("請選擇要使用的資料庫：", 
    list_database, 
    on_change=change_database, 
    key='database', 
    index=index_database,
    placeholder='資料庫不存在，請重新選擇。'
    )

db_col1, db_col2 = st.columns([9,1])

db_col1.write(f"建立時間：{create_time_database}")
db_col1.write(f"嵌入模型：{selected_embedding}")
db_col1.write(f"資料庫備註：{remarks_database}")

if db_col2.button("編輯", key=1):
    edit_database()

if db_col2.button("新增", key=2):
    add_database()

if db_col2.button("刪除", key=3):
    remove_database()

#-----------------------------------------------------------------------------#

st.divider()

#-----------------------------------------------------------------------------#

st.header("資料上傳")

database_status = st.empty()

files = st.file_uploader(
    "請選擇要上傳的PDF:", 
    type="pdf", 
    accept_multiple_files=True, 
    label_visibility="visible",
    )

#-----------------------------------------------------------------------------#

PDF_col1, PDF_col2 = st.columns([9,1])

#-----------------------------------------------------------------------------#

df = DatabaseController.database_to_dataframes()

df_event = df.loc[df.groupby(['source', 'start_date'])['size'].idxmax(), ['source', 'size', 'chunk_size', 'chunk_overlap', 'start_date', 'end_date', 'version', 'latest']]

df_event = df_event.sort_values(by='start_date', ascending=False)

event = PDF_col1.dataframe(
    df_event,
    column_config=event_config,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
    )

select_id = event.selection.rows

df_selected = df_event.iloc[select_id][['source', 'start_date']]

df_result = df.merge(df_selected, on=['source', 'start_date'])

#-----------------------------------------------------------------------------#

if PDF_col2.button("新增", key=4):

    with database_status.status('資料處理中...', expanded=True) as update_status:

        #DatabaseController.save_PDF(files)

        ModelController.unload_all_running_models()

        #subprocess.run([f"{sys.executable}", "convert_controller.py", selected_database])

        #ToolController.remove_temp_PDF("temp_PDF")

        #DatabaseController.add_database(files)

        update_status.update(label="資料處理完成!", state="complete", expanded=False)

    st.rerun()
        
if PDF_col2.button('刪除', key=5):

    with database_status.status('資料刪除中...', expanded=True) as remove_status:

        delete_source = df_result[['source', 'version']].values.tolist()
        delete_source = list(map(list, set(map(tuple, delete_source))))
        DatabaseController.rollback_database(delete_source)
          
        delete_ids = df_result['ids'].values.tolist()
        DatabaseController.clear_database(delete_ids)

        remove_status.update(label="資料刪除完成!", state="complete", expanded=False)

    st.rerun()

#-----------------------------------------------------------------------------#

st.divider()

#-----------------------------------------------------------------------------#

st.header("資料預覽")

st.dataframe(
    df_result[['source', 'documents', 'start_date', 'end_date', 'version', 'latest']],
    column_config=selected_config,
    use_container_width=True, 
    hide_index=True
    )
