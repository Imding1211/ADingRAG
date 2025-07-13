
import streamlit as st

#=============================================================================#

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

#-----------------------------------------------------------------------------#

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

#-----------------------------------------------------------------------------#

embedding_info_config = {
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

#-----------------------------------------------------------------------------#

LLM_info_config = {
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
