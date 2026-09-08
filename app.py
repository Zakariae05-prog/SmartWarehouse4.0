import numpy as np
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Suivi Phase Contrôle - PFA", page_icon="📈", layout="wide"
)

# Style CSS personnalisé pour l'esthétique industrielle
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555555;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Titre principal
st.markdown(
    '<p class="main-header">Tableau de Bord - Phase Contrôle (PFA)</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Suivi des performances et de la stabilisation de la ligne HDEP après améliorations (Lean & Six Sigma)</p>',
    unsafe_allow_html=True,
)

# --- Barre latérale (Filtres et Navigation) ---
st.sidebar.header("Paramètres de Suivi")
semaine_selectionnee = st.sidebar.selectbox(
    "Sélectionner la Semaine",
    [
        "Semaine N+1",
        "Semaine N+2",
        "Semaine N+3",
        "Semaine N+4",
        "Semaine N+5",
        "Semaine N+6",
    ],
)

# Simulation de données de contrôle basées sur les améliorations
np.random.seed(42)
jours = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
]  # Cibles initiales (Avant vs Après)
takt_time_cible = 48.0  # secondes

# --- Section 1 : KPIs Globaux (Indicateurs Clés) ---
st.subheader("1. Indicateurs Clés de Performance (KPIs)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Takt Time Cible",
        value=f"{takt_time_cible} s",
        delta="Objectif Client",
    )
with col2:
    # Temps de cycle moyen poste Insertion (Cible < 48s)
    cycle_insertion = np.random.normal(35.8, 1.2)
    st.metric(
        label="Poste Insertion (10 têtes)",
        value=f"{cycle_insertion:.2f} s",
        delta=f"{cycle_insertion - takt_time_cible:.2f} s vs Takt",
        delta_color="inverse",
    )
with col3:
    # Temps de changement de série (SMED) - Cible < 3.5 min
    smed_temps = np.random.normal(3.25, 0.1)
    st.metric(
        label="Temps SMED Komax",
        value=f"{smed_temps:.2f} min",
        delta="-48% vs Initial (6.33m)",
    )
with col4:
    # Déplacements / Gaspillage (Spaghetti)
    deplacement = np.random.normal(1.5, 0.2)
    st.metric(
        label="Temps Transport/Heure",
        value=f"{deplacement:.1f} min",
        delta="Optimisé (Milk-Run)",
        delta_color="normal",
    )

st.markdown("---")

# --- Section 2 : Suivi des Temps de Cycle par Poste ---
st.subheader("2. Évolution des Temps de Cycle par Poste Critique")

# Données simulées pour le graphique des postes
df_postes = pd.DataFrame(
    {
        "Jour": jours,
        "Insertion & Push-Back (Cible < 48s)": np.random.uniform(
            35.0, 37.0, len(jours)
        ),
        "Poste Assemblage (Cible < 48s)": np.random.uniform(
            45.0, 47.5, len(jours)
        ),
        "Coupe & Sertissage": np.random.uniform(25.0, 28.0, len(jours)),
    }
)

st.line_chart(df_postes.set_index("Jour"))

# --- Section 3 : Suivi du SMED et de la Disponibilité ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("3. Suivi SMED (Komax Alpha 550T)")
    df_smed = pd.DataFrame(
        {
            "Lot de Production": ["Lot 1", "Lot 2", "Lot 3", "Lot 4", "Lot 5"],
            "Temps de Changement (min)": [3.4, 3.2, 3.3, 3.1, 3.0],
        }
    )
    st.bar_chart(df_smed.set_index("Lot de Production"))

with col_right:
    st.subheader("4. Suivi des Non-Conformités / Scrap")
    df_scrap = pd.DataFrame(
        {
            "Jour": jours,
            "Taux de Défaut (%)": [0.8, 0.5, 0.6, 0.4, 0.3],
        }
    )
    st.area_chart(df_scrap.set_index("Jour"))

st.markdown("---")

# --- Section 4 : Plan d'Action / Remarques de la Phase Contrôle ---
st.subheader("5. Remarques et Validation du Pilote de Ligne")

note_controle = st.text_area(
    "Ajouter une observation pour le rapport (ex: Stabilité de l'outil multi-têtes, retours opérateurs...)",
    "L'utilisation du nouvel outil de fixation multi-têtes a permis de stabiliser le poste d'insertion sous la barre des 36 secondes. Aucune dérive majeure constatée cette semaine.",
)

if st.button("Enregistrer les données de la session"):
    st.success(
        f"Données pour la **{semaine_selectionnee}** enregistrées avec succès !"
    )

# Instructions pour GitHub dans l'application (repliables)
with st.expander("Comment lier ce code à GitHub et le déployer ?"):
    st.markdown(
        """
    1. Créez un dépôt sur **GitHub** (ex: `pfa-controle-line`).
    2. Créez un fichier nommé `app.py` et collez ce code dedans, puis créez un fichier `requirements.txt` contenant :
       ```text
       streamlit
       pandas
       numpy
       ```
    3. Rendez-vous sur [Streamlit Community Cloud](https://streamlit.io/cloud).
    4. Connectez votre compte GitHub, sélectionnez votre dépôt et pointez vers le fichier `app.py`.
    5. Cliquez sur **Deploy** !
    """
    )


