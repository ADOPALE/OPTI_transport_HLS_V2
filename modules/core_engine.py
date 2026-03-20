import pandas as pd

def generate_target_windows(sites_config):
    """Génère les créneaux cibles basés sur l'ouverture et la fréquence."""
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
    """Calcule les tournées unitaires avec contrainte de site unique."""
    if config_rh is None:
        config_rh = {'amplitude': 450, 'pause': 30, 'releve': 15}

    # Préparation matrice
    from modules.data_handler import get_clean_matrix
    df = get_clean_matrix(m_duree_df)
    depot = "HLS"
    
    tasks = generate_target_windows(sites_config)
    tournees_unitaires = []
    tasks_copy = [t.copy() for t in tasks]
    
    while any(not t['done'] for t in tasks_copy):
        remaining = [t for t in tasks_copy if not t['done']]
        if not remaining: break
        
        first_task = remaining[0]
        site_cible = first_task['site_name']
        if site_cible not in df.index:
            first_task['done'] = True
            continue

        heure_depart = max(300, first_task['window'][0] - df.loc[depot, site_cible])
        current_time = heure_depart
        tournee = [{'site': depot, 'heure': current_time}]
        current_site = depot
        sites_visites_cette_tournee = set()

        while True:
            best_task_idx = None
            score_min = float('inf')
            
            for idx, task in enumerate(tasks_copy):
                t_site = task['site_name']
                if task['done'] or t_site not in df.index or t_site in sites_visites_cette_tournee:
                    continue
                
                trajet = df.loc[current_site, t_site]
                retour = df.loc[t_site, depot]
                arrivee = current_time + trajet
                debut_coll = max(arrivee, task['window'][0])
                fin_coll = debut_coll + temps_collecte
                
                if (fin_coll + retour - tournee[0]['heure']) <= max_tournee:
                    attente = max(0, task['window'][0] - arrivee)
                    score = attente + (trajet * 2) 
                    if score < score_min:
                        score_min, best_task_idx = score, idx
            
            if best_task_idx is not None:
                task = tasks_copy[best_task_idx]
                t_site = task['site_name']
                heure_reelle = max(current_time + df.loc[current_site, t_site], task['window'][0])
                tournee.append({'site': t_site, 'heure': heure_reelle})
                current_time = heure_reelle + temps_collecte
                task['done'] = True
                current_site = t_site
                sites_visites_cette_tournee.add(t_site)
                # Bloquer sites distance 0
                for s_adj in df.columns:
                    if df.loc[t_site, s_adj] == 0: sites_visites_cette_tournee.add(s_adj)
            else:
                tournee.append({'site': depot, 'heure': current_time + df.loc[current_site, depot]})
                break
        tournees_unitaires.append(tournee)
    
    return assign_to_vehicles(tournees_unitaires, config_rh)

def assign_to_vehicles(tournees, config_rh):
    """Logique d'attribution Véhicules vs Chauffeurs (Postes)."""
    MAX_POSTE = config_rh.get('amplitude', 450)
    PAUSE = config_rh.get('pause', 30)
    RELEVE = config_rh.get('releve', 15)
    
    tournees_triees = sorted(tournees, key=lambda x: x[0]['heure'])
    flotte = {}
    
    for trne in tournees_triees:
        debut, fin = trne[0]['heure'], trne[-1]['heure']
        assigned = False
        for v_id, postes in flotte.items():
            der_p = postes[-1]
            h_d_p, h_f_p = der_p[0][0]['heure'], der_p[-1][-1]['heure']
            if (fin - h_d_p) <= MAX_POSTE:
                marge = PAUSE if (h_f_p - h_d_p) > 180 else 0
                if h_f_p + marge <= debut:
                    der_p.append(trne)
                    assigned = True; break
            elif h_f_p + RELEVE <= debut:
                postes.append([trne])
                assigned = True; break
        if not assigned:
            flotte[f"Véhicule {len(flotte)+1}"] = [[trne]]
    return flotte
