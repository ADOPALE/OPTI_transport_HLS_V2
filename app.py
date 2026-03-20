import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Imports des modules de pages (UI)
from modules.Import import show_import
from modules.GeoMatrix import run_matrix_tool
from modules.dataViz import show_volumes, show_flux_control_charts
from modules.biologie_ui import (
    show_biologie_config, 
    show_simulation_page, 
    show_detail_tournees
)

# Configuration de la page
st.set_page_config(layout="wide", page_title="Logistique CHU Nantes & ADOPALE", page_icon="📍")

# Chemins et Assets
BASE_DIR = Path(__file__).resolve().parent
LOGO_ADOPALE = BASE_DIR / "assets" / "ADOPALE.jpg"
LOGO_CHU = BASE_DIR / "assets" / "CHU Nantes.png"

# Initialisation Session State
if "sim_lancee" not in st.session_state:
    st.session_state.sim_lancee = False

# --- BARRE LATÉRALE (NAVIGATION) ---
with st.sidebar:
    # Logos
    c1, c2 = st.columns(2)
    if LOGO_ADOPALE.exists(): c1.image(str(LOGO_ADOPALE))
    if LOGO_CHU.exists(): c2.image(str(LOGO_CHU))
    
    st.divider()

    # Menu Dynamique
    options = ["Accueil", "Calcul Matrices", "Importer Données", "Volumes Distribution", "Passages Biologie", "Optimisation"]
    icons = ["house", "geo-alt", "cloud-upload", "truck", "microscope", "play-circle"]

    if st.session_state.sim_lancee:
        options += ["Détail tournées", "Exporter"]
        icons += ["map", "file-earmark-pdf"]

    selected = option_menu(None, options, icons=icons, menu_icon="cast", default_index=0)

    if st.session_state.sim_lancee:
        st.divider()
        if st.button("🔄 Réinitialiser la simulation", use_container_width=True):
            st.session_state.sim_lancee = False
            st.rerun()

# --- ROUTAGE DES PAGES ---
if selected == "Accueil":
    st.title("📍 Optimisation des flux logistiques")
    st.info("Bienvenue. Utilisez le menu à gauche pour naviguer.")

elif selected == "Calcul Matrices":
    run_matrix_tool()

elif selected == "Importer Données":
    show_import()
    if "data" in st.session_state:
        show_flux_control_charts()

elif selected == "Volumes Distribution":
    show_volumes() if show_volumes else st.warning("Module non disponible")

elif selected == "Passages Biologie":
    show_biologie_config() # Appel de la nouvelle UI déportée

elif selected == "Optimisation":
    show_simulation_page() # Appel de la nouvelle UI déportée

elif selected == "Détail tournées":
    show_detail_tournees() # Appel de la nouvelle UI déportée

elif selected == "Exporter":
    st.title("📥 Exporter les résultats")
