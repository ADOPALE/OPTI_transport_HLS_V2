import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Import des nouveaux modules structurés
from modules.data_handler import load_all_data
from modules.core_geo import run_matrix_tool # Si vous gardez l'outil de calcul matriciel
from modules.ui_biologie import show_biologie_config_ui, show_run_simulation_ui
from modules.ui_viz import render_flux_charts, render_timeline_plotly, render_route_map

# Configuration de la page
st.set_page_config(
    layout="wide", 
    page_title="CHU Nantes x ADOPALE - Optimisation Transport",
    page_icon="📍"
)

# --- INITIALISATION DU SESSION STATE ---
if "data" not in st.session_state:
    st.session_state["data"] = None
if "resultat_flotte" not in st.session_state:
    st.session_state["resultat_flotte"] = None

# --- SIDEBAR : NAVIGATION ET IMPORT ---
with st.sidebar:
    st.image("assets/ADOPALE.jpg", width=200) # Assurez-vous que le chemin est correct
    st.title("Menu Principal")
    
    selected = option_menu(
        menu_title=None,
        options=["Accueil", "Importer Données", "Volumes Flux", "Configuration Biologie", "Résultats & Cartes", "Calcul Matrices"],
        icons=["house", "cloud-upload", "bar-chart", "thermometer-half", "map", "geo-alt"],
        menu_icon="cast",
        default_index=0,
    )
    
    st.divider()
    st.subheader("📁 Chargement des données")
    uploaded_file = st.file_uploader("Fichier Excel (Template)", type=["xlsx"])
    
    if uploaded_file:
        if st.button("Actualiser les données", use_container_width=True):
            st.session_state["data"] = load_all_data(uploaded_file)
            st.success("Données chargées avec succès !")

# --- ROUTAGE DES PAGES ---

if selected == "Accueil":
    st.title("📍 Optimisation des flux logistiques")
    st.markdown("---")
    st.markdown("""
    ### Bienvenue sur l'outil de simulation ADOPALE x CHU de Nantes
    Cet outil permet de modéliser les tournées de transport entre les différents sites du CHU.
    
    **Étapes recommandées :**
    1. **Importer** votre fichier de configuration dans l'onglet dédié.
    2. **Vérifier** les volumes de flux (Volumes Distribution).
    3. **Configurer** les fréquences de passage pour la Biologie.
    4. **Lancer** l'optimisation pour obtenir le nombre de véhicules et de chauffeurs nécessaires.
    """)
    
    if st.session_state["data"] is None:
        st.info("💡 Commencez par importer un fichier Excel dans la barre latérale.")

elif selected == "Importer Données":
    st.header("📥 Gestion des données")
    if st.session_state["data"]:
        st.success("Un fichier est actuellement chargé.")
        # Petit aperçu des onglets chargés
        for key in st.session_state["data"].keys():
            with st.expander(f"Aperçu : {key}"):
                st.dataframe(st.session_state["data"][key].head(10))
    else:
        st.warning("Aucune donnée chargée. Utilisez le menu à gauche.")

elif selected == "Volumes Flux":
    if st.session_state["data"]:
        render_flux_charts(st.session_state["data"]["m_flux"])
    else:
        st.error("Veuillez importer des données pour voir les graphiques.")

elif selected == "Configuration Biologie":
    if st.session_state["data"]:
        show_biologie_config_ui()
        show_run_simulation_ui()
    else:
        st.error("Données manquantes pour la configuration.")

elif selected == "Résultats & Cartes":
    if st.session_state["resultat_flotte"]:
        st.header("🗺️ Analyse des tournées optimisées")
        
        # 1. Frise Chronologique Globale
        render_timeline_plotly(st.session_state["resultat_flotte"])
        
        st.divider()
        
        # 2. Détail par véhicule et carte
        col_list, col_map = st.columns([1, 2])
        
        flotte = st.session_state["resultat_flotte"]
        with col_list:
            v_sel = st.selectbox("Sélectionner un véhicule", list(flotte.keys()))
            p_idx = st.selectbox("Sélectionner la vacation (Chauffeur)", range(len(flotte[v_sel])), 
                                 format_func=lambda x: f"Chauffeur n°{x+1}")
            
            vacation = flotte[v_sel][p_idx]
            for i, tournee in enumerate(vacation):
                with st.expander(f"Tournée {i+1}", expanded=(i==0)):
                    for stop in tournee:
                        st.write(f"⏱️ **{int(stop['heure']//60):02d}:{int(stop['heure']%60):02d}** - {stop['site']}")
        
        with col_map:
            # On récupère les coordonnées (depuis la matrice de distance par exemple ou un fichier de sites)
            # Ici on suppose que vous avez un dictionnaire 'coords' stocké quelque part
            if "coords" in st.session_state:
                # Fusionner toutes les tournées de la vacation pour la carte
                vacation_complete = [stop for tournee in vacation for stop in tournee]
                render_route_map(vacation_complete, st.session_state["coords"])
            else:
                st.info("Les coordonnées GPS ne sont pas chargées. La carte ne peut pas s'afficher.")
    else:
        st.warning("Aucun résultat disponible. Lancez l'optimisation dans 'Configuration Biologie'.")

elif selected == "Calcul Matrices":
    # On garde votre outil de calcul de distances OSRM/Geopy si nécessaire
    run_matrix_tool()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Développé pour le CHU de Nantes v2.0")
