# validador_anuncio_app.py (com busca automática de palavras-chave via autocomplete do Mercado Livre)
from autocomplete import get_autocomplete_keywords
import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urlparse, quote
import pandas as pd

st.set_page_config(page_title="Validador de Anúncios", layout="centered")
st.title("🔎 Validador de Anúncios de Marketplace (Calçados)")

st.markdown("""
Este app analisa o título e a ficha técnica de um anúncio do Mercado Livre, e verifica se ele contém palavras-chave populares relacionadas ao termo buscado.
""")

def detectar_marketplace(url):
    dominio = urlparse(url).netloc
    if "mercadolivre" in dominio:
        return "mercadolivre"
    else:
        return "desconhecido"

def obter_autocomplete_ml(termo):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/autosuggest?showFilters=true&limit=20&q={quote(termo)}"
        res = requests.get(url)
        sugestoes = get_autocomplete_keywords(palavra_base)
        palavras = []
        for s in sugestoes:
            palavras += s.get("q", "").lower().split()
        return list(set(palavras))
    except:
        return []

def analisar_texto_com_palavras(texto, palavras):
    texto = texto.lower()
    presentes = [p for p in palavras if p in texto]
    ausentes = [p for p in palavras if p not in texto]
    return presentes, ausentes

def analisar_anuncio_mercadolivre(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo_tag = soup.find('h1', class_='ui-pdp-title')
        titulo = titulo_tag.text.strip() if titulo_tag else ""

        ficha = soup.find_all('tr', class_='andes-table__row')
        ficha_texto = " ".join([x.get_text(strip=True).lower() for x in ficha])

        texto_completo = (titulo + " " + ficha_texto).lower()
        return texto_completo, titulo

    except Exception as e:
        return "", ""

# Interface principal
st.markdown("## 🔗 Analisar anúncio")
url = st.text_input("Cole o link do anúncio do Mercado Livre")
termo_base = st.text_input("🔍 Palavra-chave base para autocomplete (ex: botina feminina)", "botina feminina")

if st.button("Validar") and url:
    marketplace = detectar_marketplace(url)
    if marketplace != "mercadolivre":
        st.warning("Por enquanto só analisamos anúncios do Mercado Livre.")
    else:
        st.info("🔄 Buscando sugestões de palavras-chave…")
        palavras_chave = obter_autocomplete_ml(termo_base)

        if not palavras_chave:
            st.error("❌ Não foi possível obter sugestões de palavras-chave.")
        else:
            st.success(f"✅ {len(palavras_chave)} palavras-chave coletadas!")
            st.write(palavras_chave)

            texto_anuncio, titulo = analisar_anuncio_mercadolivre(url)
            if not texto_anuncio:
                st.error("❌ Não foi possível extrair informações do anúncio.")
            else:
                presentes, ausentes = analisar_texto_com_palavras(texto_anuncio, palavras_chave)

                st.markdown("### 📌 Título do Anúncio:")
                st.write(titulo)

                st.markdown("### ✅ Palavras-chave encontradas no título ou ficha técnica:")
                st.success(", ".join(presentes) if presentes else "Nenhuma palavra-chave encontrada")

                st.markdown("### ❌ Palavras-chave ausentes:")
                st.warning(", ".join(ausentes) if ausentes else "Todas as palavras estão presentes!")

                st.markdown(f"### 📊 Cobertura: {len(presentes)} de {len(palavras_chave)} palavras-chave")

st.markdown("""
---
🧪 Este app utiliza autocomplete do Mercado Livre para validar presença de palavras-chave relevantes no título e ficha técnica de anúncios.\n
Desenvolvido por [**Mateus Nascimento**](https://www.linkedin.com/in/mateus-nascimento-6b918a4b/)
""", unsafe_allow_html=True)
