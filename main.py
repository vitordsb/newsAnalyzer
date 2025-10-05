
import json
from utils.scraper import extrair_texto
from utils.analyzer import analisar_texto_com_score

def main():
    print("\n🧠  ANALISADOR DE NOTÍCIAS INTELIGENTE\n")

    url = input("🔗 Cole a URL da notícia (ou file://samples/teste.html para teste): ").strip()

    print("\n💬 Digite os termos ou combinações de busca separados por vírgula.")
    print("   👉 Exemplo: pib subiu, inflação caiu, brasil 2025\n")

    busca_input = input("🔍 Termos: ").strip()

    combinacoes = []
    for item in busca_input.split(","):
        termos = item.strip().split()
        if termos:
            combinacoes.append(termos)

    print("\n🔎 Analisando...\n")

    titulo, texto = extrair_texto(url)
    resultado = analisar_texto_com_score(texto, combinacoes)

    saida = {
        "url": url,
        "titulo": titulo,
        **resultado
    }

    with open("saida.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=4)

    print("📰 Título:", titulo)
    print(f"📈 Relevância geral: {saida['relevancia_geral']}%\n")

    for combo, info in saida["detalhes"].items():
        score_final = info.get("score_final", 0)
        status = "✅ Encontrado" if score_final > 0 else "❌ Não encontrado"

        print(f" → {combo}: {status} | Score final: {score_final}%")
        print(f"    🔹 Textual: {info.get('score_textual', 0)}% | Semântico: {info.get('score_semantico', 0)}%")
        if info["trechos"]:
            print(f"    Trecho: {info['trechos'][0][:200]}...")
        print()

    print("🧩 Texto consolidado:")
    print("-" * 80)
    print(saida["texto_consolidado"])
    print("-" * 80)

    print("\n🧠 Resumo automático:")
    print("-" * 80)
    print(saida["resumo"])
    print("-" * 80)

    print("\n💾 Resultados completos salvos em 'saida.json'")

if __name__ == "__main__":
    main()

