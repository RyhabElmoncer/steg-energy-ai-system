# ⚡ Système Intelligent de Diagnostic Énergétique

### Centrale Thermique de La Goulette — STEG

---

## 📌 Description

Ce projet est une application intelligente développée avec **Streamlit** permettant d’analyser, diagnostiquer et optimiser les performances énergétiques d’une centrale thermique.

L’application intègre :

* 📊 Analyse de données
* ⚙️ Diagnostic énergétique
* 🤖 Machine Learning
* 📈 Optimisation des performances
* 📉 Dashboard interactif

---

## 🎯 Objectifs

* Améliorer le rendement énergétique
* Détecter les anomalies de fonctionnement
* Prédire la production électrique
* Optimiser la consommation de combustible
* Aider à la prise de décision

---

## 🧠 Technologies utilisées

* **Python**
* **Streamlit**
* **Pandas**
* **Plotly**
* **Scikit-learn**

---

## 🏗️ Architecture du projet

```
├── app.py
├── modules/
│   ├── module1_data.py
│   ├── module2_diagnostic.py
│   ├── module3_prediction.py
│   ├── module4_optimisation.py
│   └── module5_dashboard.py
├── data/
├── requirements.txt
└── README.md
```

---

## ⚙️ Fonctionnalités

### 🔹 Module 1 — Gestion des données

* Import Excel
* Vérification des colonnes
* Nettoyage des données
* Analyse qualité

### 🔹 Module 2 — Diagnostic énergétique

* Calcul du rendement
* Consommation spécifique
* Détection d’anomalies

### 🔹 Module 3 — Prédiction ML

* Régression linéaire
* Random Forest
* Comparaison des modèles

### 🔹 Module 4 — Optimisation

* Simulation des charges
* Détection de charge optimale
* Estimation des économies

### 🔹 Module 5 — Dashboard

* KPIs en temps réel
* Visualisations interactives
* Alertes intelligentes

---

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/ton-username/smart-energy-diagnostic-steg.git

# Accéder au dossier
cd smart-energy-diagnostic-steg

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

---

## 📊 Données attendues

Le fichier Excel doit contenir les colonnes suivantes :

* Date
* Puissance_MW
* Débit_Combustible_Nm3h
* Temp_Vapeur_C
* Pression_Vapeur_bar
* Temp_Condenseur_C
* Charge_%

---

## 📈 Résultats

L'application permet :

* Une visualisation claire des performances
* Une détection automatique des anomalies
* Une recommandation de fonctionnement optimal
* Une estimation des économies énergétiques

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre d’un PFE (Projet de Fin d’Études) en informatique.

---

## 📜 Licence

Ce projet est destiné à un usage académique et éducatif.

---
