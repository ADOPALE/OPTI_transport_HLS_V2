import pandas as pd

def generate_target_windows(sites_config):
    tasks = []
    for site_name, config in sites_config.items():
        ouv, fer, freq = config['open'], config['close'], config['freq']
        intervalle = (fer - ouv) / freq
        marge = intervalle * 0.20 
        for i in range(freq):
            cible = ouv + (i + 0.5) * intervalle
            tasks.append({
                'site_name': str(site_name).strip().upper(),
                'window': (max(ouv, cible - marge), min(fer, cible + marge)),
                'done': False
            })
    return sorted(tasks, key=lambda x: x['window'][0])

def run_optimization(m_duree_df, sites_config, temps_collecte, max_tournee, config_rh=None):
    # Logique de calcul identique à ta version "Nickel!"
    # ... (Garder le code de calcul pur ici)
    pass

def assign_to_vehicles(tournees, config_rh):
    # Logique d'assignation Chauffeurs vs Véhicules
    # ... (Garder le code d'assignation ici)
    pass
