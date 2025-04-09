# validador_anuncio_app.py

import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urlparse
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt
import seaborn as sns

PALAVRAS_CHAVE = ["tênis", "mochila", "smartphone", "calça", "notebook", "sapato", "jaqueta"]

st.set_page_config(page_title="Validador de Anúncios", layout="centered")
st.title("🔎 Validador de Anúncios de Marketplace")

st.markdown("""
Este app analisa a qualidade de anúncios em marketplaces como Mercado Livre, Shopee e Amazon, baseado em critérios como título, SEO, imagens, descrições, vídeos e avaliações.
\"\"\")

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

def gerar_grafico_barras(pontuacoes, nomes):
    fig, ax = plt.subplots()
    sns.barplot(x=nomes, y=pontuacoes, palette="Blues_d", ax=ax)
    ax.set_title("Pontuação Total por Anúncio")
    ax.set_ylabel("Pontuação")
    ax.set_ylim(0, 8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer
def gerar_pdf_comparativo_multiplos(resultados, nomes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Relatório Comparativo de Anúncios</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    colunas = ["Critério"] + nomes
    data = [colunas]
    categorias = {
        "📌 Título e SEO": ["Tem título", "Título SEO (40-80 chars)", "Título com palavra-chave"],
        "🖼️ Conteúdo Visual": ["Quantidade de imagens", "Tem vídeo"],
        "📝 Descrição": ["Tem descrição", "Tem bullet points"],
        "⭐ Avaliações": ["Tem avaliações", "Nota média", "Total de avaliações"],
        "📊 Pontuação": ["Pontuação total"]
    }
    for categoria, itens in categorias.items():
        data.append([categoria] + ["" for _ in resultados])
        for crit in itens:
            linha = [crit] + [str(r[crit]) for r in resultados]
            data.append(linha)

    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1'))
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    pontuacoes = [int(r['Pontuação total'].split("/")[0]) for r in resultados]
    img_buffer = gerar_grafico_barras(pontuacoes, nomes)
    img = Image(img_buffer, width=400, height=250)
    elements.append(Paragraph("<b>Gráfico: Pontuação Total por Anúncio</b>", styles['Heading2']))
    elements.append(img)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def analisar_anuncio(url):
    return {
        "Tem título": True,
        "Título SEO (40-80 chars)": True,
        "Título com palavra-chave": True,
        "Quantidade de imagens": 5,
        "Tem vídeo": False,
        "Tem descrição": True,
        "Tem bullet points": True,
        "Tem avaliações": True,
        "Nota média": 4.7,
        "Total de avaliações": 123,
        "Pontuação total": "7/8"
    }

# 👇 Interface principal
st.markdown("## 🔄 Comparar múltiplos anúncios")
urls_text = st.text_area("Cole as URLs (uma por linha)")
if st.button("Comparar todos") and urls_text:
    urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
    resultados = []
    nomes = []
    with st.spinner("Analisando os anúncios..."):
        for i, url in enumerate(urls):
            resultado = analisar_anuncio(url)  # aqui entraria sua função real
            resultados.append(resultado)
            nomes.append(f"Anúncio {i+1}")

    if len(resultados) == len(urls):
        st.markdown("### 🧾 Comparativo por Categorias")
        categorias = {
            "📌 Título e SEO": ["Tem título", "Título SEO (40-80 chars)", "Título com palavra-chave"],
            "🖼️ Conteúdo Visual": ["Quantidade de imagens", "Tem vídeo"],
            "📝 Descrição": ["Tem descrição", "Tem bullet points"],
            "⭐ Avaliações": ["Tem avaliações", "Nota média", "Total de avaliações"],
            "📊 Pontuação": ["Pontuação total"]
        }
        full_df = pd.DataFrame()
        for cat, itens in categorias.items():
            st.subheader(cat)
            df_cat = pd.DataFrame({n: [r[i] for i in itens] for n, r in zip(nomes, resultados)}, index=itens)
            st.dataframe(df_cat)
            full_df = pd.concat([full_df, df_cat])

        st.subheader("📊 Resultado final:")
        pontuacoes = [int(r['Pontuação total'].split("/")[0]) for r in resultados]
        melhor = pontuacoes.index(max(pontuacoes))
        st.success(f"🏆 {nomes[melhor]} venceu com {pontuacoes[melhor]} pontos!")

        st.subheader("📈 Gráfico: Pontuação Total")
        grafico = gerar_grafico_barras(pontuacoes, nomes)
        st.image(grafico)

        csv_comparativo = full_df.to_csv().encode('utf-8')
        st.download_button("📄 Baixar CSV Comparativo", data=csv_comparativo, file_name="comparativo_anuncios.csv", mime='text/csv')

        pdf_buffer = gerar_pdf_comparativo_multiplos(resultados, nomes)
        st.download_button("📑 Baixar PDF Comparativo", data=pdf_buffer, file_name="comparativo_anuncios.pdf", mime='application/pdf')

# Rodapé com autoria
st.markdown("""
---
Desenvolvido por [**Mateus Nascimento**](https://www.linkedin.com/in/mateus-nascimento-6b918a4b/)
""", unsafe_allow_html=True)


