import pandas as pd
import streamlit as st

def load_all_data(uploaded_file):
    """Charge toutes les feuilles du fichier Excel et les stocke dans un dictionnaire."""
    try:
        # Lecture de toutes les feuilles
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        
        # Mapping et nettoyage basique
        data = {
            "m_flux": sheets.get("MATRICE_FLUX"),
            "accessibilite_sites": sheets.get("ACCESSIBILITE_SITES"),
            "matrice_duree": sheets.get("MATRICE_DUREE"),
            "matrice_distance": sheets.get("MATRICE_DISTANCE")
        }
        
        # Nettoyage des noms de colonnes (espaces invisibles)
        for key in data:
            if data[key] is not None:
                data[key].columns = data[key].columns.astype(str).str.strip()
                
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'Excel : {e}")
        return None

def get_clean_matrix(df):
    """Prépare une matrice (duree ou distance) avec les sites en index majuscules."""
    df_clean = df.copy()
    first_col = df_clean.columns[0]
    df_clean = df_clean.set_index(first_col)
    df_clean.index = df_clean.index.astype(str).str.strip().str.upper()
    df_clean.columns = df_clean.columns.astype(str).str.strip().str.upper()
    return df_clean
