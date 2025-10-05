import os
from newspaper import Article
from playwright.sync_api import sync_playwright

def extrair_texto(url: str):
    if url.startswith("file://"):
        caminho = url.replace("file://", "")
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()
        artigo = Article(url, language='pt')
        artigo.set_html(html)
        artigo.parse()
        return artigo.title, artigo.text

    try:
        artigo = Article(url, language='pt')
        artigo.download()
        artigo.parse()
        print("✅ Extração bem-sucedida com Newspaper3k.")
        return artigo.title, artigo.text

    except Exception as e:
        print(f"⚠️ Newspaper3k falhou: {e}\nTentando com Playwright...")

        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                html = page.content()
                browser.close()

            artigo = Article(url, language='pt')
            artigo.set_html(html)
            artigo.parse()

            print("✅ Extração bem-sucedida com Playwright.")
            return artigo.title, artigo.text

        except Exception as e2:
            raise RuntimeError(f"Falha total ao extrair conteúdo da URL ({url}): {e2}")

