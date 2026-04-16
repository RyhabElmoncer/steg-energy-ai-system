# =============================================================
# MODULE 5 : TABLEAU DE BORD (DASHBOARD)
# Centrale Thermique de La Goulette - STEG
# =============================================================
# Affiche une vue synthétique de tous les indicateurs clés :
#   - KPIs en temps quasi réel
#   - Graphiques d'évolution multi-paramètres
#   - Alertes et messages d'aide à la décision
#   - Résumé des modules 2, 3 et 4
# =============================================================

import pandas as pd
import numpy as np


# ------------------------------------------------------------------
# FONCTION 1 : Calculer tous les KPIs du dashboard
# ------------------------------------------------------------------
def calculer_kpis(df):
    """
    Calcule les indicateurs clés à partir du DataFrame enrichi.

    Retourne :
        dict avec tous les KPIs
    """
    # Dernière semaine (14 dernières lignes = 7 jours × 2 mesures/jour)
    recent = df.tail(14)

    kpis = {
        # Puissance
        'puissance_actuelle':   round(recent['Puissance_MW'].iloc[-1], 1),
        'puissance_moyenne':    round(df['Puissance_MW'].mean(), 1),
        'puissance_max':        round(df['Puissance_MW'].max(), 1),
        'puissance_min':        round(df['Puissance_MW'].min(), 1),

        # Rendement
        'rendement_actuel':     round(recent['Rendement_%'].iloc[-1], 2) if 'Rendement_%' in recent else 0,
        'rendement_moyen':      round(df['Rendement_%'].mean(), 2)        if 'Rendement_%' in df     else 0,
        'rendement_max':        round(df['Rendement_%'].max(), 2)         if 'Rendement_%' in df     else 0,

        # Consommation spécifique
        'conso_actuelle':       round(recent['Conso_Specifique_Nm3MWh'].iloc[-1], 1) if 'Conso_Specifique_Nm3MWh' in recent else 0,
        'conso_moyenne':        round(df['Conso_Specifique_Nm3MWh'].mean(), 1)       if 'Conso_Specifique_Nm3MWh' in df     else 0,

        # Charge
        'charge_actuelle':      round(recent['Charge_%'].iloc[-1], 1),
        'charge_moyenne':       round(df['Charge_%'].mean(), 1),

        # Anomalies
        'nb_anomalies':         int((df['Anomalie'] != 'Normal').sum()) if 'Anomalie' in df else 0,
        'pct_anomalies':        round((df['Anomalie'] != 'Normal').mean() * 100, 1) if 'Anomalie' in df else 0,

        # Période
        'date_debut':           str(df['Date'].min())[:10] if 'Date' in df else '—',
        'date_fin':             str(df['Date'].max())[:10] if 'Date' in df else '—',
        'nb_jours':             int((pd.to_datetime(df['Date']).max() - pd.to_datetime(df['Date']).min()).days) if 'Date' in df else 0,
        'nb_mesures':           len(df),
    }

    return kpis


# ------------------------------------------------------------------
# FONCTION 2 : Générer les alertes automatiques
# ------------------------------------------------------------------
def generer_alertes(kpis, df):
    """
    Génère une liste de messages d'alertes et recommandations.

    Retourne :
        alertes (list of dict) : { niveau, titre, message }
    """
    alertes = []

    # Alerte rendement
    if kpis['rendement_actuel'] < 30:
        alertes.append({'niveau': 'critique', 'titre': '🔴 Rendement critique',
            'message': f"Le rendement actuel ({kpis['rendement_actuel']}%) est sous le seuil critique de 30%. Inspection immédiate recommandée."})
    elif kpis['rendement_actuel'] < 35:
        alertes.append({'niveau': 'alerte', 'titre': '🟠 Rendement dégradé',
            'message': f"Le rendement ({kpis['rendement_actuel']}%) est en dessous de 35%. Vérifier l'encrassement des échangeurs."})
    else:
        alertes.append({'niveau': 'ok', 'titre': '🟢 Rendement normal',
            'message': f"Le rendement thermique est satisfaisant ({kpis['rendement_actuel']}%)."})

    # Alerte charge
    if kpis['charge_actuelle'] > 95:
        alertes.append({'niveau': 'alerte', 'titre': '🟠 Surcharge détectée',
            'message': f"La charge actuelle ({kpis['charge_actuelle']}%) dépasse 95%. Risque de contraintes mécaniques."})
    elif kpis['charge_actuelle'] < 50:
        alertes.append({'niveau': 'info', 'titre': '🔵 Charge faible',
            'message': f"La charge ({kpis['charge_actuelle']}%) est basse. Rendement non optimal — envisager une montée en charge."})
    else:
        alertes.append({'niveau': 'ok', 'titre': '🟢 Charge normale',
            'message': f"La charge actuelle ({kpis['charge_actuelle']}%) est dans la plage optimale."})

    # Alerte anomalies
    if kpis['pct_anomalies'] > 5:
        alertes.append({'niveau': 'alerte', 'titre': '🟠 Taux d\'anomalies élevé',
            'message': f"{kpis['nb_anomalies']} anomalies détectées ({kpis['pct_anomalies']}% des mesures). Diagnostic approfondi recommandé."})
    elif kpis['nb_anomalies'] > 0:
        alertes.append({'niveau': 'info', 'titre': '🔵 Anomalies mineures',
            'message': f"{kpis['nb_anomalies']} anomalie(s) détectée(s). Surveillance recommandée."})
    else:
        alertes.append({'niveau': 'ok', 'titre': '🟢 Aucune anomalie',
            'message': "Aucune anomalie détectée sur la période analysée."})

    # Recommandation consommation
    if kpis['conso_actuelle'] > kpis['conso_moyenne'] * 1.1:
        alertes.append({'niveau': 'alerte', 'titre': '🟠 Surconsommation de combustible',
            'message': f"La consommation spécifique actuelle ({kpis['conso_actuelle']} Nm³/MWh) dépasse de 10% la moyenne ({kpis['conso_moyenne']} Nm³/MWh)."})

    return alertes


# ------------------------------------------------------------------
# FONCTION 3 : Résumé de tendance (derniers 30 jours vs avant)
# ------------------------------------------------------------------
def calculer_tendances(df):
    """
    Compare les 60 dernières mesures vs les 60 précédentes.

    Retourne :
        dict avec delta rendement, puissance, conso
    """
    if len(df) < 120:
        return None

    recent  = df.tail(60)
    ancien  = df.iloc[-120:-60]

    tendances = {}

    if 'Rendement_%' in df.columns:
        tendances['rendement_delta'] = round(recent['Rendement_%'].mean() - ancien['Rendement_%'].mean(), 2)

    tendances['puissance_delta'] = round(recent['Puissance_MW'].mean() - ancien['Puissance_MW'].mean(), 2)

    if 'Conso_Specifique_Nm3MWh' in df.columns:
        tendances['conso_delta'] = round(recent['Conso_Specifique_Nm3MWh'].mean() - ancien['Conso_Specifique_Nm3MWh'].mean(), 2)

    return tendances