# =============================================================
# APP PRINCIPALE - Streamlit
# Système Intelligent de Diagnostic Énergétique
# Centrale Thermique de La Goulette - STEG
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.module1_data import (
    charger_fichier, verifier_colonnes, analyser_qualite,
    nettoyer_donnees, get_statistiques, verifier_plages,
    COLONNES_ATTENDUES, PLAGES_NORMALES
)

# ==============================================================
# CONFIGURATION DE LA PAGE
# ==============================================================
st.set_page_config(
    page_title="Centrale Goulette - STEG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================
# CSS PERSONNALISE
# ==============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1B2A 0%, #1F4E79 100%); }
    [data-testid="stSidebar"] * { color: #E8F4FD !important; }

    .main-title { font-size:2rem; font-weight:700; color:#1F4E79; border-bottom:3px solid #2E75B6; padding-bottom:8px; margin-bottom:20px; }
    .kpi-card { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:12px; padding:18px 22px; color:white; text-align:center; margin-bottom:10px; }
    .kpi-card .kpi-value { font-size:2rem; font-weight:700; }
    .kpi-card .kpi-label { font-size:0.85rem; opacity:0.85; margin-top:4px; }

    .alerte-rouge  { background:#FFEBEE; border-left:5px solid #C62828; padding:12px 16px; border-radius:6px; margin:8px 0; color:#B71C1C; font-weight:600; }
    .alerte-verte  { background:#E8F5E9; border-left:5px solid #2E7D32; padding:12px 16px; border-radius:6px; margin:8px 0; color:#1B5E20; font-weight:600; }
    .alerte-orange { background:#FFF8E1; border-left:5px solid #F57F17; padding:12px 16px; border-radius:6px; margin:8px 0; color:#E65100; font-weight:600; }
    .alerte-bleue  { background:#E3F2FD; border-left:5px solid #1565C0; padding:12px 16px; border-radius:6px; margin:8px 0; color:#0D47A1; font-weight:600; }

    .stButton > button { background:linear-gradient(135deg,#1F4E79,#2E75B6); color:white; border:none; border-radius:8px; padding:10px 24px; font-weight:600; }
    .stButton > button:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(30,78,121,0.35); }
</style>
""", unsafe_allow_html=True)

# ==============================================================
# SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown("## STEG — La Goulette")
    st.markdown("**Système Intelligent de Diagnostic Énergétique**")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        options=[
            "Accueil",
            "Module 1 — Données",
            "Module 2 — Diagnostic",
            "Module 3 — Prédiction ML",
            "Module 4 — Optimisation",
            "Module 5 — Dashboard",
            "Module 6 — Discussion IA",
        ],
        index=0,
        key="navigation"
    )
    st.markdown("---")
    st.markdown("**Version** : 1.0.0")
    st.markdown("**PCI Gaz** : 34.4 MJ/Nm³")

# ==============================================================
# ACCUEIL
# ==============================================================
if page == "Accueil":
    st.markdown('<div class="main-title">Bienvenue sur le Système de Diagnostic Énergétique</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="kpi-card"><div class="kpi-value">6</div><div class="kpi-label">Modules disponibles</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="kpi-card"><div class="kpi-value">180 MW</div><div class="kpi-label">Capacité nominale</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="kpi-card"><div class="kpi-value">~38%</div><div class="kpi-label">Rendement nominal</div></div>', unsafe_allow_html=True)
    st.markdown("""
    ### Description des modules
    | Module | Fonction |
    |--------|----------|
    | **Module 1** | Import Excel, nettoyage, vérification |
    | **Module 2** | Calcul rendement, détection anomalies |
    | **Module 3** | Prédiction ML (Random Forest + Régression) |
    | **Module 4** | Optimisation de la charge |
    | **Module 5** | Tableau de bord complet |
    | **Module 6** | Discussion IA — Diagnostic prédictif |

    Commencez par le Module 1.
    """)

# ==============================================================
# MODULE 1
# ==============================================================
elif page == "Module 1 — Données":
    st.markdown('<div class="main-title">Module 1 — Gestion des Données</div>', unsafe_allow_html=True)

    st.markdown("### Etape 1 — Importer le fichier Excel")
    fichier = st.file_uploader("Glissez-déposez votre fichier Excel ici", type=["xlsx", "xls"])

    if fichier is None:
        st.markdown('<div class="alerte-bleue">Colonnes attendues : Date · Puissance_MW · Débit_Combustible_Nm3h · Temp_Vapeur_C · Pression_Vapeur_bar · Temp_Condenseur_C · Charge_%</div>', unsafe_allow_html=True)
        if st.session_state.get('df_pret'):
            df_propre = st.session_state['df']
            st.markdown("---")
            st.markdown("### Etape 5 — Aperçu (données déjà chargées)")
            st.markdown('<div class="alerte-verte">Données déjà chargées. Passez au Module 2.</div>', unsafe_allow_html=True)
        st.stop()

    df_brut, msg = charger_fichier(fichier)
    if df_brut is None:
        st.error(msg)
        st.stop()
    st.success(msg)

    st.markdown("---")
    st.markdown("### Etape 2 — Vérification des colonnes")
    valide, manquantes, en_trop = verifier_colonnes(df_brut)
    col1, col2 = st.columns(2)
    with col1:
        if valide:
            st.markdown('<div class="alerte-verte">Toutes les colonnes présentes !</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alerte-rouge">Manquantes : {", ".join(manquantes)}</div>', unsafe_allow_html=True)
            st.stop()
    with col2:
        if en_trop:
            st.markdown(f'<div class="alerte-orange">Colonnes ignorées : {", ".join(en_trop)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alerte-verte">Aucune colonne inattendue</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Etape 3 — Rapport de qualité")
    rapport = analyser_qualite(df_brut)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Lignes",     rapport['nb_lignes'])
    with col2: st.metric("Manquantes", rapport['total_manquantes'])
    with col3: st.metric("Outliers",   rapport['total_outliers'])
    with col4: st.metric("Doublons",   rapport['doublons'])

    with st.expander("Détail valeurs manquantes"):
        df_m = pd.DataFrame.from_dict(rapport['valeurs_manquantes'], orient='index', columns=['Nb'])
        df_m['%'] = (df_m['Nb'] / rapport['nb_lignes'] * 100).round(2)
        st.dataframe(df_m, use_container_width=True)
    with st.expander("Détail outliers"):
        st.dataframe(pd.DataFrame.from_dict(rapport['outliers'], orient='index', columns=['Nb outliers']), use_container_width=True)

    st.markdown("---")
    st.markdown("### Etape 4 — Nettoyage")
    col1, col2 = st.columns(2)
    with col1: opt_outliers   = st.checkbox("Supprimer les outliers (IQR)", value=True)
    with col2: opt_normaliser = st.checkbox("Normaliser (Min-Max)", value=False)

    if st.button("Lancer le nettoyage"):
        df_propre, stats = nettoyer_donnees(df_brut, supprimer_outliers=opt_outliers, normaliser=opt_normaliser)
        st.session_state['df'] = df_propre
        st.session_state['df_pret'] = True

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Initial",    stats['lignes_initiales'])
        with col2: st.metric("Manquantes", stats['manquantes_supprimees'], delta=f"-{stats['manquantes_supprimees']}", delta_color="inverse")
        with col3: st.metric("Outliers",   stats['outliers_supprimes'],   delta=f"-{stats['outliers_supprimes']}",   delta_color="inverse")
        with col4: st.metric("Final",      stats['lignes_finales'])

        pct = round(stats['lignes_finales'] / stats['lignes_initiales'] * 100, 1)
        cls = "alerte-verte" if pct >= 90 else "alerte-orange"
        st.markdown(f'<div class="{cls}">{pct}% des lignes conservées</div>', unsafe_allow_html=True)

    if st.session_state.get('df_pret'):
        df_propre = st.session_state['df']
        st.markdown("---")
        st.markdown("### Etape 5 — Aperçu")
        tab1, tab2, tab3 = st.tabs(["Tableau", "Statistiques", "Graphiques"])
        with tab1:
            st.dataframe(df_propre, use_container_width=True, height=350)
            st.download_button("Télécharger (CSV)", data=df_propre.to_csv(index=False, encoding='utf-8-sig'), file_name="donnees_propres.csv", mime="text/csv")
        with tab2:
            st.dataframe(get_statistiques(df_propre), use_container_width=True)
            for al in verifier_plages(df_propre):
                st.markdown(f'<div class="alerte-orange"><b>{al["colonne"]}</b> : {al["nb_hors_plage"]} valeurs hors [{al["plage_normale"]}]</div>', unsafe_allow_html=True)
        with tab3:
            col_g = st.selectbox("Paramètre :", [c for c in PLAGES_NORMALES if c in df_propre.columns], key="sel_g1")
            if 'Date' in df_propre.columns:
                fig = px.line(df_propre, x='Date', y=col_g, color_discrete_sequence=["#2E75B6"])
                mn, mx = PLAGES_NORMALES.get(col_g, (None, None))
                if mn: fig.add_hline(y=mn, line_dash="dash", line_color="orange", annotation_text="Min")
                if mx: fig.add_hline(y=mx, line_dash="dash", line_color="red",    annotation_text="Max")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="alerte-verte">Module 1 terminé ! Passez au Module 2.</div>', unsafe_allow_html=True)

# ==============================================================
# MODULE 2
# ==============================================================
elif page == "Module 2 — Diagnostic":
    st.markdown('<div class="main-title">Module 2 — Diagnostic Énergétique</div>', unsafe_allow_html=True)

    if not st.session_state.get('df_pret'):
        st.markdown('<div class="alerte-orange">Veuillez d\'abord importer vos données dans le Module 1.</div>', unsafe_allow_html=True)
        st.stop()

    from modules.module2_diagnostic import calculer_rendement, calculer_consommation_specifique, detecter_anomalies, get_etat_systeme

    df = st.session_state['df'].copy()
    df = calculer_rendement(df)
    df = calculer_consommation_specifique(df)
    df, resume_anomalies = detecter_anomalies(df)
    etat, message, couleur = get_etat_systeme(df)

    st.markdown("### Etat Global")
    css = {'green':'alerte-verte','orange':'alerte-orange','red':'alerte-rouge'}.get(couleur,'alerte-bleue')
    st.markdown(f'<div class="{css}">{message}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Puissance",        f"{df['Puissance_MW'].mean():.1f} MW")
    with col2: st.metric("Rendement",         f"{df['Rendement_%'].mean():.1f} %")
    with col3: st.metric("Conso. spécifique", f"{df['Conso_Specifique_Nm3MWh'].mean():.0f} Nm³/MWh")
    with col4:
        nb_a = (df['Anomalie'] != 'Normal').sum()
        st.metric("Anomalies", nb_a)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Rendement", "Anomalies", "Données"])
    with tab1:
        fig1 = px.line(df, x='Date', y='Rendement_%', title="Rendement Thermique (%)", color_discrete_sequence=["#2E75B6"])
        fig1.add_hline(y=30, line_dash="dash", line_color="red",    annotation_text="Critique 30%")
        fig1.add_hline(y=35, line_dash="dash", line_color="orange", annotation_text="Alerte 35%")
        fig1.add_hline(y=df['Rendement_%'].mean(), line_dash="dot", line_color="green", annotation_text=f"Moy {df['Rendement_%'].mean():.1f}%")
        fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)
        fig2 = px.line(df, x='Date', y='Conso_Specifique_Nm3MWh', title="Consommation Spécifique", color_discrete_sequence=["#C55A11"])
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)
    with tab2:
        if len(resume_anomalies) == 0:
            st.markdown('<div class="alerte-verte">Aucune anomalie.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alerte-orange">{nb_a} anomalies ({nb_a/len(df)*100:.1f}%)</div>', unsafe_allow_html=True)
            st.dataframe(resume_anomalies, use_container_width=True)
            fig3 = px.pie(resume_anomalies, names='Type anomalie', values='Nombre', color_discrete_sequence=["#C62828","#F57F17","#1565C0","#2E7D32"])
            st.plotly_chart(fig3, use_container_width=True)
            with st.expander("Voir lignes anormales"):
                st.dataframe(df[df['Anomalie']!='Normal'][['Date','Puissance_MW','Rendement_%','Charge_%','Temp_Vapeur_C','Anomalie']], use_container_width=True)
    with tab3:
        st.dataframe(df[['Date','Puissance_MW','Charge_%','Rendement_%','Conso_Specifique_Nm3MWh','Anomalie']], use_container_width=True, height=400)

    st.session_state['df'] = df
    st.session_state['df_diagnostic_pret'] = True
    st.markdown('<div class="alerte-verte">Module 2 terminé ! Passez au Module 3.</div>', unsafe_allow_html=True)

# ==============================================================
# MODULE 3
# ==============================================================
elif page == "Module 3 — Prédiction ML":
    st.markdown('<div class="main-title">Module 3 — Prédiction ML</div>', unsafe_allow_html=True)

    if not st.session_state.get('df_pret'):
        st.markdown('<div class="alerte-orange">Veuillez d\'abord importer vos données dans le Module 1.</div>', unsafe_allow_html=True)
        st.stop()

    from modules.module3_prediction import preparer_donnees, entrainer_modeles, evaluer_modeles, meilleur_modele, predire_manuel, importance_features

    df = st.session_state['df'].copy()

    st.markdown("### Entrainement")
    with st.spinner("En cours..."):
        X_train, X_test, y_train, y_test = preparer_donnees(df)
        modeles   = entrainer_modeles(X_train, y_train)
        resultats = evaluer_modeles(modeles, X_test, y_test)
        meilleur  = meilleur_modele(resultats)

    st.markdown(f'<div class="alerte-verte">Entraîné sur <b>{len(X_train)}</b> lignes — Testé sur <b>{len(X_test)}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Comparaison")
    col1, col2 = st.columns(2)
    for i, (nom, res) in enumerate(resultats.items()):
        with (col1 if i == 0 else col2):
            bg = "#E8F5E9" if nom == meilleur else "#F5F5F5"
            bd = "#2E7D32" if nom == meilleur else "#CCCCCC"
            st.markdown(f'<div style="background:{bg};border-radius:10px;padding:18px;border:2px solid {bd}"><h4 style="margin:0 0 8px 0">{res["label"]} {"[Meilleur]" if nom==meilleur else ""}</h4><p style="font-size:1.4rem;font-weight:700;color:#1F4E79;margin:0">R² = {res["r2"]}</p><p style="color:#555;margin:4px 0 0 0">MAE = {res["mae"]} MW</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Réelles vs Prédites", "Importance", "Prédiction manuelle"])
    with tab1:
        mc = st.selectbox("Modèle :", list(resultats.keys()), format_func=lambda k: resultats[k]['label'], key="sel_mod")
        res = resultats[mc]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=res['y_test'], y=res['y_pred'], mode='markers', marker=dict(color='#2E75B6', size=6, opacity=0.6)))
        mn, mx = float(min(res['y_test'])), float(max(res['y_test']))
        fig.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx], mode='lines', line=dict(color='red', dash='dash')))
        fig.update_layout(xaxis_title="Réelles (MW)", yaxis_title="Prédites (MW)", plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        imp = importance_features(modeles)
        if imp is not None:
            fig2 = px.bar(imp, x='Importance', y='Feature', orientation='h', color='Importance', color_continuous_scale='Blues')
            fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
            for _, row in imp.iterrows():
                st.markdown(f"- **{row['Feature']}** : **{round(row['Importance']*100,1)}%**")
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1: c_in = st.slider("Charge (%)",           30,    100,   75,    key="c_pred")
        with col2: t_in = st.slider("Temp. vapeur (°C)",    450,   580,   520,   key="t_pred")
        with col3: d_in = st.slider("Débit (Nm³/h)",        10000, 60000, 35000, 500, key="d_pred")
        if st.button("Prédire", key="btn_pred"):
            preds = predire_manuel(modeles, c_in, t_in, d_in)
            col1, col2 = st.columns(2)
            with col1: st.markdown(f'<div class="kpi-card"><div class="kpi-value">{preds["regression"]} MW</div><div class="kpi-label">Régression Linéaire</div></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="kpi-card"><div class="kpi-value">{preds["random_forest"]} MW</div><div class="kpi-label">Random Forest [Meilleur]</div></div>', unsafe_allow_html=True)

    st.session_state['modeles']    = modeles
    st.session_state['resultats']  = resultats
    st.session_state['df_ml_pret'] = True
    st.markdown('<div class="alerte-verte">Module 3 terminé ! Passez au Module 4.</div>', unsafe_allow_html=True)

# ==============================================================
# MODULE 4
# ==============================================================
elif page == "Module 4 — Optimisation":
    st.markdown('<div class="main-title">Module 4 — Optimisation</div>', unsafe_allow_html=True)

    if not st.session_state.get('df_pret'):
        st.markdown('<div class="alerte-orange">Veuillez d\'abord importer vos données dans le Module 1.</div>', unsafe_allow_html=True)
        st.stop()

    from modules.module4_optimisation import simuler_charges, get_charge_optimale, generer_recommandation, estimer_economies

    df = st.session_state['df'].copy()

    st.markdown("### Simulation par niveau de charge")
    st.markdown("Comparaison des performances pour 4 niveaux de charge : **40% · 60% · 80% · 90%**")

    with st.spinner("Simulation en cours..."):
        resultats      = simuler_charges(df)
        charge_opt     = get_charge_optimale(resultats)
        recommandation = generer_recommandation(charge_opt, resultats)
        economies      = estimer_economies(resultats)

    st.markdown("---")
    st.markdown("### Recommandation")
    st.markdown(f'<div class="alerte-verte">{recommandation}</div>', unsafe_allow_html=True)

    if charge_opt is not None:
        st.markdown("---")
        st.markdown("### Indicateurs à la charge optimale")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Charge optimale",  f"{charge_opt['Charge_%']} %")
        with col2: st.metric("Puissance",         f"{charge_opt['Puissance_MW']} MW")
        with col3: st.metric("Rendement",         f"{charge_opt['Rendement_%']} %")
        with col4: st.metric("Conso. spécifique", f"{charge_opt['Conso_Specifique']} Nm³/MWh")

    if economies:
        st.markdown("---")
        st.markdown("### Économies annuelles estimées (vs pire configuration)")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Économie spécifique", f"{economies['diff_conso_spec']} Nm³/MWh")
        with col2: st.metric("Économie gaz/an",     f"{economies['eco_nm3']:,.0f} Nm³")
        with col3: st.metric("Économie financière", f"{economies['eco_dt']:,.0f} DT/an")

    st.markdown("---")
    st.markdown("### Tableau comparatif des scénarios")
    for i, row in resultats.iterrows():
        is_opt = (row['Charge_%'] == charge_opt['Charge_%']) if charge_opt is not None else False
        bg     = "#E8F5E9" if is_opt else ("#FFF8F0" if i % 2 == 0 else "#F9F9F9")
        border = "2px solid #2E7D32" if is_opt else "1px solid #EEEEEE"
        badge  = " [OPTIMAL]" if is_opt else ""
        st.markdown(f"""
        <div style="background:{bg}; border:{border}; border-radius:8px; padding:14px 20px; margin:6px 0; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.1rem; color:#1F4E79;">Charge {row['Charge_%']}%{badge}</span>
            <span><b>{row['Puissance_MW']} MW</b></span>
            <span>Rendement : <b>{row['Rendement_%']}%</b></span>
            <span>Conso : <b>{row['Conso_Specifique']} Nm³/MWh</b></span>
            <span style="color:#888;">({int(row['Nb_Points'])} points)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2 = st.tabs(["Rendement par charge", "Consommation spécifique"])
    with tab1:
        fig1 = px.bar(resultats, x='Charge_%', y='Rendement_%',
            title="Rendement thermique par niveau de charge",
            color='Rendement_%', color_continuous_scale='Blues', text='Rendement_%')
        if charge_opt is not None:
            fig1.add_vline(x=charge_opt['Charge_%'], line_dash="dash", line_color="green", annotation_text="Optimal")
        fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis_title="Charge (%)", yaxis_title="Rendement (%)")
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig2 = px.bar(resultats, x='Charge_%', y='Conso_Specifique',
            title="Consommation spécifique par niveau de charge",
            color='Conso_Specifique', color_continuous_scale='Reds_r', text='Conso_Specifique')
        fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis_title="Charge (%)", yaxis_title="Conso. spécifique (Nm³/MWh)")
        st.plotly_chart(fig2, use_container_width=True)

    st.session_state['df_optim_pret'] = True
    st.markdown('<div class="alerte-verte">Module 4 terminé ! Passez au Module 5 — Dashboard.</div>', unsafe_allow_html=True)

# ==============================================================
# MODULE 5
# ==============================================================
elif page == "Module 5 — Dashboard":
    st.markdown('<div class="main-title">Module 5 — Tableau de Bord</div>', unsafe_allow_html=True)

    if not st.session_state.get('df_pret'):
        st.markdown('<div class="alerte-orange">Veuillez d\'abord importer vos données dans le Module 1.</div>', unsafe_allow_html=True)
        st.stop()

    from modules.module2_diagnostic  import calculer_rendement, calculer_consommation_specifique, detecter_anomalies, get_etat_systeme
    from modules.module4_optimisation import simuler_charges, get_charge_optimale
    from modules.module5_dashboard    import calculer_kpis, generer_alertes, calculer_tendances

    df = st.session_state['df'].copy()
    if 'Rendement_%' not in df.columns:
        df = calculer_rendement(df)
        df = calculer_consommation_specifique(df)
        df, _ = detecter_anomalies(df)

    kpis      = calculer_kpis(df)
    alertes   = generer_alertes(kpis, df)
    tendances = calculer_tendances(df)
    etat, message_etat, couleur = get_etat_systeme(df)

    css = {'green':'alerte-verte','orange':'alerte-orange','red':'alerte-rouge'}.get(couleur,'alerte-bleue')
    st.markdown(f'<div class="{css}">{message_etat}</div>', unsafe_allow_html=True)
    st.markdown(f"*Période analysée : **{kpis['date_debut']}** → **{kpis['date_fin']}** ({kpis['nb_jours']} jours · {kpis['nb_mesures']} mesures)*")

    st.markdown("---")
    st.markdown("### Indicateurs en Temps Quasi Réel")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        delta_p = f"{tendances['puissance_delta']:+.1f} MW" if tendances else None
        st.metric("Puissance actuelle", f"{kpis['puissance_actuelle']} MW", delta=delta_p)
    with col2:
        delta_r = f"{tendances['rendement_delta']:+.2f} %" if tendances and 'rendement_delta' in tendances else None
        st.metric("Rendement actuel",   f"{kpis['rendement_actuel']} %",  delta=delta_r)
    with col3:
        delta_c = f"{tendances['conso_delta']:+.1f}" if tendances and 'conso_delta' in tendances else None
        st.metric("Conso. spécifique",  f"{kpis['conso_actuelle']} Nm³/MWh", delta=delta_c, delta_color="inverse")
    with col4:
        st.metric("Charge actuelle", f"{kpis['charge_actuelle']} %")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Puissance moy.", f"{kpis['puissance_moyenne']} MW")
    with col2: st.metric("Rendement moy.", f"{kpis['rendement_moyen']} %")
    with col3: st.metric("Conso. moy.",    f"{kpis['conso_moyenne']} Nm³/MWh")
    with col4: st.metric("Anomalies",      f"{kpis['nb_anomalies']} ({kpis['pct_anomalies']}%)")

    st.markdown("---")
    st.markdown("### Evolution Temporelle")
    tab1, tab2, tab3 = st.tabs(["Puissance & Charge", "Rendement", "Consommation"])

    with tab1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['Date'], y=df['Puissance_MW'], name='Puissance (MW)', line=dict(color='#2E75B6', width=1.5)))
        fig1.add_trace(go.Scatter(x=df['Date'], y=df['Charge_%'], name='Charge (%)', line=dict(color='#C55A11', width=1.5, dash='dot'), yaxis='y2'))
        fig1.update_layout(title="Puissance produite et Charge",
            yaxis=dict(title="Puissance (MW)", color='#2E75B6'),
            yaxis2=dict(title="Charge (%)", overlaying='y', side='right', color='#C55A11'),
            plot_bgcolor='white', paper_bgcolor='white', legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df['Date'], y=df['Rendement_%'], name='Rendement',
            fill='tozeroy', line=dict(color='#2E7D32', width=1.5), fillcolor='rgba(46,125,50,0.1)'))
        fig2.add_hline(y=30, line_dash="dash", line_color="red",    annotation_text="Critique 30%")
        fig2.add_hline(y=35, line_dash="dash", line_color="orange", annotation_text="Alerte 35%")
        fig2.add_hline(y=kpis['rendement_moyen'], line_dash="dot",  line_color="blue",
                       annotation_text=f"Moy {kpis['rendement_moyen']}%")
        fig2.update_layout(title="Rendement Thermique (%)", plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df['Date'], y=df['Conso_Specifique_Nm3MWh'], name='Conso spécifique',
            line=dict(color='#C55A11', width=1.5)))
        fig3.add_hline(y=kpis['conso_moyenne'], line_dash="dot", line_color="blue",
                       annotation_text=f"Moy {kpis['conso_moyenne']} Nm³/MWh")
        fig3.update_layout(title="Consommation Spécifique (Nm³/MWh)", plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("### Alertes & Recommandations")
    for al in alertes:
        css_map = {'critique':'alerte-rouge','alerte':'alerte-orange','ok':'alerte-verte','info':'alerte-bleue'}
        css_al = css_map.get(al['niveau'], 'alerte-bleue')
        st.markdown(f'<div class="{css_al}"><b>{al["titre"]}</b><br>{al["message"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Résumé Optimisation")
    resultats_opt = simuler_charges(df)
    charge_opt    = get_charge_optimale(resultats_opt)

    if charge_opt is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background:#E8F5E9; border-radius:10px; padding:20px; border:2px solid #2E7D32">
                <h4 style="margin:0 0 10px 0; color:#1B5E20">Charge Optimale Recommandée</h4>
                <p style="font-size:2.5rem; font-weight:700; color:#1F4E79; margin:0">{charge_opt['Charge_%']}%</p>
                <p style="margin:8px 0 0 0; color:#555">
                    Rendement : <b>{charge_opt['Rendement_%']}%</b><br>
                    Puissance : <b>{charge_opt['Puissance_MW']} MW</b><br>
                    Conso. spéc. : <b>{charge_opt['Conso_Specifique']} Nm³/MWh</b>
                </p>
            </div>""", unsafe_allow_html=True)
        with col2:
            fig4 = px.bar(resultats_opt, x='Charge_%', y='Rendement_%',
                title="Rendement par niveau de charge",
                color='Rendement_%', color_continuous_scale='Greens', text='Rendement_%')
            fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False,
                xaxis_title="Charge (%)", yaxis_title="Rendement (%)")
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="alerte-verte">Dashboard complet ! Tous les modules sont opérationnels.</div>', unsafe_allow_html=True)

# ==============================================================
# MODULE 6 — DISCUSSION IA
# ==============================================================
elif page == "Module 6 — Discussion IA":
    st.markdown('<div class="main-title">Module 6 — Discussion IA</div>', unsafe_allow_html=True)

    from modules.module6_discussion import (
        construire_system_prompt, appeler_api_claude, SUGGESTIONS
    )
    from modules.module2_diagnostic import (
        calculer_rendement, calculer_consommation_specifique, detecter_anomalies
    )

    # ── Enrichir df si disponible ─────────────────────────────────
    df_ctx = None
    if st.session_state.get('df_pret'):
        df_ctx = st.session_state['df'].copy()
        if 'Rendement_%' not in df_ctx.columns:
            df_ctx = calculer_rendement(df_ctx)
            df_ctx = calculer_consommation_specifique(df_ctx)
            df_ctx, _ = detecter_anomalies(df_ctx)

    # ── Bannière contexte ─────────────────────────────────────────
    if df_ctx is not None:
        nb_mes   = len(df_ctx)
        rend_moy = round(df_ctx['Rendement_%'].mean(), 1) if 'Rendement_%' in df_ctx.columns else "—"
        nb_ano   = int((df_ctx['Anomalie'] != 'Normal').sum()) if 'Anomalie' in df_ctx.columns else "—"
        st.markdown(
            f'<div class="alerte-verte">'
            f'Contexte chargé — <b>{nb_mes}</b> mesures · Rendement moy. <b>{rend_moy}%</b> · '
            f'<b>{nb_ano}</b> anomalies · L\'IA analyse vos données en temps réel.'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="alerte-bleue">'
            'Aucune donnée chargée — L\'IA répond en mode expert général. '
            'Importez un fichier dans le Module 1 pour des analyses personnalisées.'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Initialiser l'historique ───────────────────────────────────
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'chat_input_key' not in st.session_state:
        st.session_state['chat_input_key'] = 0

    # ── Suggestions ───────────────────────────────────────────────
    with st.expander("Questions suggérées", expanded=False):
        for bloc in SUGGESTIONS:
            st.markdown(f"**{bloc['categorie']}**")
            for idx, q in enumerate(bloc['questions']):
                btn_key = f"sug_{bloc['categorie']}_{idx}"
                label   = q[:90] + "…" if len(q) > 90 else q
                if st.button(label, key=btn_key, use_container_width=True):
                    st.session_state['question_suggeree'] = q
                    st.session_state['auto_envoyer'] = True
                    st.rerun()
            st.markdown("")

    st.markdown("---")
    st.markdown("### Conversation")

    # ── Affichage historique ───────────────────────────────────────
    if not st.session_state['chat_history']:
        st.markdown(
            '<div class="alerte-bleue">'
            'Bonjour — Assistant expert en diagnostic énergétique, Centrale de La Goulette.<br>'
            'Posez une question sur les performances, les anomalies, les pannes ou l\'optimisation.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state['chat_history']:
            if msg['role'] == 'user':
                st.markdown(
                    f'<div style="background:#EEF2F7; border-radius:10px 10px 2px 10px; '
                    f'padding:10px 16px; margin:6px 0 4px 80px; color:#1F4E79; font-size:0.95rem;">'
                    f'<span style="font-weight:600; font-size:0.75rem; text-transform:uppercase; '
                    f'letter-spacing:0.08em; opacity:0.6;">Vous</span><br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                content_html = msg['content'].replace('\n', '<br>')
                st.markdown(
                    f'<div style="background:#F7FAFF; border-left:3px solid #2E75B6; '
                    f'border-radius:0 10px 10px 0; padding:12px 18px; margin:4px 80px 6px 0; '
                    f'color:#0D1B2A; font-size:0.95rem; line-height:1.6;">'
                    f'<span style="font-weight:600; font-size:0.75rem; text-transform:uppercase; '
                    f'letter-spacing:0.08em; color:#2E75B6;">Assistant</span><br>{content_html}</div>',
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # ── Zone de saisie ────────────────────────────────────────────
    valeur_initiale = st.session_state.pop('question_suggeree', "")
    auto            = st.session_state.pop('auto_envoyer', False)

    col_input, col_btn, col_clear = st.columns([6, 1, 1])
    with col_input:
        user_input = st.text_input(
            "Votre question :",
            value=valeur_initiale,
            placeholder="Ex : Quelles sont les causes d'une chute de rendement ?",
            key=f"chat_input_{st.session_state['chat_input_key']}",
            label_visibility="collapsed"
        )
    with col_btn:
        envoyer = st.button("Envoyer", use_container_width=True, key="btn_envoyer")
    with col_clear:
        if st.button("Effacer", use_container_width=True, key="btn_clear"):
            st.session_state['chat_history'] = []
            st.session_state['chat_input_key'] += 1
            st.rerun()

    # ── Envoi et appel API ────────────────────────────────────────
    question_a_envoyer = None
    if auto and valeur_initiale.strip():
        question_a_envoyer = valeur_initiale.strip()
    elif envoyer and user_input.strip():
        question_a_envoyer = user_input.strip()

    if question_a_envoyer:
        st.session_state['chat_history'].append({"role": "user", "content": question_a_envoyer})
        system_prompt = construire_system_prompt(df_ctx)
        with st.spinner("Analyse en cours…"):
            reponse, statut = appeler_api_claude(
                historique=st.session_state['chat_history'],
                system_prompt=system_prompt
            )
        st.session_state['chat_history'].append({"role": "assistant", "content": reponse})
        st.session_state['chat_input_key'] += 1
        st.rerun()

    # ── Compteur ──────────────────────────────────────────────────
    if st.session_state['chat_history']:
        nb_tours = len(st.session_state['chat_history']) // 2
        st.markdown(
            f'<div style="text-align:right; color:#aaa; font-size:0.78rem; margin-top:8px;">'
            f'{nb_tours} échange(s) dans cette session</div>',
            unsafe_allow_html=True
        )