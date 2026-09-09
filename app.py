from datetime import date
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

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
ASSEMBLY_TARGET = 48.0  # Modifié à 48s
PUSHBACK_BASELINE = 52.11
PUSHBACK_TARGET = 35.81
SMED_BASELINE = 6.33
SMED_TARGET = 3.31

CAUSES = [
    "Aucune (Conforme)",
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
  return pd.DataFrame(
      columns=[
          "Date",
          "Objectif production",
          "Total production",
          "Scrap (%)",
          "CT Assemblage (s)",
          "CT Push-Back (s)",
          "SMED Komax (min)",
          "Milk-Run 100%",
          "Cause dérive",
          "Performance validée",
          "Commentaire",
      ]
  )


def save_data(df):
  df.to_csv(DATA_FILE, index=False)


def load_actions():
  if ACTIONS_FILE.exists():
    return pd.read_csv(ACTIONS_FILE)
  return pd.DataFrame(
      columns=[
          "Date",
          "Problème",
          "Cause",
          "Action corrective",
          "Responsable",
          "Échéance",
          "Statut",
          "Efficacité",
      ]
  )


def save_actions(df):
  df.to_csv(ACTIONS_FILE, index=False)


df = load_data()
actions = load_actions()

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
        "🚨 Alertes & Dérives",
        "🔧 Plan d'actions",
        "🔄 Avant / Après",
        "📥 Données & export",
    ],
)

st.sidebar.divider()
st.sidebar.info(
    "Contrôle journalier des améliorations post-implémentation (Temps de"
    " cycle, SMED, Scrap, Milk-Run)."
)

# ============================================================
# 1. DASHBOARD
# ============================================================
if page == "📊 Dashboard Control":
  st.title("📊 Dashboard de Contrôle – Ligne HDEP")
  st.markdown("### Pérennisation des améliorations – Phase **Control**")

  if df.empty:
    st.warning("Aucune donnée quotidienne n'est encore saisie.")
    st.info("Commencez par la page « Saisie quotidienne ».")
    st.stop()

  last = df.sort_values("Date").iloc[-1]

  st.subheader("Situation du dernier relevé (Objectifs & Seuils)")
  c1, c2, c3, c4, c5 = st.columns(5)

  # Évaluation des objectifs (Vert si atteint, Rouge sinon)
  # Production
  prod_ok = last["Total production"] >= last["Objectif production"]
  c1.metric(
      "Production",
      f'{last["Total production"]:.0f}',
      f"Objectif: {last['Objectif production']:.0f}",
      delta_color="normal" if prod_ok else "inverse",
  )

  # CT Assemblage (Doit être <= Takt Time 48s)
  asm_ok = last["CT Assemblage (s)"] <= TAKT_TIME
  c2.metric(
      "CT Assemblage",
      f'{last["CT Assemblage (s)"]:.2f} s',
      f"{last['CT Assemblage (s)'] - TAKT_TIME:+.2f} s vs Takt",
      delta_color="normal" if asm_ok else "inverse",
  )

  # CT Push-Back (Doit être <= Takt Time 48s)
  pb_ok = last["CT Push-Back (s)"] <= TAKT_TIME
  c3.metric(
      "CT Push-Back",
      f'{last["CT Push-Back (s)"]:.2f} s',
      f"{last['CT Push-Back (s)'] - TAKT_TIME:+.2f} s vs Takt",
      delta_color="normal" if pb_ok else "inverse",
  )

  # SMED Komax (Doit être <= SMED_TARGET 3.31 min)
  smed_ok = last["SMED Komax (min)"] <= SMED_TARGET
  c4.metric(
      "SMED Komax",
      f'{last["SMED Komax (min)"]:.2f} min',
      f"Cible {SMED_TARGET} min",
      delta_color="normal" if smed_ok else "inverse",
  )

  # Milk-Run (Doit être "Oui" pour 100%)
  milk_ok = str(last["Milk-Run 100%"]).strip().lower() in ["oui", "100%"]
  c5.metric(
      "Milk-Run (0 déplace.)",
      str(last["Milk-Run 100%"]),
      "Cible: Oui",
      delta_color="normal" if milk_ok else "inverse",
  )

  st.divider()

  # Status de validation journalière
  statut_val = last["Performance validée"]
  if statut_val == "Validée":
    st.success(
        f"✅ **Statut de la journée ({last['Date'].strftime('%d/%m/%Y')}):"
        " Performances VALIDÉES**"
    )
  else:
    st.error(
        f"❌ **Statut de la journée ({last['Date'].strftime('%d/%m/%Y')}):"
        " Performances NON VALIDÉES (Dérive détectée)**"
    )
    if (
        pd.notna(last["Cause dérive"])
        and last["Cause dérive"] != "Aucune (Conforme)"
    ):
      st.warning(f"🔍 **Cause principale identifiée :** {last['Cause dérive']}")

  if pd.notna(last["Commentaire"]) and str(last["Commentaire"]).strip() != "":
    st.info(f"💬 **Remarque du jour :** {last['Commentaire']}")

  st.divider()
  st.subheader("Évolution du Temps de Cycle")
  chart_df = df.sort_values("Date").copy()

  fig = px.line(
      chart_df,
      x="Date",
      y=["CT Assemblage (s)", "CT Push-Back (s)"],
      markers=True,
      title="Suivi des Temps de Cycle vs Takt Time (48s)",
  )
  fig.add_hline(
      y=TAKT_TIME, line_dash="dash", line_color="red", annotation_text="Takt"
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 2. DAILY ENTRY
# ============================================================
elif page == "📝 Saisie quotidienne":
  st.title("📝 Saisie quotidienne")
  st.caption(
      "Enregistrez les indicateurs clés et validez la performance du jour."
  )

  with st.form("daily_form"):
    d = st.date_input("Date du relevé", value=date.today())

    st.subheader("1. Production & Qualité")
    col1, col2, col3 = st.columns(3)
    obj_prod = col1.number_input(
        "Objectif de production", min_value=0.0, value=75.0, step=1.0
    )
    tot_prod = col2.number_input(
        "Total de production", min_value=0.0, value=75.0, step=1.0
    )
    scrap = col3.number_input("Scrap (%)", min_value=0.0, value=1.0, step=0.1)

    st.subheader("2. Temps de Cycle & SMED")
    col1, col2, col3 = st.columns(3)
    ct_assembly = col1.number_input(
        "Cycle time poste assemblage (s)",
        min_value=0.0,
        value=float(ASSEMBLY_TARGET),
        step=0.1,
    )
    ct_pushback = col2.number_input(
        "Cycle time insertion & push-back (s)",
        min_value=0.0,
        value=float(PUSHBACK_TARGET),
        step=0.1,
    )
    smed_komax = col3.number_input(
        "Temps SMED Komax 550T (min)",
        min_value=0.0,
        value=float(SMED_TARGET),
        step=0.01,
    )

    st.subheader("3. Logistique & Dérives")
    col1, col2 = st.columns(2)
    milk_run = col1.selectbox(
        "Déplacements opérateurs éliminés à 100% par Milk-Run ?",
        ["Oui", "Non", "Partiellement"],
    )
    cause_derive = col2.selectbox(
        "Cause de la dérive (si écart détecté)", CAUSES
    )

    st.subheader("4. Commentaire & Validation finale")
    commentaire = st.text_area(
        "Commentaire ou remarque du jour à propos des améliorations"
    )
    perf_validee = st.radio(
        "Performances validées pour la journée ?",
        ["Validée", "Non validée"],
        horizontal=True,
    )

    submitted = st.form_submit_button("💾 Enregistrer le relevé journalier")

  if submitted:
    new_row = pd.DataFrame([
        {
            "Date": pd.Timestamp(d),
            "Objectif production": obj_prod,
            "Total production": tot_prod,
            "Scrap (%)": scrap,
            "CT Assemblage (s)": ct_assembly,
            "CT Push-Back (s)": ct_pushback,
            "SMED Komax (min)": smed_komax,
            "Milk-Run 100%": milk_run,
            "Cause dérive": cause_derive,
            "Performance validée": perf_validee,
            "Commentaire": commentaire,
        }
    ])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.success("Relevé journalier enregistré avec succès !")

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
      "Choisir le KPI à analyser",
      [
          "CT Assemblage (s)",
          "CT Push-Back (s)",
          "SMED Komax (min)",
          "Scrap (%)",
          "Total production",
      ],
  )

  fig = px.line(dff, x="Date", y=kpi, markers=True, title=f"Évolution de {kpi}")
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 4. ALERTS & DRIFTS
# ============================================================
elif page == "🚨 Alertes & Dérives":
  st.title("🚨 Suivi des Dérives & Causes")
  if df.empty:
    st.info("Aucune donnée.")
    st.stop()

  derives_df = df[df["Performance validée"] == "Non validée"]
  if not derives_df.empty:
    st.warning(
        f"{len(derives_df)} jour(s) avec des performances non validées."
    )
    st.dataframe(
        derives_df[
            [
                "Date",
                "Cause dérive",
                "Commentaire",
                "CT Assemblage (s)",
                "SMED Komax (min)",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.success("🟢 Aucune dérive majeure enregistrée (Toutes journées validées).")

# ============================================================
# 5. ACTION PLAN
# ============================================================
elif page == "🔧 Plan d'actions":
  st.title("🔧 Plan d'actions correctives")

  with st.form("action_form"):
    d = st.date_input("Date", value=date.today())
    problem = st.text_input("Problème / Dérive constatée")
    cause = st.selectbox("Cause principale", CAUSES)
    action = st.text_area("Action corrective")
    responsible = st.text_input("Responsable")
    deadline = st.date_input("Échéance", value=date.today())
    status = st.selectbox("Statut", ["À faire", "En cours", "Réalisée"])
    efficiency = st.selectbox("Efficacité", ["Non évaluée", "Efficace"])
    submit = st.form_submit_button("Ajouter l'action")

  if submit:
    new_action = pd.DataFrame([
        {
            "Date": pd.Timestamp(d),
            "Problème": problem,
            "Cause": cause,
            "Action corrective": action,
            "Responsable": responsible,
            "Échéance": pd.Timestamp(deadline),
            "Statut": status,
            "Efficacité": efficiency,
        }
    ])
    actions = pd.concat([actions, new_action], ignore_index=True)
    save_actions(actions)
    st.success("Action ajoutée au plan.")

  if not actions.empty:
    st.dataframe(actions, use_container_width=True, hide_index=True)

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
      "Avant": [ASSEMBLY_BASELINE, PUSHBACK_BASELINE, SMED_BASELINE, 837.51],
      "Après / Cible": [
          ASSEMBLY_TARGET,
          PUSHBACK_TARGET,
          SMED_TARGET,
          0.0,
      ],  # Assembly target = 48s
      "Unité": ["s", "s", "min", "s/h"],
  })

  comparison["Gain"] = comparison["Avant"] - comparison["Après / Cible"]
  st.dataframe(comparison, use_container_width=True, hide_index=True)

  fig = px.bar(
      comparison,
      x="KPI",
      y=["Avant", "Après / Cible"],
      barmode="group",
      title="Comparaison Avant / Après",
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 7. DATA & EXPORT
# ============================================================
elif page == "📥 Données & export":
  st.title("📥 Données & export")
  if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger le suivi (CSV)",
        csv,
        "HDEP_Control_Data.csv",
        "text/csv",
    )
