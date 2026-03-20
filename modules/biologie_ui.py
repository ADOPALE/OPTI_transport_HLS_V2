import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from modules.biologie_engine import run_optimization

# ==========================================
# 1. CONFIGURATION DES SITES (ONGLET PASSAGES)
# ==========================================

def show_biologie_config():
    st.title("🧪 Paramétrage des Passages Biologie")
    # On récupère l'état du verrou
    est_verrouille =  st.button("💾 Enregistrer la configuration")

    if not est_verrouille:
        if st.button("Enregistrer le paramétrage"):
            st.session_state.biologie_verrouille = True
            st.success("Paramètres sauvegardés !")
            st.rerun()

    if "data" not in st.session_state:
        st.warning("⚠️ Veuillez d'abord importer un fichier Excel dans l'onglet 'Importer Données'.")
        return

    data = st.session_state["data"]
    # On récupère la liste des sites depuis l'import
    df_sites = data["accessibilite_sites"]
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        duree_max = st.number_input("Durée max d'une tournée (min)", value=200, help="Temps total max entre le départ et le retour au HLS")
    with col_g2:
        temps_coll = st.number_input("Temps de collecte par site (min)", value=10)

    st.divider()
    st.subheader("🏥 Configuration par site")

    current_sites_config = {}

    for _, row in df_sites.iterrows():
        site_name = str(row['site']).strip().upper()
        if site_name == "HLS": continue 
        
        cols = st.columns([1, 4])
        is_active = cols[0].checkbox("Inclure", value=True, key=f"check_{site_name}")
        
        if is_active:
            with cols[1].expander(f"📍 {site_name}", expanded=False):
                c1, c2 = st.columns([3, 1])
                with c1:
                    res = st.select_slider(
                        "Plage horaire d'ouverture",
                        options=range(0, 1441, 15),
                        value=(480, 1080), # 08:00 - 18:00
                        format_func=lambda x: f"{x//60:02d}:{x%60:02d}",
                        key=f"slide_{site_name}"
                    )
                with c2:
                    freq = st.number_input("Passages/jour", min_value=1, value=3, key=f"freq_{site_name}")

                current_sites_config[site_name] = {
                    'open': res[0],
                    'close': res[1],
                    'freq': freq
                }
        else:
            cols[1].info(f"❄️ {site_name} est exclu de la simulation.")

    if st.button("💾 Enregistrer la configuration", use_container_width=True, type="primary"):
        st.session_state["biologie_config"] = {
            "duree_max": duree_max,
            "temps_collecte": temps_coll,
            "sites": current_sites_config
        }
        st.success(f"Configuration enregistrée pour {len(current_sites_config)} sites.")

# ==========================================
# 2. PAGE DE LANCEMENT DE SIMULATION
# ==========================================

def show_simulation_page():
    st.title("🏎️ Optimisation des tournées")
    
    if "biologie_config" not in st.session_state:
        st.warning("⚠️ Configurez d'abord les passages dans l'onglet 'Passages Biologie'.")
        return

    config = st.session_state["biologie_config"]
    df_duree = st.session_state["data"]["matrice_duree"]

    st.info(f"Prêt à optimiser les flux pour {len(config['sites'])} sites hospitaliers.")

    if st.button("🚀 Lancer l'algorithme d'optimisation", use_container_width=True, type="primary"):
        with st.spinner("🧠 Calcul des tournées optimales..."):
            try:
                resultats = run_optimization(
                    m_duree_df=df_duree,
                    sites_config=config["sites"],
                    temps_collecte=config["temps_collecte"],
                    max_tournee=config["duree_max"]
                )
                st.session_state.resultat_flotte = resultats
                st.session_state.sim_lancee = True
                st.success(f"✅ Simulation terminée : {len(resultats)} véhicules mobilisés.")
                st.balloons()
            except Exception as e:
                st.error(f"Erreur lors du calcul : {e}")

# ==========================================
# 3. AFFICHAGE DES RÉSULTATS DÉTAILLÉS
# ==========================================

def show_detail_tournees():
    if "resultat_flotte" not in st.session_state:
        st.info("Aucun résultat à afficher.")
        return

    flotte = st.session_state.resultat_flotte
    
    # Récupération sécurisée de la matrice de distance pour les KPIs
    data_store = st.session_state.get("data", {})
    df_dist = data_store.get("matrice_distance", data_store.get("matrice_duree")).copy()
    
    if isinstance(df_dist.index, pd.RangeIndex) or df_dist.index.dtype in ['int64', 'float64']:
        df_dist = df_dist.set_index(df_dist.columns[0])
    df_dist.index = df_dist.index.astype(str).str.strip().str.upper()
    df_dist.columns = df_dist.columns.astype(str).str.strip().str.upper()

    # --- SYNTHÈSE FLOTTE ---
    st.subheader("📊 Performance de la Flotte")
    summary = []
    for i, v_tours in enumerate(flotte):
        h_start, h_end = v_tours[0][0]['heure'], v_tours[-1][-1]['heure']
        dist = 0
        for t in v_tours:
            for j in range(len(t)-1):
                a, b = str(t[j]['site']).upper(), str(t[j+1]['site']).upper()
                if a in df_dist.index and b in df_dist.columns:
                    dist += df_dist.loc[a, b]
        
        summary.append({
            "Véhicule": f"Véhicule {i+1}",
            "Amplitude": f"{int(h_start//60):02d}:{int(h_start%60):02d} - {int(h_end//60):02d}:{int(h_end%60):02d}",
            "Distance (km)": round(dist, 1),
            "Tournées": len(v_tours),
            "Occupation": f"{min(100, round(((h_end-h_start)/480)*100, 1))}%"
        })
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    # --- FRISE CHRONOLOGIQUE ---
    st.divider()
    st.subheader("⏱️ Passages par Site")
    all_p = []
    for i, v in enumerate(flotte):
        for t in v:
            for s in t:
                if s['site'].upper() != "HLS":
                    all_p.append({"Site": s['site'].upper(), "Heure": s['heure'], 
                                 "Label": f"{int(s['heure']//60):02d}:{int(s['heure']%60):02d}", "V": f"V{i+1}"})
    df_p = pd.DataFrame(all_p)
    if not df_p.empty:
        site_sel = st.selectbox("Site à contrôler", sorted(df_p["Site"].unique()))
        fig = px.scatter(df_p[df_p["Site"]==site_sel], x="Heure", y=[site_sel]*len(df_p[df_p["Site"]==site_sel]),
                         color="V", hover_data={"Heure":False, "Label":True}, height=200)
        fig.update_layout(xaxis=dict(tickvals=list(range(180, 1380, 60)), 
                          ticktext=[f"{h//60:02d}:00" for h in range(180, 1380, 60)]), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # --- CARTE ---
    st.divider()
    st.subheader("🗺️ Itinéraires")
    c1, c2 = st.columns(2)
    v_idx = c1.selectbox("Sélectionner Véhicule", range(len(flotte)), format_func=lambda x: f"Véhicule {x+1}")
    t_idx = c2.selectbox("Sélectionner Tournée", range(len(flotte[v_idx])), format_func=lambda x: f"Tournée {x+1}")
    
    tournee = flotte[v_idx][t_idx]
    col_m, col_l = st.columns([2, 1])
    
    with col_l:
        for s in tournee:
            st.write(f"📍 **{int(s['heure']//60):02d}:{int(s['heure']%60):02d}** : {s['site']}")

    with col_m:
        if "coords_sites" in st.session_state:
            coords = st.session_state.coords_sites
            m = folium.Map(location=[45.77, 3.08], zoom_start=12)
            pts = []
            for s in tournee:
                n = s['site'].upper()
                if n in coords:
                    p = [coords[n]['lat'], coords[n]['lon']]
                    pts.append(p)
                    folium.Marker(p, tooltip=f"{n} ({int(s['heure']//60):02d}:{int(s['heure']%60):02d})").add_to(m)
            if len(pts) > 1:
                folium.PolyLine(pts, color="blue", weight=3).add_to(m)
            st_folium(m, width=None, height=400)
        else:
            st.info("ℹ️ Géocodage requis pour la carte.")
