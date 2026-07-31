import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from backend import process_question


def test_pipeline():

    perguntas = [
        "Quantos pedidos existem na base?",
        "Quantos clientes únicos realizaram compras?",
        "Qual categoria possui mais produtos?",
    ]

    resultados = {"sucesso": 0, "falha": 0}

    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{'='*70}")
        print(f"  TESTE {i}/{len(perguntas)}: {pergunta}")
        print(f"{'='*70}")

        result = process_question(pergunta)

        if result["erro"]:
            print(f"  ❌ FALHA: {result['erro']}")
            resultados["falha"] += 1
        else:
            print(f"  ✅ SQL gerada:")
            # Indentar SQL
            for line in result["sql"].split("\n"):
                print(f"     {line}")

            print(f"\n  📊 Resultado ({len(result['resultado'])} linhas):")
            preview = result["resultado"].head(5).to_string(index=False)
            for line in preview.split("\n"):
                print(f"     {line}")

            resultados["sucesso"] += 1

    # Resumo
    total = resultados["sucesso"] + resultados["falha"]
    print(f"\n\n{'='*70}")
    print(f"  RESUMO: {resultados['sucesso']}/{total} testes passaram")
    if resultados["falha"] > 0:
        print(f"  ⚠️  {resultados['falha']} teste(s) falharam")
    else:
        print("  🎉 Todos os testes passaram!")
    print(f"{'='*70}")


if __name__ == "__main__":
    test_pipeline()
