# =============================================================
# MODULE 3 : PRÉDICTION INTELLIGENTE (Machine Learning)
# Centrale Thermique de La Goulette - STEG
# =============================================================
# Modèles utilisés :
#   - Régression Linéaire  (simple, interprétable)
#   - Random Forest        (plus précis, non linéaire)
#
# Variables d'entrée (features) :
#   - Charge_%
#   - Temp_Vapeur_C
#   - Débit_Combustible_Nm3h
#
# Variable cible :
#   - Puissance_MW
# =============================================================

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler


# Colonnes utilisées
FEATURES = ['Charge_%', 'Temp_Vapeur_C', 'Débit_Combustible_Nm3h']
CIBLE    = 'Puissance_MW'


# ------------------------------------------------------------------
# FONCTION 1 : Préparer les données pour le ML
# ------------------------------------------------------------------
def preparer_donnees(df, test_size=0.2):
    """
    Sépare les features (X) et la cible (y),
    puis split en train/test (80/20 par défaut).

    Retourne :
        X_train, X_test, y_train, y_test
    """
    # Vérifier que toutes les colonnes existent
    cols_manquantes = [c for c in FEATURES + [CIBLE] if c not in df.columns]
    if cols_manquantes:
        raise ValueError(f"Colonnes manquantes : {cols_manquantes}")

    # Supprimer les lignes avec valeurs manquantes sur ces colonnes
    df_ml = df[FEATURES + [CIBLE]].dropna()

    X = df_ml[FEATURES]
    y = df_ml[CIBLE]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    return X_train, X_test, y_train, y_test


# ------------------------------------------------------------------
# FONCTION 2 : Entraîner les deux modèles
# ------------------------------------------------------------------
def entrainer_modeles(X_train, y_train):
    """
    Entraîne Régression Linéaire et Random Forest.

    Retourne :
        modeles (dict) : {'regression': model, 'random_forest': model}
    """
    # Régression Linéaire
    model_lr = LinearRegression()
    model_lr.fit(X_train, y_train)

    # Random Forest
    model_rf = RandomForestRegressor(
        n_estimators=100,   # 100 arbres
        max_depth=10,
        random_state=42,
        n_jobs=-1           # utiliser tous les cœurs CPU
    )
    model_rf.fit(X_train, y_train)

    return {
        'regression':    model_lr,
        'random_forest': model_rf
    }


# ------------------------------------------------------------------
# FONCTION 3 : Évaluer les modèles
# ------------------------------------------------------------------
def evaluer_modeles(modeles, X_test, y_test):
    """
    Calcule R² et MAE pour chaque modèle.

    Retourne :
        resultats (dict) avec métriques + prédictions
    """
    resultats = {}

    for nom, model in modeles.items():
        y_pred = model.predict(X_test)

        r2  = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        resultats[nom] = {
            'r2':        round(r2,  4),
            'mae':       round(mae, 3),
            'y_pred':    y_pred,
            'y_test':    y_test.values,
            'label':     'Régression Linéaire' if nom == 'regression' else 'Random Forest',
        }

    return resultats


# ------------------------------------------------------------------
# FONCTION 4 : Choisir le meilleur modèle
# ------------------------------------------------------------------
def meilleur_modele(resultats):
    """
    Retourne le nom du modèle avec le meilleur R².
    """
    return max(resultats, key=lambda k: resultats[k]['r2'])


# ------------------------------------------------------------------
# FONCTION 5 : Prédire une valeur manuelle
# ------------------------------------------------------------------
def predire_manuel(modeles, charge, temp_vapeur, debit):
    """
    Prédit la puissance pour des valeurs saisies manuellement.

    Paramètres :
        charge      : Charge_%
        temp_vapeur : Temp_Vapeur_C
        debit       : Débit_Combustible_Nm3h

    Retourne :
        dict { 'regression': valeur_MW, 'random_forest': valeur_MW }
    """
    X_input = pd.DataFrame([[charge, temp_vapeur, debit]], columns=FEATURES)

    predictions = {}
    for nom, model in modeles.items():
        val = model.predict(X_input)[0]
        predictions[nom] = round(float(val), 2)

    return predictions


# ------------------------------------------------------------------
# FONCTION 6 : Importance des features (Random Forest)
# ------------------------------------------------------------------
def importance_features(modeles):
    """
    Retourne l'importance des variables pour le Random Forest.
    """
    rf = modeles.get('random_forest')
    if rf is None:
        return None

    importances = pd.DataFrame({
        'Feature':    FEATURES,
        'Importance': rf.feature_importances_.round(4)
    }).sort_values('Importance', ascending=False)

    return importances