
# 🧠 Notícia Insight

Analisador inteligente de notícias com **extração de contexto**, **similaridade semântica** e **resumo automático em português**.

---

## 🚀 Funcionalidades

✅ Extrai o texto de uma notícia (web ou local)  
✅ Analisa termos e combinações com semelhança semântica  
✅ Gera trechos de contexto amplos  
✅ Consolida resultados sem repetição  
✅ Cria um resumo automático com IA (modelo T5 Unicamp)

---

## 🛠️ Tecnologias

- Python 3.12  
- [newspaper3k](https://github.com/codelucas/newspaper)  
- [Playwright](https://playwright.dev/python/)  
- [Sentence Transformers](https://www.sbert.net/)  
- [Transformers (Hugging Face)](https://huggingface.co/)  
- Torch, Protobuf, Tiktoken, Blobfile  

---

## ⚙️ Como usar

```bash
git clone https://github.com/seuusuario/noticia-insight.git
cd noticia-insight
python3 -m venv venv
source venv/bin/activate (se estiver usando Linux)
source venv\Scripts\activate (se estiver usando windows no CMD)
source venv\Scripts\Activate.ps1 (se estiver usando windows no PowerShell)
pip install -r requirements.txt
playwright install firefox
python3 main.py
