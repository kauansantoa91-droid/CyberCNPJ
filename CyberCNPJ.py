from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import random
import re
import time
import requests
import streamlit as st

# Configuração da Página Web
st.set_page_config(
    page_title="2B DataSync - Cyber CNPJ", page_icon="🛡️", layout="wide"
)

# Estilização Visual (Tema Cyberpunk Hacker)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050807;
        color: #00ff66;
    }
    h1, h2, h3 {
        color: #00ff66 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #030504 !important;
        color: #00ff66 !important;
        border: 1px solid #004d1f !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ TERMINAL // GERADOR & FILTRO DE ALTA RENDA CNPJ")

# --- MOTOR MATEMÁTICO DE DÍGITOS VERIFICADORES (MÓDULO 11) ---


def calcular_dv_cnpj(raiz_12_digitos):
  p1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
  s1 = sum(int(raiz_12_digitos[i]) * p1[i] for i in range(12))
  r1 = s1 % 11
  d1 = 0 if r1 < 2 else 11 - r1

  p2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
  raiz_com_d1 = raiz_12_digitos + str(d1)
  s2 = sum(int(raiz_com_d1[i]) * p2[i] for i in range(13))
  r2 = s2 % 11
  d2 = 0 if r2 < 2 else 11 - r2

  return f"{raiz_12_digitos}{d1}{d2}"


# Abas da Aplicação Web
aba_gerador, aba_triagem = st.tabs(
    ["[01] GERADOR EM MASSA", "[02] FILTRO TURBO DE ALTA RENDA"]
)

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

    for i in range(inicio_raiz, inicio_raiz + min(qtd_alvo, 100000)):
      r12 = f"{i:08d}{ordem_fixa}"
      cnpjs_gerados.append(calcular_dv_cnpj(r12))

    dt = time.time() - t0
    barra.progress(1.0)
    st.success(
        f"Sucesso! Gerados {len(cnpjs_gerados):,} vetores em {dt:.2f}s."
    )

    # Guarda na sessão para usar na triagem
    st.session_state["cnpjs_lote"] = cnpjs_gerados
    st.text_area(
        "Pré-visualização dos Vetores Gerados:",
        value="\n".join(cnpjs_gerados[:50]),
        height=150,
    )

# ==============================================================================
# ABA 02: FILTRO TURBO DE ALTA RENDA
# ==============================================================================
with aba_triagem:
  st.subheader("Filtro Turbo de Ativos e Alta Renda")

  col_t1, col_t2 = st.columns(2)
  with col_t1:
    criterio_renda = st.selectbox(
        "PORTE/CRITÉRIO:",
        [
            "SOMENTE DEMAIS (ALTA RENDA)",
            "DEMAIS + EPP (ALTA E MÉDIA)",
            "QUALQUER ATIVA (CAPITAL > 0)",
        ],
    )
  with col_t2:
    capital_minimo = st.number_input(
        "CAPITAL SOCIAL MÍNIMO (R$):", value=100000.0, step=50000.0
    )

  if st.button("> INICIAR VARREDURA TURBO"):
    alvos = st.session_state.get("cnpjs_lote", [])
    if not alvos:
      st.warning(
          "Nenhum vetor encontrado. Gere os vetores primeiro na Aba [01]."
      )
    else:
      st.info(f"A iniciar triagem em {len(alvos)} alvos...")
      barra_triagem = st.progress(0)
      aprovados = []

      session_http = requests.Session()

      def testar_cnpj(c):
        try:
          r = session_http.get(f"https://minhareceita.org/{c}", timeout=4)
          if r.status_code == 200:
            d = r.json()
            sit = str(d.get("descricao_situacao_cadastral", "")).upper()
            razao = str(d.get("razao_social", ""))
            cap_raw = str(d.get("capital_social", 0)).replace(",", ".")
            capital = float(cap_raw) if cap_raw else 0.0

            if "ATIVA" in sit and capital >= capital_minimo:
              return c, razao, capital, sit
        except Exception:
          pass
        return None

      with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(testar_cnpj, c): c for c in alvos[:500]}
        concluidos = 0
        total = len(futures)

        for future in as_completed(futures):
          concluidos += 1
          res = future.result()
          if res:
            aprovados.append(res)
          barra_triagem.progress(concluidos / total)

      if aprovados:
        st.success(
            f"Varredura concluída! Encontrados {len(aprovados)} ativos"
            " qualificados."
        )
        for ap in aprovados:
          st.code(
              f"CNPJ: {ap[0]} | RAZÃO: {ap[1]} | CAPITAL: R$ {ap[2]:,.2f}"
          )
      else:
        st.warning(
            "Nenhum CNPJ correspondeu aos critérios rigorosos nesta amostra."
        )
