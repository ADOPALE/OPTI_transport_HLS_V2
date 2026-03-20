import streamlit as st
import pandas as pd
from modules.core_engine import run_optimization

def show_biologie_config_ui():
    """Interface de paramétrage des sites et contraintes RH."""
    st.header("⚙️ Configuration des collectes Biologie")
    
    if "data" not in st.session_state or "m_flux" not in st.session_state["data"]:
        st.warning("Veuillez d'abord importer les données Excel.")
        return

    # 1. Sélection des sites à inclure
    df_flux = st.session_state["data"]["m_flux"]
    all_sites = sorted(df_flux["Site hospitalier"].unique())
    
    with st.expander("📍 Sélection et Fréquences des Sites", expanded=True):
        selected_sites = st.multiselect("Sites à intégrer dans l'optimisation", all_sites, default=all_sites[:5])
        
        sites_config = {}
        cols = st.columns(3)
        for i, site in enumerate(selected_sites):
            with cols[i % 3]:
                st.markdown(f"**{site}**")
                freq = st.number_input(f"Passages/jour", min_value=1, value=3, key=f"freq_{site}")
                sites_config[site] = {
                    "open": 480,  # 08:00
                    "close": 1140, # 19:00
                    "freq": freq
                }

    # 2. Paramètres Transport et RH
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚐 Contraintes Transport")
        duree_max = st.slider("Durée max d'une tournée (min)", 30, 240, 120)
        temps_coll = st.slider("Temps fixe par arrêt (min)", 2, 20, 10)
    
    with col2:
        st.subheader("👨‍✈️ Contraintes Chauffeurs (RH)")
        amplitude = st.number_input("Amplitude max poste (min)", value=450, help="7h30 = 450 min")
        pause = st.number_input("Pause déjeuner (min)", value=30)
        releve = st.number_input("Temps de relève véhicule (min)", value=15)

    # Sauvegarde en session_state
    st.session_state["biologie_config"] = {
        "sites": sites_config,
        "duree_max": duree_max,
        "temps_collecte": temps_coll,
        "rh": {"amplitude": amplitude, "pause": pause, "releve": releve}
    }

def show_run_simulation_ui():
    """Bouton de lancement et affichage des résultats synthétiques."""
    if "biologie_config" not in st.session_state:
        return

    st.divider()
    if st.button("🚀 Lancer l'Optimisation des Tournées", use_container_width=True):
        config = st.session_state["biologie_config"]
        df_duree = st.session_state["data"]["matrice_duree"]
        
        with st.spinner("Calcul des tournées en cours..."):
            resultats = run_optimization(
                m_duree_df=df_duree,
                sites_config=config["sites"],
                temps_collecte=config["temps_collecte"],
                max_tournee=config["duree_max"],
                config_rh=config["rh"]
            )
            st.session_state["resultat_flotte"] = resultats
            st.success("Optimisation terminée !")

    if "resultat_flotte" in st.session_state:
        render_summary_dashboard(st.session_state["resultat_flotte"])

def render_summary_dashboard(flotte):
    """Tableau de bord des KPIs après calcul."""
    n_vehicules = len(flotte)
    n_chauffeurs = sum(len(postes) for postes in flotte.values())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🚗 Véhicules Mobilisés", n_vehicules)
    c2.metric("👨‍✈️ Chauffeurs / Vacations", n_chauffeurs)
    c3.metric("📦 Tournées Total", sum(len(p) for v in flotte.values() for p in v))
    
    # Tableau récapitulatif
    summary_data = []
    for v_id, postes in flotte.items():
        summary_data.append({
            "Moyen": v_id,
            "Nb Vacations": len(postes),
            "Premier Départ": f"{postes[0][0][0]['heure']//60:02d}h{postes[0][0][0]['heure']%60:02d}",
            "Dernier Retour": f"{postes[-1][-1][-1]['heure']//60:02d}h{postes[-1][-1][-1]['heure']%60:02d}"
        })
    st.table(pd.DataFrame(summary_data))
