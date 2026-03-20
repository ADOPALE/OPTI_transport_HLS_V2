import streamlit as st
from modules.data_handler import load_all_data
from modules.ui_biologie import show_biologie_config_ui, show_run_simulation_ui
from modules.ui_viz import render_flux_charts

st.set_page_config(page_title="OptiTransport HLS", layout="wide")

# Sidebar - Import
with st.sidebar:
    up = st.file_uploader("Fichier Excel")
    if up:
        st.session_state["data"] = load_all_data(up)

# Menu Principal
tab1, tab2, tab3 = st.tabs(["Flux", "Config Biologie", "Résultats"])

with tab1:
    if "data" in st.session_state:
        render_flux_charts(st.session_state["data"]["m_flux"])

with tab2:
    show_biologie_config_ui()

with tab3:
    show_run_simulation_ui()
