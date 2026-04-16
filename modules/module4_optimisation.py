# =============================================================
# MODULE 4 : OPTIMISATION ÉNERGÉTIQUE
# Centrale Thermique de La Goulette - STEG
# =============================================================
# Objectif :
#   Trouver la charge optimale (40%, 60%, 80%, 90%) qui maximise
#   le rendement thermique et minimise la consommation spécifique.
# =============================================================

import pandas as pd
import numpy as np

PCI_GAZ = 34.4  # MJ/Nm³


# ------------------------------------------------------------------
# FONCTION 1 : Simuler le rendement pour chaque niveau de charge
# ------------------------------------------------------------------
def simuler_charges(df):
    """
    Pour chaque niveau de charge (40, 60, 80, 90%),
    filtre les données réelles et calcule les indicateurs moyens.

    Retourne :
        resultats (DataFrame) avec colonnes :
            Charge_%, Puissance_MW, Rendement_%, Conso_Specifique, Nb_Points
    """
    niveaux = [40, 60, 80, 90]
    tolerance = 8  # ±8% autour de chaque niveau

    rows = []
    for niveau in niveaux:
        # Filtrer les lignes proches de ce niveau de charge
        masque = (df['Charge_%'] >= niveau - tolerance) & (df['Charge_%'] <= niveau + tolerance)
        subset = df[masque]

        if len(subset) == 0:
            continue

        # Calcul rendement si pas déjà fait
        if 'Rendement_%' not in subset.columns:
            rendement = ((subset['Puissance_MW'] * 3600) / (subset['Débit_Combustible_Nm3h'] * PCI_GAZ) * 100).mean()
        else:
            rendement = subset['Rendement_%'].mean()

        # Consommation spécifique
        conso_spec = (subset['Débit_Combustible_Nm3h'] / subset['Puissance_MW']).mean()

        rows.append({
            'Charge_%':             niveau,
            'Puissance_MW':         round(subset['Puissance_MW'].mean(), 2),
            'Rendement_%':          round(rendement, 2),
            'Conso_Specifique':     round(conso_spec, 1),
            'Nb_Points':            len(subset),
        })

    resultats = pd.DataFrame(rows).sort_values('Rendement_%', ascending=False).reset_index(drop=True)
    return resultats


# ------------------------------------------------------------------
# FONCTION 2 : Identifier la charge optimale
# ------------------------------------------------------------------
def get_charge_optimale(resultats):
    """
    Retourne la ligne avec le meilleur rendement.
    """
    if len(resultats) == 0:
        return None
    return resultats.iloc[0]  # déjà trié par rendement décroissant


# ------------------------------------------------------------------
# FONCTION 3 : Générer une recommandation textuelle
# ------------------------------------------------------------------
def generer_recommandation(charge_opt, resultats):
    """
    Génère un message de recommandation basé sur la charge optimale.
    """
    if charge_opt is None:
        return "⚠️ Pas assez de données pour déterminer la charge optimale."

    charge = charge_opt['Charge_%']
    rend   = charge_opt['Rendement_%']
    conso  = charge_opt['Conso_Specifique']

    # Comparer avec la pire charge
    pire = resultats.iloc[-1]
    gain_rend = round(rend - pire['Rendement_%'], 2)
    gain_conso = round(pire['Conso_Specifique'] - conso, 1)

    msg = (
        f"✅ **Charge optimale recommandée : {charge}%**\n\n"
        f"À cette charge, la centrale atteint un rendement de **{rend}%** "
        f"avec une consommation spécifique de **{conso} Nm³/MWh**.\n\n"
        f"Par rapport à la pire configuration ({pire['Charge_%']}%), "
        f"cela représente un gain de **+{gain_rend}%** de rendement "
        f"et une économie de **{gain_conso} Nm³/MWh** de combustible."
    )
    return msg


# ------------------------------------------------------------------
# FONCTION 4 : Estimer les économies annuelles
# ------------------------------------------------------------------
def estimer_economies(resultats, prix_gaz=0.35):
    """
    Estime les économies annuelles en passant à la charge optimale.

    Paramètres :
        prix_gaz : prix du gaz en DT/Nm³ (défaut 0.35 DT)

    Retourne :
        dict avec économies en Nm³ et en DT
    """
    if len(resultats) < 2:
        return None

    optimal = resultats.iloc[0]
    actuel  = resultats.iloc[-1]  # pire cas

    # Différence de consommation spécifique (Nm³/MWh)
    diff_conso = actuel['Conso_Specifique'] - optimal['Conso_Specifique']

    # Production annuelle estimée (MWh) : 8000h/an × puissance moyenne
    prod_annuelle_mwh = optimal['Puissance_MW'] * 8000

    # Économie annuelle
    eco_nm3 = round(diff_conso * prod_annuelle_mwh, 0)
    eco_dt  = round(eco_nm3 * prix_gaz, 0)

    return {
        'diff_conso_spec':   round(diff_conso, 1),
        'prod_annuelle_mwh': round(prod_annuelle_mwh, 0),
        'eco_nm3':           eco_nm3,
        'eco_dt':            eco_dt,
    }