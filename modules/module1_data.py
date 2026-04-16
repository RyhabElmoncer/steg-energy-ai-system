# =============================================================
# MODULE 1 : GESTION DES DONNÉES
# Centrale Thermique de La Goulette - STEG
# =============================================================
# Fonctionnalités :
#   - Import fichier Excel (.xls / .xlsx)
#   - Vérification des colonnes attendues
#   - Nettoyage automatique :
#       * Suppression valeurs manquantes
#       * Détection et suppression des outliers (méthode IQR)
#       * Normalisation des données (optionnelle)
# =============================================================

import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# CONSTANTES : colonnes obligatoires dans le fichier Excel
# ------------------------------------------------------------------
COLONNES_ATTENDUES = [
    'Date',
    'Puissance_MW',
    'Débit_Combustible_Nm3h',
    'Temp_Vapeur_C',
    'Pression_Vapeur_bar',
    'Temp_Condenseur_C',
    'Charge_%'
]

# Plages normales de fonctionnement (pour validation)
PLAGES_NORMALES = {
    'Puissance_MW':            (50,   200),
    'Débit_Combustible_Nm3h':  (8000, 65000),
    'Temp_Vapeur_C':           (450,  580),
    'Pression_Vapeur_bar':     (70,   145),
    'Temp_Condenseur_C':       (20,   55),
    'Charge_%':                (30,   100),
}


# ------------------------------------------------------------------
# FONCTION 1 : Charger le fichier Excel
# ------------------------------------------------------------------
def charger_fichier(fichier_upload):
    """
    Charge un fichier Excel uploadé via Streamlit.
    
    Paramètres :
        fichier_upload : objet UploadedFile de Streamlit
    
    Retourne :
        df (DataFrame) ou None si erreur
        message (str) : message de succès ou d'erreur
    """
    try:
        # Lire le fichier Excel (supporte .xls et .xlsx)
        df = pd.read_excel(fichier_upload, engine='openpyxl')
        message = f"✅ Fichier chargé avec succès : **{len(df)} lignes** et **{len(df.columns)} colonnes**"
        return df, message

    except Exception as e:
        return None, f"❌ Erreur lors du chargement : {str(e)}"


# ------------------------------------------------------------------
# FONCTION 2 : Vérifier les colonnes
# ------------------------------------------------------------------
def verifier_colonnes(df):
    """
    Vérifie que le DataFrame contient toutes les colonnes attendues.
    
    Retourne :
        valide (bool)
        colonnes_manquantes (list)
        colonnes_en_trop (list)
    """
    colonnes_df = list(df.columns)
    manquantes  = [c for c in COLONNES_ATTENDUES if c not in colonnes_df]
    en_trop     = [c for c in colonnes_df if c not in COLONNES_ATTENDUES]

    valide = len(manquantes) == 0
    return valide, manquantes, en_trop


# ------------------------------------------------------------------
# FONCTION 3 : Analyser la qualité des données (avant nettoyage)
# ------------------------------------------------------------------
def analyser_qualite(df):
    """
    Génère un rapport de qualité sur le DataFrame brut.
    
    Retourne :
        rapport (dict) : statistiques de qualité
    """
    rapport = {}

    # Valeurs manquantes par colonne
    rapport['valeurs_manquantes'] = df.isnull().sum().to_dict()
    rapport['total_manquantes']   = df.isnull().sum().sum()
    rapport['pct_manquantes']     = round(df.isnull().mean().mean() * 100, 2)

    # Nombre de doublons
    rapport['doublons'] = df.duplicated().sum()

    # Outliers par colonne numérique (méthode IQR)
    rapport['outliers'] = {}
    for col in PLAGES_NORMALES.keys():
        if col in df.columns:
            Q1  = df[col].quantile(0.25)
            Q3  = df[col].quantile(0.75)
            IQR = Q3 - Q1
            borne_inf = Q1 - 1.5 * IQR
            borne_sup = Q3 + 1.5 * IQR
            n_outliers = ((df[col] < borne_inf) | (df[col] > borne_sup)).sum()
            rapport['outliers'][col] = int(n_outliers)

    rapport['total_outliers'] = sum(rapport['outliers'].values())
    rapport['nb_lignes']      = len(df)

    return rapport


# ------------------------------------------------------------------
# FONCTION 4 : Nettoyer les données
# ------------------------------------------------------------------
def nettoyer_donnees(df, supprimer_outliers=True, normaliser=False):
    """
    Nettoie le DataFrame en 3 étapes :
      1. Conversion de la colonne Date
      2. Suppression des valeurs manquantes
      3. Suppression des outliers (IQR)
      4. Normalisation (optionnelle)
    
    Paramètres :
        df               : DataFrame brut
        supprimer_outliers (bool) : activer la suppression des outliers
        normaliser (bool)         : activer la normalisation Min-Max
    
    Retourne :
        df_propre (DataFrame)
        stats (dict) : résumé du nettoyage
    """
    df_propre = df.copy()
    stats = {
        'lignes_initiales':    len(df_propre),
        'manquantes_supprimees': 0,
        'outliers_supprimes':    0,
        'lignes_finales':        0,
    }

    # --- Étape 1 : Convertir la colonne Date ---
    if 'Date' in df_propre.columns:
        df_propre['Date'] = pd.to_datetime(df_propre['Date'], errors='coerce')

    # --- Étape 2 : Supprimer les lignes avec valeurs manquantes ---
    avant = len(df_propre)
    df_propre = df_propre.dropna(subset=[
        c for c in COLONNES_ATTENDUES if c != 'Date' and c in df_propre.columns
    ])
    stats['manquantes_supprimees'] = avant - len(df_propre)

    # --- Étape 3 : Supprimer les outliers (IQR) ---
    if supprimer_outliers:
        avant = len(df_propre)
        for col in PLAGES_NORMALES.keys():
            if col in df_propre.columns:
                Q1  = df_propre[col].quantile(0.25)
                Q3  = df_propre[col].quantile(0.75)
                IQR = Q3 - Q1
                borne_inf = Q1 - 1.5 * IQR
                borne_sup = Q3 + 1.5 * IQR
                df_propre = df_propre[
                    (df_propre[col] >= borne_inf) &
                    (df_propre[col] <= borne_sup)
                ]
        stats['outliers_supprimes'] = avant - len(df_propre)

    # --- Étape 4 : Normalisation Min-Max (optionnelle) ---
    colonnes_normalisees = []
    if normaliser:
        cols_num = [c for c in PLAGES_NORMALES.keys() if c in df_propre.columns]
        for col in cols_num:
            min_val = df_propre[col].min()
            max_val = df_propre[col].max()
            if max_val != min_val:
                df_propre[col + '_norm'] = (df_propre[col] - min_val) / (max_val - min_val)
                colonnes_normalisees.append(col)

    # Réindexer
    df_propre = df_propre.reset_index(drop=True)

    stats['lignes_finales']       = len(df_propre)
    stats['colonnes_normalisees'] = colonnes_normalisees

    return df_propre, stats


# ------------------------------------------------------------------
# FONCTION 5 : Résumé statistique
# ------------------------------------------------------------------
def get_statistiques(df):
    """
    Retourne un DataFrame de statistiques descriptives formaté.
    """
    cols_num = [c for c in PLAGES_NORMALES.keys() if c in df.columns]
    stats = df[cols_num].describe().round(2)
    return stats


# ------------------------------------------------------------------
# FONCTION 6 : Vérification des plages normales
# ------------------------------------------------------------------
def verifier_plages(df):
    """
    Vérifie si les valeurs sont dans les plages normales de fonctionnement.
    
    Retourne :
        alertes (list of dict) : colonnes hors plage avec détails
    """
    alertes = []
    for col, (min_val, max_val) in PLAGES_NORMALES.items():
        if col not in df.columns:
            continue
        hors_plage = df[(df[col] < min_val) | (df[col] > max_val)]
        if len(hors_plage) > 0:
            alertes.append({
                'colonne':     col,
                'nb_hors_plage': len(hors_plage),
                'plage_normale': f"{min_val} – {max_val}",
                'min_observe':   round(df[col].min(), 2),
                'max_observe':   round(df[col].max(), 2),
            })
    return alertes
