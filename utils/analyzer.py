import re
import sys
import time
from unicodedata import normalize
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# Cache global para modelos (evita recarregar toda vez)
_modelo_semantico = None
_modelo_resumo = None

# ---------- Funções auxiliares ----------
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

def encontrar_trecho(texto, termo, contexto=500):
    """Retorna um trecho grande e contextualizado em torno do termo."""
    padrao = re.compile(rf".{{0,{contexto}}}\b{re.escape(termo)}\b.{{0,{contexto}}}", re.IGNORECASE)
    match = padrao.search(texto)
    return match.group(0).strip() if match else None

# ---------- Carregamento preguiçoso ----------
def get_modelo_semantico():
    """Carrega o modelo semântico apenas uma vez."""
    global _modelo_semantico
    if _modelo_semantico is None:
        print("\n🧠 Carregando modelo de similaridade semântica (SentenceTransformer)...")
        inicio = time.time()
        _modelo_semantico = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print(f"✅ Modelo semântico carregado em {round(time.time() - inicio, 2)}s.\n")
    return _modelo_semantico

def get_modelo_resumo():
    """Carrega o modelo de resumo apenas uma vez."""
    global _modelo_resumo
    if _modelo_resumo is None:
        print("\n📝 Carregando modelo de resumo automático (T5 Unicamp)...")
        inicio = time.time()
        _modelo_resumo = pipeline("summarization", model="unicamp-dl/ptt5-base-portuguese-vocab")
        print(f"✅ Modelo de resumo carregado em {round(time.time() - inicio, 2)}s.\n")
    return _modelo_resumo

# ---------- Consolidação de trechos ----------
def consolidar_trechos(trechos, similaridade_min=0.80):
    """Une trechos parecidos em um único texto."""
    if not trechos:
        return ""
    modelo_semantico = get_modelo_semantico()
    unicos = []
    emb_trechos = modelo_semantico.encode(trechos, convert_to_tensor=True)

    for i, trecho in enumerate(trechos):
        eh_similar = False
        for unico in unicos:
            emb_unico = modelo_semantico.encode(unico, convert_to_tensor=True)
            sim = float(util.cos_sim(emb_trechos[i], emb_unico))
            if sim >= similaridade_min:
                eh_similar = True
                break
        if not eh_similar:
            unicos.append(trecho)

    return "\n\n".join(unicos).strip()

# ---------- Geração de resumo ----------
def gerar_resumo(texto: str, max_palavras: int = 150):
    """Gera um resumo em português do texto consolidado."""
    if not texto or len(texto.strip()) < 80:
        return "Texto muito curto para gerar um resumo."

    modelo_resumo = get_modelo_resumo()

    try:
        resumo = modelo_resumo(texto, max_length=max_palavras * 2, min_length=80, do_sample=False)
        return resumo[0]["summary_text"].strip()
    except Exception as e:
        return f"⚠️ Erro ao gerar resumo: {e}"

# ---------- Função de busca ----------
def buscar_combinacoes_semanticas(texto, combinacoes):
    modelo_semantico = get_modelo_semantico()
    texto_norm = normalizar(texto)
    resultados = {}
    total_tokens = len(texto_norm.split())
    frases = [f.strip() for f in texto.split(".") if len(f.strip()) > 20]
    todos_trechos = []

    for combo in combinacoes:
        combo_norm = [normalizar(c) for c in combo]
        score_textual = 0
        score_semantico = 0
        trechos = []

        # --- Busca literal ---
        posicoes = []
        for termo in combo_norm:
            padrao = re.compile(rf"\b{re.escape(termo)}\b")
            for m in padrao.finditer(texto_norm):
                posicoes.append((termo, m.start()))
                trecho = encontrar_trecho(texto, termo, contexto=600)
                if trecho:
                    trechos.append(trecho)
                    todos_trechos.append(trecho)

        # --- Score literal ---
        if len(posicoes) > 1:
            pos_ordenadas = sorted([p[1] for p in posicoes])
            distancias = [abs(pos_ordenadas[i] - pos_ordenadas[i-1]) for i in range(1, len(pos_ordenadas))]
            media_dist = sum(distancias) / len(distancias) if distancias else 0
            score_textual = max(0, 100 - (media_dist / total_tokens * 100))
        elif len(posicoes) == 1:
            score_textual = 90
        else:
            score_textual = 0

        # --- Score semântico ---
        alvo = " ".join(combo_norm)
        emb_alvo = modelo_semantico.encode(alvo, convert_to_tensor=True)
        maior_sim = 0.0
        frase_mais_similar = None

        for frase in frases:
            emb_frase = modelo_semantico.encode(frase, convert_to_tensor=True)
            similaridade = float(util.cos_sim(emb_alvo, emb_frase))
            if similaridade > maior_sim:
                maior_sim = similaridade
                frase_mais_similar = frase

        score_semantico = round(maior_sim * 100, 2)
        if frase_mais_similar and frase_mais_similar not in trechos:
            trechos.append(frase_mais_similar)
            todos_trechos.append(frase_mais_similar)

        score_final = round(max(score_textual, score_semantico), 2)

        resultados[" ".join(combo)] = {
            "score_textual": round(score_textual, 2),
            "score_semantico": round(score_semantico, 2),
            "score_final": score_final,
            "trechos": trechos
        }

    texto_consolidado = consolidar_trechos(todos_trechos)
    return resultados, texto_consolidado

# ---------- Função principal ----------
def analisar_texto_com_score(texto, combinacoes):
    resultados, texto_consolidado = buscar_combinacoes_semanticas(texto, combinacoes)
    scores = [r["score_final"] for r in resultados.values()]
    media_relevancia = round(sum(scores) / len(scores), 2) if scores else 0
    resumo_final = gerar_resumo(texto_consolidado)

    return {
        "relevancia_geral": media_relevancia,
        "detalhes": resultados,
        "texto_consolidado": texto_consolidado,
        "resumo": resumo_final
    }

