
from controller.setting import SettingController

import streamlit as st

version = 2.2

#=============================================================================#

SettingController = SettingController()

#=============================================================================#

st.set_page_config(layout="wide")

#=============================================================================#

st.header("設定")

#-----------------------------------------------------------------------------#

if st.button("還原初始設定"):
	SettingController.generate_default_setting()
	st.toast('已還原初始設定。')

st.caption(f"版本:{version}")