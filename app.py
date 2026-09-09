from datetime import date
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURATION & DESIGN ULTRA-MODERNE (CSS INJECTION)
# ============================================================
st.set_page_config(
    page_title="HDEP - Control DMAIC Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
        /* Importation d'une police moderne (Inter / Roboto) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Fond global de l'application */
        .main {
            background-color: #0f172a;
            color: #f8fafc;
        }

        /* Style de la barre latérale (Sidebar) */
        section[data-testid="stSidebar"] {
            background-color: #1e293b;
            border-right: 1px solid #334155;
        }
        
        section[data-testid="stSidebar"] .css-17lntkn {
            color: #f8fafc;
        }

        /* Cartes de métriques personnalisées avec effet néon subtil */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            padding: 18px 20px;
            border-radius: 14px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }

        /* Style des en-têtes */
        h1, h2, h3 {
            color: #f8fafc;
            font-weight: 700;
        }

        /* Boutons personnalisés */
        div.stButton > button {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.3);
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
            box-shadow: 0 6px 8px -1px rgba(2, 132, 199, 0.4);
            transform: translateY(-1px);
        }

        /* Tableaux et dataframes */
        DataFrame {
            border-radius: 10px;
            overflow: hidden;
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
st.sidebar.markdown(
    "<h2 style='color: #38bdf8; text-align: center;'>⚡ HDEP CONTROL</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>TE"
    " Connectivity | Ligne Volvo</p>",
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
    "💡 Pilotage journalier post-implémentation (Temps de cycle, SMED, Scrap,"
    " Milk-Run)."
)

# ============================================================
# 1. DASHBOARD
# ============================================================
if page == "📊 Dashboard Control":
  st.title("📊 Dashboard de Contrôle – Ligne HDEP")
  st.markdown(
      "<p style='color: #94a3b8;'>Pérennisation des améliorations – Phase"
      " <b>Control</b> du projet DMAIC</p>",
      unsafe_allow_html=True,
  )
  st.write("")

  if df.empty:
    st.warning("⚠️ Aucune donnée quotidienne n'est encore saisie.")
    st.info("Commencez par renseigner la page « Saisie quotidienne ».")
    st.stop()

  last = df.sort_values("Date").iloc[-1]

  st.markdown("### 📌 Situation du dernier relevé")
  c1, c2, c3, c4, c5 = st.columns(5)

  # 1. Production
  prod_ok = last["Total production"] >= last["Objectif production"]
  c1.metric(
      "Production",
      f'{last["Total production"]:.0f}',
      f"Objectif: {last['Objectif production']:.0f}",
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
      "Milk-Run (0 déplace.)",
      str(last["Milk-Run 100%"]),
      "Cible: Oui",
      delta_color="normal" if milk_ok else "inverse",
  )

  st.write("")
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
  st.subheader("📈 Évolution des Temps de Cycle")
  chart_df = df.sort_values("Date").copy()

  fig = px.line(
      chart_df,
      x="Date",
      y=["CT Assemblage (s)", "CT Push-Back (s)"],
      markers=True,
      template="plotly_dark",
  )
  fig.add_hline(
      y=TAKT_TIME,
      line_dash="dash",
      line_color="#ef4444",
      annotation_text="Takt Time (48s)",
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      margin=dict(l=20, r=20, t=30, b=20),
      legend_title="Indicateurs",
      font=dict(family="Inter", color="#f8fafc"),
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 2. DAILY ENTRY
# ============================================================
elif page == "📝 Saisie quotidienne":
  st.title("📝 Saisie Quotidienne des Indicateurs")
  st.markdown(
      "<p style='color: #94a3b8;'>Enregistrez les performances journalières"
      " pour alimenter le tableau de bord.</p>",
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
        "Remarque ou commentaire du jour sur les améliorations"
    )
    perf_validee = st.radio(
        "Performances validées pour la journée ?",
        ["Validée", "Non validée"],
        horizontal=True,
    )

    st.write("")
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
    st.success("✨ Relevé journalier enregistré avec succès !")

# ============================================================
# 3. KPI FOLLOW-UP
# ============================================================
elif page == "📈 Suivi des KPI":
  st.title("📈 Analyse et Suivi des KPI")
  if df.empty:
    st.info("Aucune donnée disponible.")
    st.stop()

  dff = df.sort_values("Date")
  kpi = st.selectbox(
      "Sélectionner le KPI à analyser",
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
      template="plotly_dark",
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font=dict(family="Inter", color="#f8fafc"),
  )
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
        "🟢 Aucune dérive majeure enregistrée (Toutes les journées sont"
        " validées)."
    )

# ============================================================
# 5. ACTION PLAN
# ============================================================
elif page == "🔧 Plan d'actions":
  st.title("🔧 Plan d'actions correctives")

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
  st.title("🔄 Bilan Avant / Après – Gains du Projet")

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
      title="Comparaison Avant / Après les Améliorations",
      template="plotly_dark",
  )
  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font=dict(family="Inter", color="#f8fafc"),
  )
  st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 7. DATA & EXPORT
# ============================================================
elif page == "📥 Données & export":
  st.title("📥 Base de données & Export")
  if not df.empty:
    st.subheader("Journal des relevés")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger le rapport complet (CSV)",
        csv,
        "HDEP_Control_Data.csv",
        "text/csv",
    )
