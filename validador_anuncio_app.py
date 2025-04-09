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
import base64

PALAVRAS_CHAVE = ["tênis", "mochila", "smartphone", "calça", "notebook", "sapato", "jaqueta"]

st.set_page_config(page_title="Validador de Anúncios", layout="centered")
st.title("🔎 Validador de Anúncios de Marketplace")

st.markdown("""
Este app analisa a qualidade de anúncios em marketplaces como Mercado Livre, Shopee e Amazon, baseado em critérios como título, SEO, imagens, descrições, vídeos e avaliações.
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
