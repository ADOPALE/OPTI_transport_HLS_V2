import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# --- 1. IMPORTS DES MODULES (LOGIQUE MÉTIER) ---
from modules.Import import show_import
from modules.GeoMatrix import run_matrix_tool
from modules.dataViz import show_volumes, show_flux_control_charts
from modules.biologie_ui import (
    show_biologie_config, 
    show_simulation_page, 
    show_detail_tournees
)

# --- 2. CONFIGURATION DE L'APPLICATION ---
st.set_page_config(
    layout="wide", 
    page_title="Logistique CHU Nantes & ADOPALE", 
    page_icon="📍"
)

# Gestion des chemins pour les images (robuste pour Windows/Linux)
BASE_DIR = Path(__file__).resolve().parent
LOGO_ADOPALE = BASE_DIR / "assets" / "ADOPALE.jpg"
LOGO_CHU = BASE_DIR / "assets" / "CHU Nantes.png"

# --- 3. INITIALISATION DU SESSION STATE ---
# 'biologie_verrouille' : permettra de figer les champs dans l'onglet Biologie
if "biologie_verrouille" not in st.session_state:
    st.session_state.biologie_verrouille = False

# --- 4. BARRE LATÉRALE ET NAVIGATION ---
with st.sidebar:
    # Affichage des logos côte à côte
    c1, c2 = st.columns(2)
    if LOGO_ADOPALE.exists(): c1.image(str(LOGO_ADOPALE))
    if LOGO_CHU.exists(): c2.image(str(LOGO_CHU))
    
    st.divider()

    # Menu statique : toutes les options sont affichées dès le départ
    options = [
        "Accueil", 
        "Calcul Matrices distance et durées", 
        "Importer Données", 
        "Passages Biologie", 
        "Optimisation", 
        "Détail tournées", 
        "Exporter"
    ]
    
    icons = [
        "house", "geo-alt", "cloud-upload", 
        "microscope", "play-circle", 
        "map", "file-earmark-pdf"
    ]

    # Composant de navigation horizontal/vertical
    selected = option_menu(
        menu_title=None, 
        options=options, 
        icons=icons, 
        menu_icon="cast", 
        default_index=0
    )

    st.divider()
    
    # Bouton de réinitialisation globale toujours accessible
    if st.button("🔄 Réinitialiser la session", use_container_width=True):
        # On remet à zéro le verrou et on pourrait aussi vider st.session_state.data ici
        st.session_state.biologie_verrouille = False
        st.rerun()

# --- 5. ROUTAGE (AFFICHAGE DES PAGES) ---

# PAGE ACCUEIL : détailler l'ensemble des consignes et objectifs de l'application. 
if selected == "Accueil":
    st.title("📍 Optimisation des flux logistiques")
    st.info("Sélectionnez une étape dans le menu de gauche pour commencer.")

# PAGE qui permet de recalculer les distances et les durées entre les adresses.
elif selected == "Calcul Matrices distance et durées":
    # Outil de calcul des distances GPS / temps de trajet
    run_matrix_tool()

elif selected == "Importer Données":
    show_import()
    # Si des données ont été chargées, on affiche les graphiques de visualisation
    if "data" in st.session_state:
        show_flux_control_charts()

elif selected == "Volumes Distribution":
    # Sécurité au cas où l'import de la fonction échouerait
    show_volumes() if show_volumes else st.warning("Module de visualisation non chargé.")

elif selected == "Passages Biologie":
    st.header("🔬 Configuration des passages Biologie")
    
    # Message d'information si le paramétrage est figé
    if st.session_state.biologie_verrouille:
        st.success("🔒 Le paramétrage est actuellement enregistré et verrouillé.")
        if st.button("🔓 Déverrouiller pour modifier"):
            st.session_state.biologie_verrouille = False
            st.rerun()
    
    # On appelle l'UI. Note : pour que cela fonctionne, 
    # show_biologie_config() doit vérifier st.session_state.biologie_verrouille
    show_biologie_config()

elif selected == "Optimisation":
    show_simulation_page()

elif selected == "Détail tournées":
    show_detail_tournees()

elif selected == "Exporter":
    st.title("📥 Exportation des résultats")
    st.write("Génération des rapports PDF et Excel en cours...")
