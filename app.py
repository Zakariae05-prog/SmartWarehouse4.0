import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="HDEP - Control DMAIC",
    page_icon="📊",
    layout="wide",
)

DATA_FILE = Path("hdep_control_data.csv")
ACTIONS_FILE = Path("hdep_actions.csv")

TAKT_TIME = 48.0
ASSEMBLY_BASELINE = 56.05
ASSEMBLY_S3 = 50.20
PUSHBACK_BASELINE = 52.11
PUSHBACK_TARGET = 35.81
SMED_BASELINE = 6.33
SMED_TARGET = 3.31
MOVEMENT_BASELINE = 837.51
PRODUCTION_TARGET_H = 75

POSTS = [
    "Twist 1",
    "Twist 2",
    "Splice 1",
    "Splice 2",
    "Assemblage écrous",
    "Insertion & Push-Back",
    "Assemblage P7",
    "Assemblage P8",
    "Assemblage P9",
    "Assemblage P10",
    "Assemblage P11",
    "Assemblage P12",
    "TEST EOL",
    "Contrôle / Packaging",
]

CAUSES = [
    "Attente matière",
    "Réglage / changement de série",
    "Problème machine",
    "Méthode de travail",
    "Formation opérateur",
    "Déplacement / transport",
    "Qualité / scrap",
    "Outil Push-Back",
    "Autre",
]

# ============================================================
# DATA
# ============================================================
def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame(columns=[
        "Date", "Production totale", "Production OK", "Production NOK",
        "Takt Time (s)", "CT Assemblage (s)", "CT Push-Back (s)",
        "SMED Komax (min)", "Temps attente (min)",
        "Distance Milk-Run (m/h)", "Cause principale", "Commentaire"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_actions():
    if ACTIONS_FILE.exists():
        return pd.read_csv(ACTIONS_FILE)
    return pd.DataFrame(columns=[
        "Date", "Problème", "Cause", "Action corrective",
        "Responsable", "Échéance", "Statut", "Efficacité"
    ])

def save_actions(df):
    df.to_csv(ACTIONS_FILE, index=False)

df = load_data()
actions = load_actions()

# ============================================================
# HELPERS
# ============================================================
def status_lower_is_better(value, target, orange_margin=0.10):
    if pd.isna(value):
        return "⚪"
    if value <= target:
        return "🟢"
    if value <= target * (1 + orange_margin):
        return "🟠"
    return "🔴"

def status_higher_is_better(value, target, orange_margin=0.10):
    if pd.isna(value):
        return "⚪"
    if value >= target:
        return "🟢"
    if value >= target * (1 - orange_margin):
        return "🟠"
    return "🔴"

def quality_rate(row):
    total = row["Production totale"]
    return (row["Production OK"] / total * 100) if total else 0

def global_status(last):
    checks = [
        last["CT Assemblage (s)"] <= TAKT_TIME,
        last["CT Push-Back (s)"] <= TAKT_TIME,
        last["SMED Komax (min)"] <= SMED_TARGET,
        last["Temps attente (min)"] <= 10,
        last["Production totale"] >= PRODUCTION_TARGET_H,
    ]
    if all(checks):
        return "🟢 STABLE"
    if sum(checks) >= 3:
        return "🟠 À SURVEILLER"
    return "🔴 ACTION REQUISE"

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("HDEP – DMAIC Control")
st.sidebar.caption("TE Connectivity | Ligne HDEP | Volvo")
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard Control",
        "📝 Saisie quotidienne",
        "📈 Suivi des KPI",
        "🚨 Alertes",
        "🔧 Plan d'actions",
        "🔄 Avant / Après",
        "📥 Données & export",
    ],
)

st.sidebar.divider()
st.sidebar.info(
    "Objectif de la phase Control : surveiller les performances "
    "et vérifier la pérennisation des améliorations."
)

# ============================================================
# 1. DASHBOARD
# ============================================================
if page == "📊 Dashboard Control":
    st.title("📊 Dashboard de Contrôle – Ligne HDEP")
    st.markdown(
        "### Pérennisation des améliorations – Phase **Control** de DMAIC"
    )

    if df.empty:
        st.warning("Aucune donnée quotidienne n'est encore saisie.")
        st.info("Commencez par la page « Saisie quotidienne ».")
        st.stop()

    last = df.sort_values("Date").iloc[-1]

    st.subheader("Situation du dernier relevé")
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Production",
        f'{last["Production totale"]:.0f}',
        f"cible {PRODUCTION_TARGET_H}/h",
    )
    c2.metric(
        "CT Assemblage",
        f'{last["CT Assemblage (s)"]:.2f} s',
        f"{last['CT Assemblage (s)'] - TAKT_TIME:+.2f} s vs Takt",
    )
    c3.metric(
        "CT Push-Back",
        f'{last["CT Push-Back (s)"]:.2f} s',
        f"{last['CT Push-Back (s)'] - TAKT_TIME:+.2f} s vs Takt",
    )
    c4.metric(
        "SMED Komax",
        f'{last["SMED Komax (min)"]:.2f} min',
        f"cible {SMED_TARGET:.2f} min",
    )
    c5.metric(
        "Qualité",
        f"{quality_rate(last):.1f} %",
        f'{last["Production NOK"]:.0f} NOK',
    )

    st.divider()

    # Status cards
    st.subheader("Feu de contrôle")
    s1, s2, s3, s4, s5 = st.columns(5)

    s1.metric("Assemblage", status_lower_is_better(last["CT Assemblage (s)"], TAKT_TIME))
    s2.metric("Push-Back", status_lower_is_better(last["CT Push-Back (s)"], TAKT_TIME))
    s3.metric("SMED", status_lower_is_better(last["SMED Komax (min)"], SMED_TARGET))
    s4.metric("Attente", status_lower_is_better(last["Temps attente (min)"], 10))
    s5.metric("Production", status_higher_is_better(last["Production totale"], PRODUCTION_TARGET_H))

    st.markdown(f"### Statut global : **{global_status(last)}**")

    st.subheader("Évolution des postes critiques")
    chart_df = df.sort_values("Date").copy()

    fig = px.line(
        chart_df,
        x="Date",
        y=["CT Assemblage (s)", "CT Push-Back (s)"],
        markers=True,
        title="Cycle Time des postes critiques",
    )
    fig.add_hline(y=TAKT_TIME, line_dash="dash", annotation_text="Takt = 48 s")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Dernières mesures")
    display_cols = [
        "Date", "Production totale", "Production OK", "Production NOK",
        "CT Assemblage (s)", "CT Push-Back (s)",
        "SMED Komax (min)", "Temps attente (min)",
        "Distance Milk-Run (m/h)", "Cause principale"
    ]
    st.dataframe(
        df.sort_values("Date", ascending=False)[display_cols].head(10),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# 2. DAILY ENTRY
# ============================================================
elif page == "📝 Saisie quotidienne":
    st.title("📝 Saisie quotidienne")
    st.caption("Un relevé par jour pour assurer le contrôle de la ligne.")

    with st.form("daily_form"):
        d = st.date_input("Date du relevé", value=date.today())

        st.subheader("Production & qualité")
        a, b, c = st.columns(3)
        production = a.number_input("Production totale", min_value=0, step=1)
        ok = b.number_input("Production OK", min_value=0, step=1)
        nok = c.number_input("Production NOK", min_value=0, step=1)

        st.subheader("Cycle Time")
        a, b = st.columns(2)
        ct_assembly = a.number_input(
            "CT Assemblage (s)",
            min_value=0.0,
            value=float(ASSEMBLY_S3),
            step=0.1,
        )
        ct_pushback = b.number_input(
            "CT Insertion & Push-Back (s)",
            min_value=0.0,
            value=float(PUSHBACK_TARGET),
            step=0.1,
        )

        st.subheader("Autres KPI")
        a, b, c = st.columns(3)
        smed = a.number_input(
            "SMED Komax Alpha 550T (min)",
            min_value=0.0,
            value=float(SMED_TARGET),
            step=0.01,
        )
        waiting = b.number_input(
            "Temps d'attente (min)",
            min_value=0.0,
            step=0.1,
        )
        milk_run = c.number_input(
            "Distance Milk-Run (m/h)",
            min_value=0.0,
            step=1.0,
            help="À renseigner après mise en œuvre du Milk-Run.",
        )

        cause = st.selectbox("Cause principale", CAUSES)
        comment = st.text_area("Commentaire / observation")

        submitted = st.form_submit_button("💾 Enregistrer le relevé")

    if submitted:
        if ok + nok > production:
            st.error("Production OK + NOK ne peut pas dépasser la production totale.")
        else:
            new_row = pd.DataFrame([{
                "Date": pd.Timestamp(d),
                "Production totale": production,
                "Production OK": ok,
                "Production NOK": nok,
                "Takt Time (s)": TAKT_TIME,
                "CT Assemblage (s)": ct_assembly,
                "CT Push-Back (s)": ct_pushback,
                "SMED Komax (min)": smed,
                "Temps attente (min)": waiting,
                "Distance Milk-Run (m/h)": milk_run,
                "Cause principale": cause,
                "Commentaire": comment,
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)

            st.success("Relevé enregistré avec succès.")

            alerts = []
            if ct_assembly > TAKT_TIME:
                alerts.append("CT Assemblage supérieur au Takt.")
            if ct_pushback > TAKT_TIME:
                alerts.append("CT Push-Back supérieur au Takt.")
            if smed > SMED_TARGET:
                alerts.append("SMED supérieur à la cible.")
            if waiting > 10:
                alerts.append("Temps d'attente élevé.")
            if production < PRODUCTION_TARGET_H:
                alerts.append("Production inférieure à l'objectif.")

            if alerts:
                st.warning("⚠️ Écarts détectés : " + " | ".join(alerts))
            else:
                st.success("🟢 Tous les contrôles principaux sont conformes.")

# ============================================================
# 3. KPI FOLLOW-UP
# ============================================================
elif page == "📈 Suivi des KPI":
    st.title("📈 Suivi des KPI")
    if df.empty:
        st.info("Aucune donnée disponible.")
        st.stop()

    dff = df.sort_values("Date")

    kpi = st.selectbox(
        "Choisir le KPI",
        [
            "CT Assemblage (s)",
            "CT Push-Back (s)",
            "SMED Komax (min)",
            "Temps attente (min)",
            "Distance Milk-Run (m/h)",
            "Production totale",
        ],
    )

    targets = {
        "CT Assemblage (s)": TAKT_TIME,
        "CT Push-Back (s)": TAKT_TIME,
        "SMED Komax (min)": SMED_TARGET,
        "Temps attente (min)": 10,
        "Distance Milk-Run (m/h)": 400,
        "Production totale": PRODUCTION_TARGET_H,
    }

    fig = px.line(
        dff,
        x="Date",
        y=kpi,
        markers=True,
        title=f"Évolution : {kpi}",
    )

    if kpi in ["Production totale"]:
        fig.add_hline(
            y=targets[kpi],
            line_dash="dash",
            annotation_text=f"Cible = {targets[kpi]}",
        )
    else:
        fig.add_hline(
            y=targets[kpi],
            line_dash="dash",
            annotation_text=f"Seuil = {targets[kpi]}",
        )

    st.plotly_chart(fig, use_container_width=True)

    latest = dff.iloc[-1][kpi]
    target = targets[kpi]

    if kpi == "Production totale":
        status = status_higher_is_better(latest, target)
    else:
        status = status_lower_is_better(latest, target)

    a, b, c = st.columns(3)
    a.metric("Dernière valeur", f"{latest:.2f}")
    b.metric("Cible / seuil", f"{target:.2f}")
    c.metric("Statut", status)

# ============================================================
# 4. ALERTS
# ============================================================
elif page == "🚨 Alertes":
    st.title("🚨 Alertes de contrôle")

    if df.empty:
        st.info("Aucune donnée à analyser.")
        st.stop()

    alerts = []

    for _, row in df.sort_values("Date", ascending=False).iterrows():
        if row["CT Assemblage (s)"] > TAKT_TIME:
            alerts.append([
                row["Date"].date(),
                "Cycle Time",
                "Assemblage",
                row["CT Assemblage (s)"],
                TAKT_TIME,
                "🔴 Dépassement du Takt",
            ])

        if row["CT Push-Back (s)"] > TAKT_TIME:
            alerts.append([
                row["Date"].date(),
                "Cycle Time",
                "Insertion & Push-Back",
                row["CT Push-Back (s)"],
                TAKT_TIME,
                "🔴 Dépassement du Takt",
            ])

        if row["SMED Komax (min)"] > SMED_TARGET:
            alerts.append([
                row["Date"].date(),
                "SMED",
                "Komax Alpha 550T",
                row["SMED Komax (min)"],
                SMED_TARGET,
                "🟠 Cible SMED non atteinte",
            ])

        if row["Temps attente (min)"] > 10:
            alerts.append([
                row["Date"].date(),
                "Attente",
                "Ligne HDEP",
                row["Temps attente (min)"],
                10,
                "🟠 Temps d'attente élevé",
            ])

        if row["Production totale"] < PRODUCTION_TARGET_H:
            alerts.append([
                row["Date"].date(),
                "Production",
                "Ligne HDEP",
                row["Production totale"],
                PRODUCTION_TARGET_H,
                "🟠 Production sous objectif",
            ])

    if alerts:
        alert_df = pd.DataFrame(
            alerts,
            columns=["Date", "KPI", "Poste", "Valeur", "Seuil", "Alerte"],
        )
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
        st.warning(f"{len(alerts)} écart(s) détecté(s).")
    else:
        st.success("🟢 Aucun écart détecté.")

# ============================================================
# 5. ACTION PLAN
# ============================================================
elif page == "🔧 Plan d'actions":
    st.title("🔧 Plan d'actions correctives")
    st.caption("Logique : écart → cause → action → responsable → vérification.")

    with st.form("action_form"):
        d = st.date_input("Date", value=date.today())
        problem = st.selectbox(
            "Problème",
            [
                "CT Assemblage > Takt",
                "CT Push-Back > Takt",
                "SMED Komax non atteint",
                "Temps d'attente élevé",
                "Production sous objectif",
                "Qualité / Scrap",
                "Déplacement / Milk-Run",
                "Autre",
            ],
        )
        cause = st.selectbox("Cause", CAUSES)
        action = st.text_area("Action corrective")
        responsible = st.text_input("Responsable")
        deadline = st.date_input("Échéance", value=date.today())
        status = st.selectbox("Statut", ["À faire", "En cours", "Réalisée", "Vérifiée"])
        efficiency = st.selectbox("Efficacité", ["Non évaluée", "Efficace", "Non efficace"])

        submit = st.form_submit_button("Ajouter l'action")

    if submit:
        new_action = pd.DataFrame([{
            "Date": pd.Timestamp(d),
            "Problème": problem,
            "Cause": cause,
            "Action corrective": action,
            "Responsable": responsible,
            "Échéance": pd.Timestamp(deadline),
            "Statut": status,
            "Efficacité": efficiency,
        }])
        actions = pd.concat([actions, new_action], ignore_index=True)
        save_actions(actions)
        st.success("Action ajoutée.")

    st.subheader("Actions enregistrées")
    if actions.empty:
        st.info("Aucune action enregistrée.")
    else:
        st.dataframe(actions.sort_values("Date", ascending=False),
                     use_container_width=True, hide_index=True)

# ============================================================
# 6. BEFORE / AFTER
# ============================================================
elif page == "🔄 Avant / Après":
    st.title("🔄 Avant / Après – Gains du projet")

    comparison = pd.DataFrame({
        "KPI": [
            "CT Assemblage",
            "CT Insertion & Push-Back",
            "SMED Komax",
            "Déplacements opérateurs",
        ],
        "Avant": [
            ASSEMBLY_BASELINE,
            PUSHBACK_BASELINE,
            SMED_BASELINE,
            MOVEMENT_BASELINE,
        ],
        "Après / cible": [
            ASSEMBLY_S3,
            PUSHBACK_TARGET,
            SMED_TARGET,
            0,
        ],
        "Unité": ["s", "s", "min", "s/h"],
    })

    comparison["Gain"] = comparison["Avant"] - comparison["Après / cible"]
    comparison["Gain %"] = (
        comparison["Gain"] / comparison["Avant"] * 100
    )

    st.dataframe(comparison, use_container_width=True, hide_index=True)

    fig = px.bar(
        comparison,
        x="KPI",
        y=["Avant", "Après / cible"],
        barmode="group",
        title="Comparaison Avant / Après ou cible",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Remarque : les valeurs « Après / cible » correspondent aux résultats "
        "ou cibles documentés dans le projet. Le déploiement physique final "
        "des solutions reste à réaliser par l'équipe Process."
    )

    st.subheader("Gains documentés dans le projet")
    st.markdown("""
    - **Assemblage :** 56,05 s → 50,20 s à S+3.
    - **Insertion & Push-Back :** 52,11 s → 35,81 s estimés avec l'outil multi-têtes.
    - **SMED Komax :** 6,33 min → 3,31 min.
    - **Déplacements :** 837,51 s/h de déplacements opérateurs identifiés,
      avec suppression visée grâce au nouveau layout et au Milk-Run.
    """)

# ============================================================
# 7. DATA & EXPORT
# ============================================================
elif page == "📥 Données & export":
    st.title("📥 Données & export")

    st.subheader("Données quotidiennes")
    if df.empty:
        st.info("Aucune donnée.")
    else:
        st.dataframe(df.sort_values("Date", ascending=False),
                     use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Télécharger les données KPI (CSV)",
            csv,
            "HDEP_KPI_Control.csv",
            "text/csv",
        )

    st.divider()
    st.subheader("Plan d'actions")
    if not actions.empty:
        csv_actions = actions.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Télécharger le plan d'actions (CSV)",
            csv_actions,
            "HDEP_Plan_Actions.csv",
            "text/csv",
        )

st.sidebar.divider()
st.sidebar.caption("Application de suivi – Phase Control DMAIC")
