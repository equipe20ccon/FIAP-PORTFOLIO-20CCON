import csv
import statistics
import time
from pathlib import Path

from src.busca import (
    buscar_por_id,
    buscar_por_palavras_chave,
    buscar_por_tema,
    carregar_base,
)

# Conjunto de 15 casos de teste abrangendo consultas diretas, variações de escrita,
# perguntas fora do assunto e os 3 cenários de limite obrigatórios.
CASOS_DE_TESTE = [
    # 1. Consultas diretas (6 casos)
    {
        "caso": 1,
        "categoria": "Direta",
        "metodo": "palavra_chave",
        "entrada": "Como consultar o CPF?",
        "esperado": "ID 1",
    },
    {
        "caso": 2,
        "categoria": "Direta",
        "metodo": "palavra_chave",
        "entrada": "Como emitir a CIN?",
        "esperado": "ID 2",
    },
    {
        "caso": 3,
        "categoria": "Direta",
        "metodo": "palavra_chave",
        "entrada": "Como se cadastrar no CadÚnico?",
        "esperado": "ID 6",
    },
    {
        "caso": 4,
        "categoria": "Direta",
        "metodo": "palavra_chave",
        "entrada": "Como solicitar o seguro-desemprego?",
        "esperado": "ID 15",
    },
    {
        "caso": 5,
        "categoria": "Direta",
        "metodo": "id",
        "entrada": "9",
        "esperado": "ID 9",
    },
    {
        "caso": 6,
        "categoria": "Direta",
        "metodo": "tema",
        "entrada": "Documentação",
        "esperado": "5 registros",
    },
    # 2. Variações de escrita: sem acento, caixa alta/baixa, reformulações (3 casos)
    {
        "caso": 7,
        "categoria": "Variação de escrita",
        "metodo": "palavra_chave",
        "entrada": "SITUAÇÃO CADASTRAL CPF",
        "esperado": "ID 1",
    },
    {
        "caso": 8,
        "categoria": "Variação de escrita",
        "metodo": "palavra_chave",
        "entrada": "titulo de eleitor regularizacao",
        "esperado": "ID 4",
    },
    {
        "caso": 9,
        "categoria": "Variação de escrita",
        "metodo": "palavra_chave",
        "entrada": "credencial de estacionamento para pessoa idosa",
        "esperado": "ID 10",
    },
    # 3. Perguntas fora do assunto (2 casos)
    {
        "caso": 10,
        "categoria": "Fora do assunto",
        "metodo": "palavra_chave",
        "entrada": "Como preparar uma receita de bolo de chocolate?",
        "esperado": "Vazio",
    },
    {
        "caso": 11,
        "categoria": "Fora do assunto",
        "metodo": "palavra_chave",
        "entrada": "Qual a previsão do tempo para amanhã?",
        "esperado": "Vazio",
    },
    # 4. Cenários de limite obrigatórios (4 casos)
    {
        "caso": 12,
        "categoria": "Limite (Entrada vazia)",
        "metodo": "palavra_chave",
        "entrada": "   ",
        "esperado": "Vazio",
    },
    {
        "caso": 13,
        "categoria": "Limite (Consulta vaga/stopwords)",
        "metodo": "palavra_chave",
        "entrada": "como posso consultar",
        "esperado": "Vazio",
    },
    {
        "caso": 14,
        "categoria": "Limite (Consulta ambígua)",
        "metodo": "palavra_chave",
        "entrada": "denúncia",
        "esperado": "IDs [11, 12, 13]",
    },
    {
        "caso": 15,
        "categoria": "Limite (Sem base confiável)",
        "metodo": "palavra_chave",
        "entrada": "Como tirar passaporte de emergência na Polícia Federal?",
        "esperado": "Vazio",
    },
]


def executar_consulta(base: list[dict], caso: dict) -> list[dict]:
    metodo = caso["metodo"]
    entrada = caso["entrada"]
    if metodo == "id":
        registro = buscar_por_id(base, entrada)
        return [registro] if registro else []
    if metodo == "tema":
        return buscar_por_tema(base, entrada)
    return buscar_por_palavras_chave(base, entrada)


def formatar_obtido(resultados: list[dict]) -> str:
    if not resultados:
        return "Vazio"
    ids = [r["id"] for r in resultados]
    if len(ids) == 1:
        return f"ID {ids[0]}"
    return f"IDs {ids}"


def verificar_acerto(caso: dict, resultados: list[dict]) -> tuple[bool, str]:
    esperado = caso["esperado"]
    obtido = formatar_obtido(resultados)

    if esperado == "Vazio":
        return obtido == "Vazio", obtido
    if esperado == "5 registros":
        return len(resultados) == 5, f"{len(resultados)} registros"
    if esperado.startswith("ID "):
        id_esperado = int(esperado.split()[1])
        acertou = len(resultados) > 0 and resultados[0]["id"] == id_esperado
        return acertou, obtido
    if esperado.startswith("IDs "):
        return obtido == esperado, obtido
    return False, obtido


def main() -> None:
    base = carregar_base()
    registros_saida = []
    tempos_ms = []

    for caso in CASOS_DE_TESTE:
        inicio = time.perf_counter()
        resultados = executar_consulta(base, caso)
        duracao_ms = round((time.perf_counter() - inicio) * 1000, 4)
        tempos_ms.append(duracao_ms)

        acertou, obtido = verificar_acerto(caso, resultados)
        registros_saida.append(
            {
                "caso": caso["caso"],
                "categoria": caso["categoria"],
                "metodo": caso["metodo"],
                "entrada": repr(caso["entrada"]),
                "esperado": caso["esperado"],
                "obtido": obtido,
                "status": "ACERTO" if acertou else "ERRO",
                "tempo_ms": duracao_ms,
            }
        )

    total = len(registros_saida)
    acertos = sum(1 for item in registros_saida if item["status"] == "ACERTO")
    taxa_acerto = (acertos / total) * 100 if total else 0.0
    tempo_medio_ms = statistics.mean(tempos_ms) if tempos_ms else 0.0

    caminho_csv = Path(__file__).resolve().parent / "resultados_parte4.csv"
    with caminho_csv.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=list(registros_saida[0].keys()))
        writer.writeheader()
        writer.writerows(registros_saida)

    print("=== RELATÓRIO DE AVALIAÇÃO - PARTE 4 ===")
    print(f"Total de casos executados : {total}")
    print(f"Total de acertos          : {acertos}/{total}")
    print(f"Taxa de acerto            : {taxa_acerto:.1f}%")
    print(f"Tempo médio de busca      : {tempo_medio_ms:.4f} ms")
    print(f"Relatório CSV gerado em   : {caminho_csv}")


if __name__ == "__main__":
    main()