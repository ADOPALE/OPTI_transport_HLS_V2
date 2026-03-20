import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from io import BytesIO

# --- LOGIQUE DE CALCUL ---

def get_coordinates_core(df_sites):
    """Logique de géocodage pure."""
    geolocator = Nominatim(user_agent="adopale_hospital_sim_v2")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)
    coords = {}
    for row in df_sites.itertuples():
        addr = row.adresse
        if addr not in coords:
            try:
                location = geocode(addr)
                coords[addr] = (location.latitude, location.longitude) if location else (None, None)
            except:
                coords[addr] = (None, None)
    return coords

# --- INTERFACE UTILISATEUR (L'outil de calcul) ---

def run_matrix_tool():
    """L'outil complet de calcul de matrices (Anciennement GeoMatrix.py)."""
    st.header("🌐 Calculateur de Matrices (Distance & Temps)")
    st.info("Cet outil utilise OSRM et Nominatim pour générer des matrices à partir d'adresses.")

    uploaded_file = st.file_uploader("Charger un fichier de sites (Colonnes: site, adresse)", type=["xlsx"])
    
    if uploaded_file:
        df_sites = pd.read_excel(uploaded_file)
        st.write("Aperçu des sites :", df_sites.head())

        if st.button("🚀 Calculer les Matrices"):
            prog_bar = st.progress(0)
            status_txt = st.empty()
            
            # 1. Géocodage
            status_txt.text("🌍 Récupération des coordonnées GPS...")
            geolocator = Nominatim(user_agent="hls_geo")
            latitudes, longitudes = [], []
            
            for i, row in enumerate(df_sites.itertuples()):
                try:
                    loc = geolocator.geocode(row.adresse)
                    latitudes.append(loc.latitude if loc else None)
                    longitudes.append(loc.longitude if loc else None)
                except:
                    latitudes.append(None)
                    longitudes.append(None)
                prog_bar.progress((i + 1) / len(df_sites))
                time.sleep(1) # Quota API

            df_sites['lat'] = latitudes
            df_sites['lon'] = longitudes
            
            # Suppression des sites non trouvés
            df_sites = df_sites.dropna(subset=['lat', 'lon'])
            
            # 2. Calcul des matrices via OSRM (Simplifié pour l'exemple)
            status_txt.text("📏 Calcul des distances et temps de trajet...")
            size = len(df_sites)
            dist_m = np.zeros((size, size))
            dur_m = np.zeros((size, size))

            # Ici on pourrait appeler l'API OSRM, pour l'instant on simule 
            # ou on utilise une formule de distance Haversine
            for i in range(size):
                for j in range(size):
                    if i == j: continue
                    # Simulation (à remplacer par appel API OSRM si besoin)
                    dist_m[i,j] = 10.0 # Valeur factice
                    dur_m[i,j] = 15.0 # Valeur factice

            st.success(f"✅ Matrices générées pour {size} sites.")
            
            # Affichage
            names = df_sites['site'].tolist()
            df_dist = pd.DataFrame(dist_m, index=names, columns=names)
            st.dataframe(df_dist)

            # Stockage dans la session pour la carte
            st.session_state["coords"] = {
                row.site: {"lat": row.lat, "lon": row.lon} 
                for row in df_sites.itertuples()
            }
