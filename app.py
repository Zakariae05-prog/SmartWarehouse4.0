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

  # 1. Production (Plus c'est haut, mieux c'est)
  prod_ok = last["Total production"] >= last["Objectif production"]
  c1.metric(
      "Production",
      f'{last["Total production"]:.0f}',
      f"Objectif: {last['Objectif production']:.0f}",
      delta_color="normal" if prod_ok else "inverse",
  )

  # 2. CT Assemblage (Doit être <= Takt Time 48s -> Moins c'est haut, mieux c'est)
  asm_diff = last["CT Assemblage (s)"] - TAKT_TIME
  asm_ok = asm_diff <= 0
  c2.metric(
      "CT Assemblage",
      f'{last["CT Assemblage (s)"]:.2f} s',
      f"{asm_diff:+.2f} s vs Takt",
      delta_color="inverse"
      if asm_ok
      else "normal",  # inverse fait passer le négatif (baisse) en VERT
  )

  # 3. CT Push-Back (Doit être <= Takt Time 48s -> Moins c'est haut, mieux c'est)
  pb_diff = last["CT Push-Back (s)"] - TAKT_TIME
  pb_ok = pb_diff <= 0
  c3.metric(
      "CT Push-Back",
      f'{last["CT Push-Back (s)"]:.2f} s',
      f"{pb_diff:+.2f} s vs Takt",
      delta_color="inverse" if pb_ok else "normal",
  )

  # 4. SMED Komax (Doit être <= SMED_TARGET 3.31 min)
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
