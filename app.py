from datetime import date
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURATION & DESIGN SAAS / ULTRAS-MODERNE
# ============================================================
st.set_page_config(
    page_title="HDEP - Control Dashboard", page_icon="⚡", layout="wide"
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

        /* Application de la police moderne */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta+Sans', sans-serif;
        }

        /* Fond général et palette style SaaS */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
        }

        /* Sidebar moderne */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }

        /* Cartes de métriques dynamiques avec effet glassmorphism */
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.15);
            border-color: #3b82f6;
        }

        /* Titres élégants */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 700;
        }

        /* Boutons stylisés */
        div.stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            transition: all 0.3s ease;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
            transform: translateY(-2px);
        }

        /* Conteneurs personnalisés (Cards) */
        .custom-card {
            background: #ffffff;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
            margin-bottom: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = Path("hdep_control_data.csv")
ACTIONS_FILE = Path("hdep_actions.csv")

TAKT_TIME = 48.0
ASSEMBLY_BASELINE = 56.05
ASSEMBLY_TARGET = 48.0
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
# DATA FUNCTIONS
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
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown(
    "<h3 style='color: #2563eb; text-align: center; margin-bottom: 0;'>⚡ HDEP"
    " CONTROL</h3>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>TE"
    " Connectivity — Ligne Volvo</p>",
    unsafe_allow_html=True,
)
st.sidebar.divider()

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
    "💡 Outil interactif de pérennisation des gains (DMAIC - Phase Control)."
)

# ============================================================
# 1. DASHBOARD CONTROL
# ============================================================
if page == "📊 Dashboard Control":
  st.title("📊 Dashboard de Contrôle en Temps Réel")
  st.markdown(
      "<p style='color: #64748b; margin-top: -10px;'>Suivi opérationnel et"
      " validation des performances post-optimisation de la ligne HDEP.</p>",
      unsafe_allow_html=True,
  )
  st.write("")

  if df.empty:
    st.warning("⚠️ Aucune donnée quotidienne n'est encore enregistrée.")
    st.info(
        "Rendez-vous dans la section **« Saisie quotidienne »** pour alimenter"
        " le tableau de bord."
    )
    st.stop()

  last = df.sort_values("Date").iloc[-1]

  st.markdown("### 📌 Indicateurs Clés — Dernier Relevé")
  c1, c2, c3, c4, c5 = st.columns(5)

  # 1. Production
  prod_ok = last["Total production"] >= last["Objectif production"]
  c1.metric(
      "Production",
      f'{last["Total production"]:.0f}',
      f"Obj: {last['Objectif production']:.0f}",
      delta_color="normal" if prod_ok else "inverse",
  )

  # 2. CT Assemblage
  asm_diff = last["CT Assemblage (s)"] - TAKT_TIME
  asm_ok = asm_diff <= 0
  c2.metric(
      "CT Assemblage",
      f'{last["CT Assemblage (s)"]:.2f} s',
      f"{asm_diff:+.2f} s vs Takt",
      delta_color="inverse" if asm_ok else "normal",
  )

  # 3. CT Push-Back
  pb_diff = last["CT Push-Back (s)"] - TAKT_TIME
  pb_ok = pb_diff <= 0
  c3.metric(
      "CT Push-Back",
      f'{last["CT Push-Back (s)"]:.2f} s',
      f"{pb_diff:+.2f} s vs Takt",
      delta_color="inverse" if pb_ok else "normal",
  )

  # 4. SMED Komax
  smed_ok = last["SMED Komax (min)"] <= SMED_TARGET
  c4.metric(
      "SMED Komax",
      f'{last["SMED Komax (min)"]:.2f} min',
      f"Cible {SMED_TARGET} min",
      delta_color="normal" if smed_ok else "inverse",
  )

  # 5. Milk-Run
  milk_ok = str(last["Milk-Run 100%"]).strip().lower() in ["oui", "100%"]
  c5.metric(
      "Milk-Run",
      str(last["Milk-Run 100%"]),
      "Cible: Oui",
      delta_color="normal" if milk_ok else "inverse",
  )

  st.write("")

  # Statut de validation sous forme de bannière dynamique
  statut_val = last["Performance validée"]
  if statut_val == "Validée":
    st.success(
        f"✅ **Statut de la journée ({last['Date'].strftime('%d/%m/%Y')}):**"
        " Performances validées avec succès. Objectifs atteints !"
    )
  else:
    st.error(
        f"❌ **Statut de la journée ({last['Date'].strftime('%d/%m/%Y')}):**"
        " Alerte dérive détectée sur la ligne."
    )
    if (
        pd.notna(last["Cause dérive"])
        and last["Cause dérive"] != "Aucune (Conforme)"
    ):
      st.warning(f"🔍 **Cause racine identifiée :** {last['Cause dérive']}")

  if pd.notna(last["Commentaire"]) and str(last["Commentaire"]).strip() != "":
    st.info(f"💬 **Commentaire terrain :** {last['Commentaire']}")

  st.divider()
  st.subheader("📈 Dynamique des Temps de Cycle vs Takt Time")
  chart_df = df.sort_values("Date").copy()

  fig = px.line(
      chart_df,
      x="Date",
      y=["CT Assemblage (s)", "CT Push-Back (s)"],
      markers=True,
      template="plotly_white",
      color_discrete_sequence=["#2563eb", "#06b6d4"],
  )
  fig.add_hline(
      y=TAKT_TIME,
      line_dash="dash",
      line_color="#ef4444",
      annotation_text="Takt Time Cible (48s)",
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      margin=dict(l=20, r=20, t=30, b=20),
      legend_title="Postes",
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 2. DAILY ENTRY
# ============================================================
elif page == "📝 Saisie quotidienne":
  st.title("📝 Saisie Quotidienne des Indicateurs")
  st.markdown(
      "<p style='color: #64748b;'>Enregistrez les paramètres de production de"
      " la journée pour actualiser instantanément les graphiques.</p>",
      unsafe_allow_html=True,
  )

  with st.form("daily_form"):
    d = st.date_input("Date du relevé", value=date.today())

    st.subheader("1. 📊 Production & Qualité")
    col1, col2, col3 = st.columns(3)
    obj_prod = col1.number_input(
        "Objectif de production", min_value=0.0, value=75.0, step=1.0
    )
    tot_prod = col2.number_input(
        "Total de production", min_value=0.0, value=75.0, step=1.0
    )
    scrap = col3.number_input("Scrap (%)", min_value=0.0, value=1.0, step=0.1)

    st.subheader("2. ⏱️ Temps de Cycle & SMED")
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

    st.subheader("3. 🚚 Logistique & Dérives")
    col1, col2 = st.columns(2)
    milk_run = col1.selectbox(
        "Déplacements opérateurs éliminés à 100% par Milk-Run ?",
        ["Oui", "Non", "Partiellement"],
    )
    cause_derive = col2.selectbox(
        "Cause de la dérive (si écart détecté)", CAUSES
    )

    st.subheader("4. 💬 Validation & Commentaires")
    commentaire = st.text_area(
        "Remarque ou observation sur la ligne (optionnel)"
    )
    perf_validee = st.radio(
        "Performances validées pour la journée ?",
        ["Validée", "Non validée"],
        horizontal=True,
    )

    st.write("")
    submitted = st.form_submit_button(
        "💾 Enregistrer et Mettre à Jour le Dashboard"
    )

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
    st.success("✨ Relevé journalier enregistré avec succès !")

# ============================================================
# 3. KPI FOLLOW-UP
# ============================================================
elif page == "📈 Suivi des KPI":
  st.title("📈 Analyse et Tendances des KPI")
  if df.empty:
    st.info("Aucune donnée disponible.")
    st.stop()

  dff = df.sort_values("Date")
  kpi = st.selectbox(
      "Sélectionner l'indicateur à analyser",
      [
          "CT Assemblage (s)",
          "CT Push-Back (s)",
          "SMED Komax (min)",
          "Scrap (%)",
          "Total production",
      ],
  )

  fig = px.line(
      dff,
      x="Date",
      y=kpi,
      markers=True,
      title=f"Historique de l'indicateur : {kpi}",
      template="plotly_white",
      color_discrete_sequence=["#2563eb"],
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 4. ALERTS & DRIFTS
# ============================================================
elif page == "🚨 Alertes & Dérives":
  st.title("🚨 Suivi des Dérives & Analyse des Causes")
  if df.empty:
    st.info("Aucune donnée.")
    st.stop()

  derives_df = df[df["Performance validée"] == "Non validée"]
  if not derives_df.empty:
    st.warning(
        f"⚠️ {len(derives_df)} jour(s) enregistré(s) avec des performances non"
        " validées."
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
    st.success(
        "🟢 Aucune dérive majeure enregistrée. Processus totalement sous"
        " contrôle !"
    )

# ============================================================
# 5. ACTION PLAN
# ============================================================
elif page == "🔧 Plan d'actions":
  st.title("🔧 Plan d'Actions Correctives (PDCA)")

  with st.form("action_form"):
    col1, col2 = st.columns(2)
    d = col1.date_input("Date", value=date.today())
    problem = col2.text_input("Problème / Dérive constatée")

    col3, col4 = st.columns(2)
    cause = col3.selectbox("Cause principale", CAUSES)
    responsible = col4.text_input("Responsable")

    action = st.text_area("Action corrective détaillée")

    col5, col6 = st.columns(2)
    deadline = col5.date_input("Échéance", value=date.today())
    status = col6.selectbox("Statut", ["À faire", "En cours", "Réalisée"])

    efficiency = st.selectbox("Efficacité", ["Non évaluée", "Efficace"])
    submit = st.form_submit_button("➕ Ajouter l'action au plan")

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
    st.success("✨ Action ajoutée avec succès.")

  if not actions.empty:
    st.divider()
    st.subheader("📋 Suivi du plan d'actions")
    st.dataframe(actions, use_container_width=True, hide_index=True)

# ============================================================
# 6. BEFORE / AFTER
# ============================================================
elif page == "🔄 Avant / Après":
  st.title("🔄 Bilan Avant / Après – Gains du Projet PFA")
  st.markdown(
      "<p style='color: #64748b;'>Comparaison directe des performances"
      " industrielles avant et après le déploiement du DMAIC.</p>",
      unsafe_allow_html=True,
  )

  comparison = pd.DataFrame({
      "KPI": [
          "CT Assemblage",
          "CT Insertion & Push-Back",
          "SMED Komax",
          "Déplacements opérateurs",
      ],
      "Avant": [ASSEMBLY_BASELINE, PUSHBACK_BASELINE, SMED_BASELINE, 837.51],
      "Après / Cible": [ASSEMBLY_TARGET, PUSHBACK_TARGET, SMED_TARGET, 0.0],
      "Unité": ["s", "s", "min", "s/h"],
  })

  comparison["Gain"] = comparison["Avant"] - comparison["Après / Cible"]
  st.dataframe(comparison, use_container_width=True, hide_index=True)

  fig = px.bar(
      comparison,
      x="KPI",
      y=["Avant", "Après / Cible"],
      barmode="group",
      title="Comparaison Graphique Avant / Après",
      template="plotly_white",
      color_discrete_sequence=["#94a3b8", "#2563eb"],
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 7. DATA & EXPORT
# ============================================================
elif page == "📥 Données & export":
  st.title("📥 Base de Données & Exportation")
  if not df.empty:
    st.subheader("Journal complet des relevés")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger le rapport complet (CSV)",
        csv,
        "HDEP_Control_Data.csv",
        "text/csv",
    )
