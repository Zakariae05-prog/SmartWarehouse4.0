import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Lean Production Monitoring",
    page_icon="🏭",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .kpi-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f5f5;
        text-align: center;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: bold;
    }

    .kpi-label {
        font-size: 15px;
        color: #666;
    }

    .alert-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffe6e6;
        border-left: 5px solid #ff0000;
    }

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #e6ffe6;
        border-left: 5px solid #00aa00;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "production_data" not in st.session_state:

    st.session_state.production_data = pd.DataFrame(
        columns=[
            "Date",
            "Reference",
            "Production",
            "Production_OK",
            "Production_NOK",
            "Temps_planifie",
            "Temps_arret",
            "Cycle_Time",
            "Takt_Time",
            "Temps_changement",
            "Deplacement",
            "Cause"
        ]
    )

if "smed_data" not in st.session_state:

    st.session_state.smed_data = pd.DataFrame(
        columns=[
            "Date",
            "Reference",
            "Temps_avant",
            "Temps_apres"
        ]
    )


# ============================================================
# CALCULS KPI
# ============================================================

def calcul_kpi(df):

    if len(df) == 0:
        return {
            "production": 0,
            "qualite": 0,
            "disponibilite": 0,
            "performance": 0,
            "trs": 0,
            "productivite": 0,
            "cycle": 0,
            "takt": 0,
            "arret": 0,
            "deplacement": 0
        }

    production = df["Production"].sum()
    production_ok = df["Production_OK"].sum()

    temps_planifie = df["Temps_planifie"].sum()
    temps_arret = df["Temps_arret"].sum()

    # Qualité
    if production > 0:
        qualite = production_ok / production * 100
    else:
        qualite = 0

    # Disponibilité
    if temps_planifie > 0:
        disponibilite = (
            (temps_planifie - temps_arret)
            / temps_planifie
            * 100
        )
    else:
        disponibilite = 0

    # Performance basée sur cycle/takt
    cycle = df["Cycle_Time"].mean()
    takt = df["Takt_Time"].mean()

    if cycle > 0:
        performance = min(takt / cycle * 100, 100)
    else:
        performance = 0

    trs = (
        disponibilite
        * performance
        * qualite
        / 10000
    )

    # Productivité
    if temps_planifie > 0:
        productivite = (
            production_ok
            / (temps_planifie / 60)
        )
    else:
        productivite = 0

    return {
        "production": production,
        "qualite": qualite,
        "disponibilite": disponibilite,
        "performance": performance,
        "trs": trs,
        "productivite": productivite,
        "cycle": cycle,
        "takt": takt,
        "arret": temps_arret,
        "deplacement": df["Deplacement"].sum()
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏭 Lean Production")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📥 Saisie des données",
        "🚨 Analyse des pertes",
        "🔧 SMED",
        "📈 Avant / Après"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Application de pilotage de la performance "
    "d'une ligne de production."
)


# ============================================================
# PAGE 1 : DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">🏭 Lean Production Monitoring</div>',
        unsafe_allow_html=True
    )

    df = st.session_state.production_data

    kpi = calcul_kpi(df)

    if len(df) == 0:

        st.warning(
            "⚠️ Aucune donnée disponible. "
            "Commencez par la page 'Saisie des données'."
        )

    else:

        # ---------------- KPI ----------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "TRS / OEE",
                f"{kpi['trs']:.1f}%"
            )

        with c2:
            st.metric(
                "Productivité",
                f"{kpi['productivite']:.1f} pièces/h"
            )

        with c3:
            st.metric(
                "Cycle Time",
                f"{kpi['cycle']:.1f} s"
            )

        with c4:
            st.metric(
                "Takt Time",
                f"{kpi['takt']:.1f} s"
            )

        st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Production",
                f"{kpi['production']:.0f}"
            )

        with c2:
            st.metric(
                "Qualité",
                f"{kpi['qualite']:.1f}%"
            )

        with c3:
            st.metric(
                "Temps d'arrêt",
                f"{kpi['arret']:.1f} min"
            )

        with c4:
            st.metric(
                "Déplacements",
                f"{kpi['deplacement']:.1f} min"
            )

        # ---------------- ALERTES ----------------

        st.subheader("🚨 État de la ligne")

        if kpi["cycle"] > kpi["takt"]:

            st.error(
                f"🔴 ALERTE : Cycle Time "
                f"({kpi['cycle']:.1f}s) > "
                f"Takt Time ({kpi['takt']:.1f}s)"
            )

        else:

            st.success(
                f"🟢 Cycle Time ({kpi['cycle']:.1f}s) "
                f"≤ Takt Time ({kpi['takt']:.1f}s)"
            )

        # ---------------- GRAPHIQUES ----------------

        st.subheader("📊 Évolution de la production")

        daily = (
            df.groupby("Date")["Production"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            daily,
            x="Date",
            y="Production",
            title="Production par jour"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------- DONNEES ----------------

        st.subheader("📋 Données")

        st.dataframe(
            df,
            use_container_width=True
        )


# ============================================================
# PAGE 2 : SAISIE
# ============================================================

elif page == "📥 Saisie des données":

    st.title("📥 Saisie des données de production")

    with st.form("production_form"):

        c1, c2, c3 = st.columns(3)

        with c1:

            d = st.date_input(
                "Date",
                value=date.today()
            )

            reference = st.text_input(
                "Référence produit"
            )

            production = st.number_input(
                "Production totale",
                min_value=0,
                step=1
            )

        with c2:

            production_ok = st.number_input(
                "Production OK",
                min_value=0,
                step=1
            )

            production_nok = st.number_input(
                "Production NOK",
                min_value=0,
                step=1
            )

            temps_planifie = st.number_input(
                "Temps planifié (min)",
                min_value=0.0,
                step=1.0
            )

        with c3:

            temps_arret = st.number_input(
                "Temps d'arrêt (min)",
                min_value=0.0,
                step=1.0
            )

            cycle_time = st.number_input(
                "Cycle Time (s)",
                min_value=0.0,
                step=0.1
            )

            takt_time = st.number_input(
                "Takt Time (s)",
                min_value=0.0,
                step=0.1
            )

        c1, c2, c3 = st.columns(3)

        with c1:

            temps_changement = st.number_input(
                "Temps changement série (min)",
                min_value=0.0,
                step=1.0
            )

        with c2:

            deplacement = st.number_input(
                "Temps déplacement (min)",
                min_value=0.0,
                step=1.0
            )

        with c3:

            cause = st.selectbox(
                "Cause principale",
                [
                    "Aucune",
                    "Attente matière",
                    "Panne machine",
                    "Réglage",
                    "Déplacement",
                    "Défaut qualité",
                    "Manque opérateur",
                    "Autre"
                ]
            )

        submitted = st.form_submit_button(
            "➕ Ajouter les données"
        )

    if submitted:

        new_data = pd.DataFrame(
            [{
                "Date": d,
                "Reference": reference,
                "Production": production,
                "Production_OK": production_ok,
                "Production_NOK": production_nok,
                "Temps_planifie": temps_planifie,
                "Temps_arret": temps_arret,
                "Cycle_Time": cycle_time,
                "Takt_Time": takt_time,
                "Temps_changement": temps_changement,
                "Deplacement": deplacement,
                "Cause": cause
            }]
        )

        st.session_state.production_data = pd.concat(
            [
                st.session_state.production_data,
                new_data
            ],
            ignore_index=True
        )

        st.success("✅ Données ajoutées avec succès !")

    st.subheader("📋 Historique")

    st.dataframe(
        st.session_state.production_data,
        use_container_width=True
    )


# ============================================================
# PAGE 3 : ANALYSE DES PERTES
# ============================================================

elif page == "🚨 Analyse des pertes":

    st.title("🚨 Analyse des pertes de production")

    df = st.session_state.production_data

    if len(df) == 0:

        st.warning("Aucune donnée disponible.")

    else:

        # ---------------- PARETO ----------------

        losses = (
            df.groupby("Cause")["Temps_arret"]
            .sum()
            .reset_index()
            .sort_values(
                "Temps_arret",
                ascending=False
            )
        )

        st.subheader("📊 Pareto des causes d'arrêt")

        fig = px.bar(
            losses,
            x="Cause",
            y="Temps_arret",
            title="Temps perdu par cause"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------- TOP CAUSE ----------------

        if len(losses) > 0:

            top_cause = losses.iloc[0]["Cause"]
            top_time = losses.iloc[0]["Temps_arret"]

            st.error(
                f"🔴 Cause principale : {top_cause} "
                f"→ {top_time:.1f} minutes perdues"
            )

            # ---------------- RECOMMANDATION ----------------

            recommendations = {

                "Attente matière":
                    "Rapprocher le stock du poste et mettre en place un système de réapprovisionnement.",

                "Panne machine":
                    "Renforcer la maintenance préventive et analyser les causes de panne.",

                "Réglage":
                    "Appliquer la démarche SMED pour réduire le temps de changement.",

                "Déplacement":
                    "Revoir l'implantation du poste et appliquer les principes 5S.",

                "Défaut qualité":
                    "Analyser les causes avec Ishikawa et mettre en place un contrôle au poste.",

                "Manque opérateur":
                    "Rééquilibrer les postes et vérifier la charge de travail.",

                "Autre":
                    "Effectuer une analyse détaillée de la cause."
            }

            recommendation = recommendations.get(
                top_cause,
                "Analyser la cause."
            )

            st.info(
                f"💡 **Action recommandée :** {recommendation}"
            )

        # ---------------- DONNEES ----------------

        st.subheader("📋 Détail des pertes")

        st.dataframe(
            losses,
            use_container_width=True
        )


# ============================================================
# PAGE 4 : SMED
# ============================================================

elif page == "🔧 SMED":

    st.title("🔧 Analyse SMED")

    st.write(
        "Comparez le temps de changement de série "
        "avant et après amélioration."
    )

    with st.form("smed_form"):

        d = st.date_input(
            "Date",
            value=date.today()
        )

        reference = st.text_input(
            "Référence"
        )

        avant = st.number_input(
            "Temps avant SMED (min)",
            min_value=0.0,
            step=1.0
        )

        apres = st.number_input(
            "Temps après SMED (min)",
            min_value=0.0,
            step=1.0
        )

        submitted = st.form_submit_button(
            "Ajouter"
        )

    if submitted:

        new_smed = pd.DataFrame(
            [{
                "Date": d,
                "Reference": reference,
                "Temps_avant": avant,
                "Temps_apres": apres
            }]
        )

        st.session_state.smed_data = pd.concat(
            [
                st.session_state.smed_data,
                new_smed
            ],
            ignore_index=True
        )

        st.success("Données SMED ajoutées.")

    smed = st.session_state.smed_data

    if len(smed) > 0:

        smed["Gain_%"] = (
            (
                smed["Temps_avant"]
                - smed["Temps_apres"]
            )
            / smed["Temps_avant"]
            * 100
        )

        gain_moyen = smed["Gain_%"].mean()

        st.metric(
            "Gain moyen SMED",
            f"{gain_moyen:.1f}%"
        )

        fig = px.bar(
            smed,
            x="Reference",
            y=["Temps_avant", "Temps_apres"],
            barmode="group",
            title="Avant / Après SMED"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            smed,
            use_container_width=True
        )


# ============================================================
# PAGE 5 : AVANT / APRES
# ============================================================

elif page == "📈 Avant / Après":

    st.title("📈 Comparaison avant / après amélioration")

    st.subheader("Entrer les performances")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### 🔴 Avant amélioration")

        trs_avant = st.number_input(
            "TRS avant (%)",
            min_value=0.0,
            max_value=100.0,
            value=75.0
        )

        prod_avant = st.number_input(
            "Productivité avant (pièces/h)",
            min_value=0.0,
            value=80.0
        )

        cycle_avant = st.number_input(
            "Cycle Time avant (s)",
            min_value=0.0,
            value=52.0
        )

        arret_avant = st.number_input(
            "Temps d'arrêt avant (min)",
            min_value=0.0,
            value=60.0
        )

    with c2:

        st.markdown("### 🟢 Après amélioration")

        trs_apres = st.number_input(
            "TRS après (%)",
            min_value=0.0,
            max_value=100.0,
            value=87.0
        )

        prod_apres = st.number_input(
            "Productivité après (pièces/h)",
            min_value=0.0,
            value=95.0
        )

        cycle_apres = st.number_input(
            "Cycle Time après (s)",
            min_value=0.0,
            value=45.0
        )

        arret_apres = st.number_input(
            "Temps d'arrêt après (min)",
            min_value=0.0,
            value=35.0
        )

    # ---------------- GAINS ----------------

    st.markdown("---")

    def gain_positif(avant, apres):

        if avant == 0:
            return 0

        return (apres - avant) / avant * 100

    gain_trs = gain_positif(
        trs_avant,
        trs_apres
    )

    gain_prod = gain_positif(
        prod_avant,
        prod_apres
    )

    gain_cycle = (
        (cycle_avant - cycle_apres)
        / cycle_avant
        * 100
        if cycle_avant > 0 else 0
    )

    gain_arret = (
        (arret_avant - arret_apres)
        / arret_avant
        * 100
        if arret_avant > 0 else 0
    )

    st.subheader("📊 Résultats")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Gain TRS",
            f"{gain_trs:.1f}%"
        )

    with c2:
        st.metric(
            "Gain productivité",
            f"{gain_prod:.1f}%"
        )

    with c3:
        st.metric(
            "Réduction Cycle Time",
            f"{gain_cycle:.1f}%"
        )

    with c4:
        st.metric(
            "Réduction arrêts",
            f"{gain_arret:.1f}%"
        )

    # ---------------- GRAPHIQUE ----------------

    comparison = pd.DataFrame({

        "KPI": [
            "TRS",
            "Productivité",
            "Cycle Time",
            "Temps d'arrêt"
        ],

        "Avant": [
            trs_avant,
            prod_avant,
            cycle_avant,
            arret_avant
        ],

        "Après": [
            trs_apres,
            prod_apres,
            cycle_apres,
            arret_apres
        ]
    })

    fig = px.bar(
        comparison,
        x="KPI",
        y=["Avant", "Après"],
        barmode="group",
        title="Performance avant / après"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.success(
        "🎯 L'objectif est de vérifier que les actions "
        "Lean produisent une amélioration mesurable."
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")
st.sidebar.caption(
    "Lean Production Monitoring System | PFA"
)
