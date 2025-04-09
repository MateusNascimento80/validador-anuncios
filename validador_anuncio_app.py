# validador_anuncio_app.py (MVP Simplificado)

import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urlparse
import pandas as pd

PALAVRAS_CHAVE = ["tênis", "mochila", "smartphone", "calça", "notebook", "sapato", "jaqueta"]

st.set_page_config(page_title="Validador de Anúncios", layout="centered")
st.title("🔎 Validador de Anúncios de Marketplace (MVP)")

st.markdown("""
Este app analisa critérios básicos de anúncios em marketplaces como Mercado Livre.
Versão simplificada para MVP funcional: analisando título e quantidade de imagens.
""")

def detectar_marketplace(url):
    dominio = urlparse(url).netloc
    if "mercadolivre" in dominio:
        return "mercadolivre"
    elif "shopee" in dominio:
        return "shopee"
    elif "amazon" in dominio:
        return "amazon"
    else:
        return "desconhecido"

def analisar_anuncio_mercadolivre(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo_tag = soup.find('h1', class_='ui-pdp-title')
        titulo = titulo_tag.text.strip() if titulo_tag else "Não encontrado"
        num_imagens = len(soup.select('figure.ui-pdp-gallery__figure img'))

        return {
            "Título": titulo,
            "Título SEO (40-80 chars)": 40 <= len(titulo) <= 80,
            "Título com palavra-chave": any(p.lower() in titulo.lower() for p in PALAVRAS_CHAVE),
            "Quantidade de imagens": num_imagens,
            "Vídeo": "(não disponível)",
            "Avaliações": "(não disponível)",
            "Nota média": "(não disponível)",
        }
    except Exception as e:
        return {"Erro": str(e)}

st.markdown("## 🔗 Analisar anúncio")
url = st.text_input("Cole o link do anúncio do Mercado Livre")
if st.button("Validar") and url:
    marketplace = detectar_marketplace(url)
    if marketplace == "mercadolivre":
        resultado = analisar_anuncio_mercadolivre(url)
        st.subheader("📋 Resultado da Análise")
        st.json(resultado)
    else:
        st.warning("Por enquanto só analisamos anúncios do Mercado Livre.")

st.markdown("""
---
🧪 Versão simplificada para MVP funcional. Em breve: integração com Shopee, Amazon e melhorias com IA.\n
Desenvolvido por [**Mateus Nascimento**](https://www.linkedin.com/in/mateus-nascimento-6b918a4b/)
""", unsafe_allow_html=True)
