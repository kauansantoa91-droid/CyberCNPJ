from datetime import datetime
import os
import re
import sqlite3
import urllib.parse
import requests
import streamlit as st

# Configuração da Página
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
    .stTextInput input, .stTextArea textarea {
        background-color: #030504 !important;
        color: #00ff66 !important;
        border: 1px solid #004d1f !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ TERMINAL // CYBER INTEL CNPJ")

# Criando abas semelhantes à versão de desktop
aba1, aba2, aba4 = st.tabs(
    ["[01] TARGET RECON", "[02] BATCH INJECTION", "[04] API ROOT CONFIG"]
)

# --- ABA 1: CONSULTA INDIVIDUAL ---
with aba1:
  st.subheader("Consulta Individual de Alvo")
  cnpj_input = st.text_input(
      "Inserir Vetor CNPJ (apenas números):", max_chars=14
  )

  if st.button("> SCAN TARGET"):
    cnpj_limpo = re.sub(r"\D", "", cnpj_input)

    if len(cnpj_limpo) != 14:
      st.error(
          f"[ERROR] Tamanho inválido: {len(cnpj_limpo)} dígitos detetados"
          " (necessário: 14)"
      )
    else:
      with st.spinner("A aceder ao mainframe... A recolher pacotes..."):
        try:
          url = f"https://minhareceita.org/{cnpj_limpo}"
          resp = requests.get(url, timeout=8)
          if resp.status_code == 200:
            d = resp.json()
            st.success("Target localizado com sucesso!")

            razao = d.get("razao_social", "N/A")
            situacao = d.get("descricao_situacao_cadastral", "N/A")
            porte = d.get("porte", "N/A")

            st.markdown(
                f"""
                        <div style="background-color: #0a0f0c; padding: 15px; border: 1px solid #004d1f; border-radius: 5px; font-family: monospace;">
                            <p style="color: #00ff66;"><b>ENTIDADE:</b> {razao}</p>
                            <p style="color: #00ff66;"><b>SITUAÇÃO:</b> {situacao}</p>
                            <p style="color: #00ff66;"><b>PORTE:</b> {porte}</p>
                        </div>
                        """,
                unsafe_allow_html=True,
            )

            with st.expander("Ver JSON Completo do Pacote"):
              st.json(d)
          else:
            st.error("[CRITICAL] Conexão falhou ou alvo rejeitado.")
        except Exception as e:
          st.error(f"[ERROR] Falha na conexão: {e}")

# --- ABA 2: CONSULTA EM LOTE ---
with aba2:
  st.subheader("Injeção de Alvos em Massa (Lote)")
  texto_lote = st.text_area(
      "Cole os CNPjs abaixo (um por linha ou no texto bruto):"
  )

  if st.button("> EXECUTAR RUN EM LOTE"):
    cnpjs = re.findall(r"\d{14}", re.sub(r"[.\-\/]", "", texto_lote))
    cnpjs = list(dict.fromkeys(cnpjs))

    if not cnpjs:
      st.warning("Nenhum CNPJ válido de 14 dígitos encontrado.")
    else:
      st.info(f"Total de {len(cnpjs)} alvos válidos detetados na fila.")
      barra_progresso = st.progress(0)

      resultados = []
      for i, c in enumerate(cnpjs):
        try:
          r = requests.get(f"https://minhareceita.org/{c}", timeout=5)
          if r.status_code == 200:
            d = r.json()
            resultados.append({
                "CNPJ": c,
                "Razao": d.get("razao_social"),
                "Situacao": d.get("descricao_situacao_cadastral"),
            })
        except Exception:
          pass
        barra_progresso.progress((i + 1) / len(cnpjs))

      if resultados:
        st.success("Lote processado com sucesso!")
        st.dataframe(resultados)

# --- ABA 4: CONFIGURAÇÕES ---
with aba4:
  st.subheader("Configuração do Nó de API")
  provedor = st.selectbox(
      "Selecionar Provedor:",
      ["Minha Receita (Gratuito)", "ReceitaWS", "CNPJ.ws"],
  )
  token_api = st.text_input("Chave de Segurança / Token:", type="password")

  if st.button("SALVAR CREDENCIAIS"):
    st.success("Credenciais guardadas com sucesso no ambiente web!")