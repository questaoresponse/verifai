import requests
from bs4 import BeautifulSoup
import time
import re

def limpar_texto(texto):
    # Remove espaços extras e quebras de linha
    texto = re.sub(r'\s+', ' ', texto).strip()
    # Remove caracteres especiais
    texto = re.sub(r'[^\w\s.,!?-]', '', texto)
    return texto

def extrair_conteudo_pagina(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tenta encontrar o primeiro parágrafo relevante
        # Procura em várias tags onde normalmente está o conteúdo principal
        paragrafos = soup.find_all(['p', 'article', 'div.content', 'div.article-content'])
        primeiro_paragrafo = ""

        for p in paragrafos:
            texto = p.get_text().strip()
            if len(texto) > 100:  # Considera apenas parágrafos com mais de 100 caracteres
                primeiro_paragrafo = limpar_texto(texto)
                break

        return primeiro_paragrafo
    except Exception as e:
        return f"Erro ao extrair conteúdo: {str(e)}"

def buscar_duckduckgo(query, max_results=5):
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for result in soup.find_all('div', class_='result', limit=max_results):
        title_tag = result.find('a', class_='result__a')
        snippet_tag = result.find('a', class_='result__snippet')

        if title_tag:
            link = title_tag['href']
            title = limpar_texto(title_tag.get_text())
            snippet = limpar_texto(snippet_tag.get_text()) if snippet_tag else ''

            # Extrai conteúdo adicional da página
            print(f"Extraindo conteúdo de: {title}")
            conteudo = extrair_conteudo_pagina(link)

            results.append({
                'title': title,
                'link': link,
                'snippet': snippet,
                'conteudo': conteudo
            })

            # Pequena pausa para evitar sobrecarga
            time.sleep(1)

    return results

def mostrar_resultados(resultados):
    print("\nResultados encontrados:\n")
    print("-" * 80)
    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. {r['title']}")
        print(f"\nLink: {r['link']}")
        print(f"\nResumo: {r['snippet']}")
        print(f"\nConteúdo extraído: {r['conteudo'][:500]}...")  # Mostra os primeiros 500 caracteres
        print("\n" + "-" * 80)

# Interface para o usuário
query = input("Digite o que você quer pesquisar: ")
print("\nBuscando resultados... Por favor, aguarde.")

resultados = buscar_duckduckgo(query)
mostrar_resultados(resultados)
