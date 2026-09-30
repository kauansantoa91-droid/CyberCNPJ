# ==============================================================================
# ABA 01: GERADOR EM MASSA
# ==============================================================================
with aba_gerador:
  st.subheader("Gerador de Vetores CNPJ")

  col_g1, col_g2 = st.columns(2)
  with col_g1:
    qtd_opcao = st.selectbox(
        "QUANTIDADE:",
        [
            "50.000",
            "100.000",
            "500.000",
            "1.000.000 (1 Milhão)",
            "5.000.000 (5 Milhões)",
            "10.000.000 (10 Milhões)",
            "100.000.000 (100 Milhões)",
            "1.000.000.000 (1 Bilhão)",
        ],
    )
  with col_g2:
    tipo_opcao = st.selectbox("TIPO:", ["MATRIZ (0001)", "FILIAL (0002)"])

  if st.button("> GERAR VETORES AGORA"):
    qtd_alvo = int(
        qtd_opcao.split()[0].replace(".", "").replace(",", "")
    )
    ordem_fixa = "0001" if "0001" in tipo_opcao else "0002"
    inicio_raiz = random.randint(10000000, 50000000)

    st.write("A gerar vetores matemáticos...")
    barra = st.progress(0)

    cnpjs_gerados = []
    t0 = time.time()

    # Limita a exibição imediata no ecrã para não travar o navegador se escolher valores gigantes
    limite_loop = min(qtd_alvo, 200000)

    for i in range(inicio_raiz, inicio_raiz + limite_loop):
      r12 = f"{i:08d}{ordem_fixa}"
      cnpjs_gerados.append(calcular_dv_cnpj(r12))

    dt = time.time() - t0
    barra.progress(1.0)
    st.success(
        f"Sucesso! Gerados {len(cnpjs_gerados):,} vetores (amostra inicial) em"
        f" {dt:.2f}s."
    )

    st.session_state["cnpjs_lote"] = cnpjs_gerados
    st.text_area(
        "Pré-visualização dos Vetores Gerados:",
        value="\n".join(cnpjs_gerados[:50]),
        height=150,
    )
