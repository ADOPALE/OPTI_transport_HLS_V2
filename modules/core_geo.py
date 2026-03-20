import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

def get_coordinates(site_names):
    """Récupère les coordonnées GPS des sites via Nominatim."""
    geolocator = Nominatim(user_agent="hls_optimizer")
    coords = {}
    for name in site_names:
        try:
            location = geolocator.geocode(f"{name}, Auvergne-Rhône-Alpes, France")
            if location:
                coords[name.upper()] = {"lat": location.latitude, "lon": location.longitude}
            time.sleep(1) # Respecter les quotas Nominatim
        except:
            continue
    return coords

def build_dist_matrix(coords):
    """Construit une matrice de distance simplifiée (vol d'oiseau * 1.3)."""
    sites = list(coords.keys())
    matrix = pd.DataFrame(index=sites, columns=sites)
    for s1 in sites:
        for s2 in sites:
            p1 = (coords[s1]['lat'], coords[s1]['lon'])
            p2 = (coords[s2]['lat'], coords[s2]['lon'])
            matrix.loc[s1, s2] = round(geodesic(p1, p2).km * 1.3, 2)
    return matrix
