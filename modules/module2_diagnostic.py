# =============================================================
# MODULE 2 : DIAGNOSTIC ÉNERGÉTIQUE
# Centrale Thermique de La Goulette - STEG
# =============================================================

import pandas as pd
import numpy as np

# PCI du gaz naturel (MJ/Nm³)
PCI_GAZ = 34.4  # MJ/Nm³  →  1 MJ = 1/3.6 kWh


# ------------------------------------------------------------------
# FONCTION 1 : Calcul du rendement thermique
# η = (Puissance_MW × 3600) / (Débit × PCI) × 100
# ------------------------------------------------------------------
def calculer_rendement(df):
    """
    Ajoute une colonne 'Rendement_%' au DataFrame.
    Formule : η = (P_MW * 3600) / (Débit * PCI) * 100
    """
    df = df.copy()
    df['Rendement_%'] = (
        (df['Puissance_MW'] * 3600) /
        (df['Débit_Combustible_Nm3h'] * PCI_GAZ)
    ) * 100
    df['Rendement_%'] = df['Rendement_%'].round(2)
    return df


# ------------------------------------------------------------------
# FONCTION 2 : Calcul de la consommation spécifique
# Cs = Débit / Puissance  (Nm³/MWh)
# ------------------------------------------------------------------
def calculer_consommation_specifique(df):
    """
    Ajoute une colonne 'Conso_Specifique_Nm3MWh'.
    Formule : Cs = Débit / Puissance
    """
    df = df.copy()
    df['Conso_Specifique_Nm3MWh'] = (
        df['Débit_Combustible_Nm3h'] / df['Puissance_MW']
    ).round(2)
    return df


# ------------------------------------------------------------------
# FONCTION 3 : Détection des anomalies
# ------------------------------------------------------------------
def detecter_anomalies(df):
    """
    Détecte les anomalies selon 3 critères :
      - Rendement < 30%        → Alerte critique
      - Charge > 95%           → Surcharge
      - Temp vapeur hors plage → Avertissement
    
    Retourne :
        df avec colonne 'Anomalie'
        liste de dicts résumant chaque anomalie
    """
    df = df.copy()
    df['Anomalie'] = 'Normal'

    # Critère 1 : rendement faible
    if 'Rendement_%' in df.columns:
        df.loc[df['Rendement_%'] < 30, 'Anomalie'] = 'Rendement bas'

    # Critère 2 : surcharge
    df.loc[df['Charge_%'] > 95, 'Anomalie'] = 'Surcharge'

    # Critère 3 : température vapeur hors plage [450–570°C]
    df.loc[
        (df['Temp_Vapeur_C'] < 450) | (df['Temp_Vapeur_C'] > 570),
        'Anomalie'
    ] = 'Température anormale'

    # Résumé des anomalies
    resume = df[df['Anomalie'] != 'Normal'].groupby('Anomalie').size().reset_index()
    resume.columns = ['Type anomalie', 'Nombre']

    return df, resume


# ------------------------------------------------------------------
# FONCTION 4 : État global du système
# ------------------------------------------------------------------
def get_etat_systeme(df):
    """
    Retourne l'état global et une recommandation basée sur
    les dernières 10 lignes (données récentes).
    
    Retourne :
        etat   : 'Normal' | 'Alerte' | 'Critique'
        message: recommandation textuelle
        couleur: 'green' | 'orange' | 'red'
    """
    recents = df.tail(10)

    rendement_moy = recents['Rendement_%'].mean() if 'Rendement_%' in recents else 0
    charge_max    = recents['Charge_%'].max()
    temp_moy      = recents['Temp_Vapeur_C'].mean()

    if rendement_moy < 30:
        return 'Critique', f"⚠️ Rendement moyen très bas ({rendement_moy:.1f}%). Vérifier chaudière et turbine.", 'red'
    elif rendement_moy < 35:
        return 'Alerte', f"🔶 Rendement dégradé ({rendement_moy:.1f}%). Vérifier l'encrassement des échangeurs.", 'orange'
    elif charge_max > 95:
        return 'Alerte', f"🔶 Surcharge détectée ({charge_max:.1f}%). Réduire la charge pour protéger les équipements.", 'orange'
    elif temp_moy < 460 or temp_moy > 560:
        return 'Alerte', f"🔶 Température vapeur hors plage ({temp_moy:.1f}°C). Vérifier les paramètres de la chaudière.", 'orange'
    else:
        return 'Normal', f"✅ Système en bon état. Rendement moyen : {rendement_moy:.1f}%. Charge : {charge_max:.1f}%.", 'green'