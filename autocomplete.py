# autocomplete.py

import requests

def get_autocomplete_keywords(base_keyword: str):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/autosuggest?showFilters=false&limit=10&q={base_keyword}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        suggestions = []
        for term in data.get("suggested_queries", []):
            suggestion = term.get("q")
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    except requests.exceptions.RequestException as e:
        print("Erro na requisição de autocomplete:", e)
        return []
    except Exception as e:
        print("Erro inesperado:", e)
        return []
