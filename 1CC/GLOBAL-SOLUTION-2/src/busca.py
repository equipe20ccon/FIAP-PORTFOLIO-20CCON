import json
import re
import unicodedata
from pathlib import Path

CAMINHO_BASE = Path(__file__).resolve().parent.parent / "temas.json"
CAMPOS = ("id", "tema", "pergunta", "palavras_chave", "orientacao",
          "fonte", "data_verificacao")
IGNORADAS = set("a o as os um uma de da do das dos e em no na nos nas "
                "para por com contra como qual quais que eu meu minha quero preciso "
                "saber sobre posso fazer consultar consulta acessar solicitar "
                "informacoes".split())

# Grafo não direcionado: cada tema está ligado aos outros dois.
# Os motivos permitem explicar ao usuário a continuidade sugerida.
RELACOES = {
    "Documentação": {
        "Serviços Públicos": "Documentos são utilizados para acessar serviços e benefícios.",
        "Direitos e Orientações": "Documentos ajudam no exercício de direitos e em solicitações.",
    },
    "Serviços Públicos": {
        "Documentação": "O acesso a serviços pode exigir identificação e cadastro.",
        "Direitos e Orientações": "O atendimento público envolve direitos e orientações ao cidadão.",
    },
    "Direitos e Orientações": {
        "Documentação": "Solicitações e reclamações podem exigir documentos.",
        "Serviços Públicos": "Serviços públicos são meios para exercer direitos.",
    },
}


def normalizar(texto):
    """Ignora caixa, acentos, pontuação e espaços repetidos."""
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", texto))


def carregar_base(caminho=CAMINHO_BASE):
    """Retorna uma lista de dicionários; falhas de leitura geram ValueError."""
    try:
        with open(caminho, encoding="utf-8-sig") as arquivo:
            registros = json.load(arquivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ValueError(f"Não foi possível carregar a base: {erro}") from erro
    if not isinstance(registros, list) or not registros:
        raise ValueError("A base deve ser uma lista não vazia de registros.")
    ids = set()
    for posicao, registro in enumerate(registros, start=1):
        if not isinstance(registro, dict) or any(c not in registro for c in CAMPOS):
            raise ValueError(f"Registro {posicao}: campos obrigatórios ausentes.")
        identificador = registro["id"]
        if type(identificador) is not int or identificador < 1 or identificador in ids:
            raise ValueError(f"Registro {posicao}: ID inválido ou repetido.")
        ids.add(identificador)
        for campo in CAMPOS[1:]:
            valor = registro[campo]
            if campo == "palavras_chave":
                valido = (isinstance(valor, list) and bool(valor)
                          and all(isinstance(p, str) and p.strip() for p in valor))
            else:
                valido = isinstance(valor, str) and bool(valor.strip())
            if not valido:
                raise ValueError(f"Registro {identificador}: campo {campo} inválido.")
    return registros


def listar_temas(base):
    """Lista temas na ordem em que aparecem no JSON, sem repetições."""
    return list(dict.fromkeys(registro["tema"] for registro in base))


def buscar_por_id(base, identificador):
    """Aceita inteiro ou texto numérico; retorna registro ou None."""
    if type(identificador) is int:
        numero = identificador
    elif isinstance(identificador, str) and re.fullmatch(r"[0-9]+", identificador.strip()):
        numero = int(identificador.strip())
    else:
        return None
    indice = {registro["id"]: registro for registro in base}
    return indice.get(numero)


def buscar_por_tema(base, tema):
    """Compara o nome completo do tema, ignorando acentos e caixa."""
    if not isinstance(tema, str) or not normalizar(tema):
        return []
    return [r for r in base if normalizar(r["tema"]) == normalizar(tema)]


def buscar_por_palavras_chave(base, consulta, tema=None):
    """Busca lexical: mais palavras relevantes em comum vêm primeiro.

    Retorna registros completos, preservando fonte e orientação para a interface.
    Um filtro opcional restringe a busca ao tema selecionado.
    """
    if not isinstance(consulta, str):
        return []
    termos = set(normalizar(consulta).split()) - IGNORADAS
    if not termos:
        return []
    candidatos = base if tema is None else buscar_por_tema(base, tema)
    encontrados = []
    for registro in candidatos:
        correspondencias = set()
        for palavra_chave in registro["palavras_chave"]:
            palavras = set(normalizar(palavra_chave).split()) - IGNORADAS
            # Exige os termos relevantes de cada expressão composta.
            # Assim, "receita de bolo" não corresponde a "receita federal".
            if palavras and palavras.issubset(termos):
                correspondencias.update(palavras)
        pontos = len(correspondencias)
        if pontos:
            encontrados.append((pontos, registro))
    encontrados.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [registro for pontos, registro in encontrados]


def temas_relacionados(base, tema):
    """Retorna lista de dicionários com tema e motivo da relação."""
    if not isinstance(tema, str):
        return []
    disponiveis = listar_temas(base)
    for origem, destinos in RELACOES.items():
        if normalizar(origem) == normalizar(tema) and origem in disponiveis:
            return [{"tema": destino, "motivo": motivo}
                    for destino, motivo in destinos.items() if destino in disponiveis]
    return []
