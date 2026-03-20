import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium

def get_contrast_color(hex_color):
    if hex_color.startswith('rgba'): return "white"
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return "white" if (r * 299 + g * 587 + b * 114) / 1000 < 128 else "black"

def render_flux_charts(df):
    """Affiche les graphiques Aller/Retour de dataViz."""
    st.subheader("📊 Analyse des Flux")
    # ... Insérer ici le code Plotly/Tableau de ton ancien dataViz.py ...
    st.info("Graphiques de flux générés.")

def render_simulation_results(flotte, coords):
    """Affiche la synthèse, la frise et la carte Folium."""
    st.metric("🚗 Véhicules", len(flotte))
    st.metric("👨‍✈️ Chauffeurs", sum(len(p) for p in flotte.values()))
    
    # Carte
    v_sel = st.selectbox("Véhicule", list(flotte.keys()))
    p_idx = st.selectbox("Vacation", range(len(flotte[v_sel])))
    
    tournees = flotte[v_sel][p_idx]
    m = folium.Map(location=[45.77, 3.08], zoom_start=12)
    # ... Logique Folium pour tracer les PolyLines ...
    st_folium(m, width=700, height=400)
