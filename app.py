import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# --- 1. IMPORTS ---
from modules.Import import show_import
from modules.GeoMatrix import run_matrix_tool
from modules.dataViz import show_volumes, show_flux_control_charts
from modules.biologie_ui import (
    show_biologie_config, 
    show_simulation_page, 
    show_detail_tournees
)

# --- 2. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Logistique CHU Nantes & ADOPALE", page_icon="📍")

BASE_DIR = Path(__file__).resolve().parent
LOGO_ADOPALE = BASE_DIR / "assets" / "ADOPALE.jpg"
LOGO_CHU = BASE_DIR / "assets" / "CHU Nantes.png"

# --- 3. INITIALISATION DU SESSION STATE ---
# 'biologie_verrouille' servira à figer l'onglet Passages Biologie après enregistrement
if "biologie_verrouille" not in st.session_state:
    st.session_state.biologie_verrouille = False

# --- 4. BARRE LATÉRALE (FIXE) ---
with st.sidebar:
    c1, c2 = st.columns(2)
    if LOGO_ADOPALE.exists(): c1.image(str(LOGO_ADOPALE))
    if LOGO_CHU.exists(): c2.image(str(LOGO_CHU))
    
    st.divider()

    # Le menu contient maintenant TOUTES les options dès le lancement
    options = [
        "Accueil", "Calcul Matrices", "Importer Données", 
        "Volumes Distribution", "Passages Biologie", 
        "Optimisation", "Détail tournées", "Exporter"
    ]
    icons = [
        "house", "geo-alt", "cloud-upload", 
        "truck", "microscope", "play-circle", 
        "map", "file-earmark-pdf"
    ]

    selected = option_menu(None, options, icons=icons, menu_icon="cast", default_index=0)

    st.divider()
    # Le bouton de réinitialisation est désormais toujours présent
    if st.button("🔄 Réinitialiser tout", use_container_width=True):
        # On remet à zéro les verrous et les données
        st.session_state.biologie_verrouille = False
        # On peut aussi vider d'autres variables ici si besoin
        st.rerun()

# --- 5. ROUTAGE ---

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
    # On passe le verrou en paramètre à la fonction (si elle est conçue pour l'accepter)
    # Sinon, gère le verrouillage directement à l'intérieur de 'show_biologie_config'
    st.header("🔬 Configuration Biologie")
    
    if st.session_state.biologie_verrouille:
        st.success("✅ Paramétrage enregistré et verrouillé.")
        # Optionnel : bouton pour déverrouiller manuellement si besoin
        if st.button("Modifier les paramètres"):
            st.session_state.biologie_verrouille = False
            st.rerun()
    
    # Appel de ton module
    show_biologie_config()

elif selected == "Optimisation":
    show_simulation_page()

elif selected == "Détail tournées":
    show_detail_tournees()

elif selected == "Exporter":
    st.title("📥 Exporter les résultats")
