import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import numpy as np

def get_contrast_color(hex_color):
    """Détermine si le texte doit être blanc ou noir selon la luminosité de la couleur."""
    if not hex_color or str(hex_color).startswith('rgba(0,0,0,0)'):
        return "white"
    if str(hex_color).startswith('rgba'):
        return "white"
    hex_color = str(hex_color).lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return "white" if brightness < 128 else "black"
    return "white"

def render_flux_charts(df_flux):
    """Analyse visuelle des flux (Ancien dataViz.py)."""
    if df_flux is None or df_flux.empty:
        st.warning("Données de flux indisponibles.")
        return

    df = df_flux.copy()
    df.columns = df.columns.str.strip()
    
    col_fonc = "Fonction Support associée"
    col_sens = "Aller / Retour"
    jours_cols = ["Quantité Lundi", "Quantité Mardi", "Quantité Mercredi", "Quantité Jeudi", "Quantité Vendredi", "Quantité Samedi", "Quantité Dimanche"]

    # Nettoyage des données numériques
    for j in jours_cols:
        if j in df.columns:
            df[j] = pd.to_numeric(df[j], errors='coerce').fillna(0)

    # Passage en format long pour Plotly
    df_long = df.melt(id_vars=[col_fonc, col_sens], value_vars=[c for c in jours_cols if c in df.columns],
                      var_name="Jour_Full", value_name="Valeur")
    df_long["Jour"] = df_long["Jour_Full"].str.replace("Quantité ", "").str.strip()
    ordre = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df_long["Jour"] = pd.Categorical(df_long["Jour"], categories=ordre, ordered=True)

    # Graphique principal
    st.subheader("📊 Répartition Globale des Flux")
    fig = px.bar(df_long, x="Jour", y="Valeur", color=col_fonc, 
                 barmode="stack", facet_row=col_sens, template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

def render_route_map(tournee, coords):
    """Affiche une carte Folium pour une tournée spécifique (Ancien bioViz.py)."""
    if not tournee or not coords:
        st.info("Sélectionnez une vacation pour afficher la carte.")
        return

    # Centrer la carte sur le premier point
    first_site = tournee[0]['site']
    center = [coords[first_site]['lat'], coords[first_site]['lon']] if first_site in coords else [47.21, -1.55]
    
    m = folium.Map(location=center, zoom_start=11, control_scale=True)
    
    points = []
    for step in tournee:
        s_name = step['site']
        if s_name in coords:
            pos = [coords[s_name]['lat'], coords[s_name]['lon']]
            points.append(pos)
            folium.Marker(
                location=pos,
                popup=f"{step['heure']//60:02d}h{step['heure']%60:02d} : {s_name}",
                tooltip=s_name,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
    
    if len(points) > 1:
        folium.PolyLine(points, color="red", weight=2.5, opacity=0.8).add_to(m)
    
    st_folium(m, width=800, height=500)

def render_timeline_plotly(flotte):
    """Affiche la frise chronologique de tous les véhicules."""
    data = []
    for v_id, postes in flotte.items():
        for p_idx, vacation in enumerate(postes):
            for t_idx, tournee in enumerate(vacation):
                start_h = tournee[0]['heure']
                end_h = tournee[-1]['heure']
                data.append({
                    "Véhicule": v_id,
                    "Chauffeur": f"Vacation {p_idx+1}",
                    "Début": start_h,
                    "Fin": end_h,
                    "Label": f"T{t_idx+1} ({int(end_h-start_h)} min)"
                })
    
    df_plot = pd.DataFrame(data)
    fig = px.timeline(df_plot, x_start="Début", x_end="Fin", y="Véhicule", color="Chauffeur",
                       text="Label", template="plotly_dark", title="Frise Chronologique des Véhicules")
    
    # Correction pour afficher des heures au lieu de dates sur l'axe X
    fig.update_layout(xaxis=dict(type='linear')) 
    st.plotly_chart(fig, use_container_width=True)
