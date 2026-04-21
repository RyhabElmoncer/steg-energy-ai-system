# =============================================================
# MODULE 6 — Discussion IA
# Système Intelligent de Diagnostic Énergétique
# Centrale Thermique de La Goulette - STEG
# =============================================================

import json
import requests
import pandas as pd

import streamlit as st
SYSTEM_PROMPT_BASE = """Tu es un expert en ingénierie des centrales thermiques, spécialisé dans le diagnostic
énergétique et l'optimisation des performances. Tu travailles pour la STEG (Société Tunisienne
de l'Électricité et du Gaz), sur la Centrale Thermique de La Goulette (capacité nominale 180 MW,
combustible gaz naturel, PCI = 34.4 MJ/Nm³).

Ton rôle est d'analyser les données opérationnelles fournies et d'avoir une conversation experte
avec l'ingénieur de service. Tu dois :
  - Proposer des diagnostics précis basés sur les données réelles
  - Suggérer des scénarios de problèmes et leurs causes racines probables
  - Fournir des solutions prédictives et préventives concrètes
  - Estimer des impacts économiques en DT (dinars tunisiens) quand pertinent
  - Utiliser un vocabulaire technique adapté (thermodynamique, turbomachines, échangeurs)
  - Répondre en français sauf si l'utilisateur demande une autre langue

Lorsque tu proposes des scénarios, structure-les ainsi :
  CRITIQUE  — action immédiate requise
  ALERTE    — surveillance accrue
  OK / INFO — information préventive

Sois concis mais complet. Utilise des listes à puces pour la clarté.
"""


def construire_contexte_donnees(df: pd.DataFrame | None) -> str:
    """Génère un résumé textuel des données pour enrichir le prompt système."""
    if df is None or df.empty:
        return "\n[Aucune donnée opérationnelle chargée pour cette session.]"

    cols = df.columns.tolist()
    lignes = []

    lignes.append("\n\n--- DONNÉES OPÉRATIONNELLES EN COURS ---")
    lignes.append(f"Période    : {df['Date'].min()} → {df['Date'].max()}" if 'Date' in cols else "")
    lignes.append(f"Nb mesures : {len(df)}")

    num_cols = {
        'Puissance_MW':              'MW',
        'Débit_Combustible_Nm3h':    'Nm³/h',
        'Temp_Vapeur_C':             '°C',
        'Pression_Vapeur_bar':       'bar',
        'Temp_Condenseur_C':         '°C',
        'Charge_%':                  '%',
        'Rendement_%':               '%',
        'Conso_Specifique_Nm3MWh':   'Nm³/MWh',
    }

    lignes.append("\nStatistiques clés :")
    for col, unite in num_cols.items():
        if col in df.columns:
            s = df[col].describe()
            lignes.append(
                f"  {col:<35} moy={s['mean']:.2f} | min={s['min']:.2f} | max={s['max']:.2f} {unite}"
            )

    if 'Anomalie' in df.columns:
        nb_anomalies = (df['Anomalie'] != 'Normal').sum()
        pct = round(nb_anomalies / len(df) * 100, 1)
        lignes.append(f"\nAnomalies détectées : {nb_anomalies} ({pct}% des mesures)")
        types = df[df['Anomalie'] != 'Normal']['Anomalie'].value_counts()
        for t, n in types.items():
            lignes.append(f"  - {t} : {n} occurrences")

    lignes.append("--- FIN DONNÉES ---")
    return "\n".join(l for l in lignes if l)


def construire_system_prompt(df: pd.DataFrame | None) -> str:
    """Assemble le prompt système complet avec contexte données."""
    contexte = construire_contexte_donnees(df)
    return SYSTEM_PROMPT_BASE + contexte


def appeler_api_claude(historique: list[dict], system_prompt: str) -> tuple[str, str]:
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Clé API manquante. Vérifiez .streamlit/secrets.toml", "erreur"

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,              # ← ajout
                "anthropic-version": "2023-06-01", # ← recommandé
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "system":     system_prompt,
                "messages":   historique,
            },
            timeout=60,
        )
        data = response.json()

        if response.status_code != 200:
            err = data.get("error", {}).get("message", "Erreur inconnue")
            return f"Erreur API ({response.status_code}) : {err}", "erreur"

        texte = "".join(
            bloc.get("text", "")
            for bloc in data.get("content", [])
            if bloc.get("type") == "text"
        )
        return texte or "Réponse vide reçue.", "ok"

    except requests.exceptions.Timeout:
        return "Délai d'attente dépassé. Réessayez.", "erreur"
    except Exception as e:
        return f"Erreur de connexion : {str(e)}", "erreur"


# ── Suggestions de questions prêtes à l'emploi ────────────────────────
SUGGESTIONS = [
    {
        "categorie": "Diagnostic",
        "questions": [
            "Quelles sont les causes probables d'une chute de rendement en dessous de 30% ?",
            "Mon débit combustible est élevé mais la puissance reste faible. Diagnostic ?",
            "Analyse les anomalies détectées et propose un plan d'action.",
        ]
    },
    {
        "categorie": "Scénarios de pannes",
        "questions": [
            "Quels scénarios peuvent expliquer une température vapeur anormalement basse ?",
            "Donne-moi les 3 scénarios les plus probables pour une pression vapeur instable.",
            "Que se passe-t-il si la température condenseur dépasse 45°C ?",
        ]
    },
    {
        "categorie": "Optimisation",
        "questions": [
            "Comment optimiser la consommation spécifique pour réduire les coûts de combustible ?",
            "Quelle charge recommandes-tu pour maximiser le rendement thermique ?",
            "Estime les économies annuelles si on améliore le rendement de 2 points.",
        ]
    },
    {
        "categorie": "Maintenance prédictive",
        "questions": [
            "Quels indicateurs surveiller pour détecter une dégradation des aubes turbine ?",
            "Propose un planning de maintenance préventive basé sur les données actuelles.",
            "Quand recommandes-tu le prochain arrêt pour inspection ?",
        ]
    },
]