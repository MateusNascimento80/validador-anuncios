import requests
from bs4 import BeautifulSoup

def get_autocomplete_keywords(query):
    url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        suggestions = []
        for item in soup.select("a.ui-search-link__title-card, a.ui-search-item__group__element"):
            text = item.get_text(strip=True).lower()
            if text and query.lower() in text:
                suggestions.append(text)

        return list(set(suggestions))[:10]

    except Exception as e:
        print(f"[Erro get_autocomplete_keywords] {e}")
        return []
