import streamlit as st
from modules.core_engine import run_optimization

def show_biologie_config_ui():
    st.title("🧪 Configuration Biologie")
    # ... Champs de saisie (Durée max, temps collecte, RH) ...
    if st.button("Enregistrer"):
        st.session_state["biologie_config"] = {"..."} # Structure config

def show_run_simulation_ui():
    if st.button("🚀 Lancer l'Optimisation"):
        # Appel à run_optimization
        pass
