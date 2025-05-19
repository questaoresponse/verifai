# import requests
# import urllib
# from newspaper import Article

# query = "java"
# url = f"https://google.com/?q={urllib.parse.quote(query)}&format=json"

# res = requests.get(url)
# data = res.text

# print(data)
# # Saída: Ol%C3%A1%2C%20mundo%21%20Python%20%26%20caf%C3%A9



# url = data["AbstractURL"]
# artigo = Article(url, language='pt')
# artigo.download()
# artigo.parse()

# print(artigo.title)
# print(artigo.text)

#newspaper3k lxml_html_clean

from playwright.sync_api import sync_playwright

query = "java"
url = f"https://duckduckgo.com/?q={query}&format=json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector(".conteudo")  # espera o carregamento
    html = page.content()
    browser.close()
