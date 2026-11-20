import re
import time

try:
    from .busca import (
        IGNORADAS,
        buscar_por_id,
        buscar_por_palavras_chave,
        buscar_por_tema,
        listar_temas,
        normalizar,
        temas_relacionados,
    )
except ImportError:
    from busca import (
        IGNORADAS,
        buscar_por_id,
        buscar_por_palavras_chave,
        buscar_por_tema,
        listar_temas,
        normalizar,
        temas_relacionados,
    )


AVISO_NAO_OFICIAL = (
    "Aviso: Este assistente tem caráter exclusivamente informativo e não substitui "
    "canais oficiais. Confirme prazos e requisitos atualizados na fonte indicada."
)

AVISO_PRIVACIDADE = (
    "Alerta de Privacidade (LGPD): Detectamos uma sequência numérica semelhante a um CPF "
    "ou documento pessoal. Por segurança, não informe dados pessoais aqui — este sistema "
    "não coleta nem armazena informações individuais."
)

# ==============================================================================
#                 MODELOS DE PROMPT / INSTRUÇÃO DOCUMENTADOS
# ==============================================================================
MODELOS_PROMPT = {
    "objetivo": {
        "nome": "Modelo 1 — Assistente Objetivo (Direto ao Ponto)",
        "papel": "Assistente informativo cidadão focado em respostas curtas e imediatas.",
        "instrucoes": (
            "1. Responda exclusivamente com base no registro recuperado da base verificada.\n"
            "2. Apresente a orientação em formato compacto, sem rodeios.\n"
            "3. Cite obrigatoriamente a fonte oficial e a data de verificação.\n"
            "4. Inclua aviso curto de que o sistema não é canal oficial.\n"
            "5. Se não houver correspondência na base, recuse-se a inventar instruções."
        ),
    },
    "didatico": {
        "nome": "Modelo 2 — Assistente Didático e Acessível (Guiado)",
        "papel": "Orientador cidadão acolhedor que traduz serviços públicos em linguagem clara.",
        "instrucoes": (
            "1. Contextualize o tema e reformule a dúvida atendida para confirmar o entendimento.\n"
            "2. Apresente a orientação de forma estruturada e acessível ao cidadão.\n"
            "3. Destaque a fonte oficial, a data de verificação e recomendações de conferência.\n"
            "4. Sugira até 2 temas relacionados da base para continuidade da consulta.\n"
            "5. Nunca solicite dados pessoais e deixe explícitos os limites do assistente."
        ),
    },
}


def _contem_dado_pessoal(texto):
    """Guardrail simples para detectar padrão de CPF (11 dígitos com ou sem pontuação)."""
    if not isinstance(texto, str):
        return False
    return bool(re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", texto))


def _sanitizar_consulta(texto):
    """Remove possíveis números de documentos antes de processar a busca."""
    return re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "", texto).strip()


def _classificar_entrada(consulta):
    """Valida se a entrada é vazia, composta só por símbolos ou vaga demais."""
    if not isinstance(consulta, str) or not consulta.strip():
        return "vazia"
    normalizada = normalizar(consulta)
    if not normalizada:
        return "invalida"
    termos_uteis = set(normalizada.split()) - IGNORADAS
    if not termos_uteis:
        return "vaga"
    return "valida"


def _formatar_resposta_objetiva(registro, relacionados):
    """Aplica o template do Modelo 1 (Objetivo) sobre um registro verificado."""
    linhas = [
        f"[{registro['tema']}] {registro['pergunta']}",
        f"Orientação: {registro['orientacao']}",
        f"Fonte oficial: {registro['fonte']} (Verificado em: {registro['data_verificacao']})",
        AVISO_NAO_OFICIAL,
    ]
    if relacionados:
        sugestoes = ", ".join(r["tema"] for r in relacionados)
        linhas.append(f"Assuntos relacionados: {sugestoes}.")
    return "\n".join(linhas)


def _formatar_resposta_didatica(registro, relacionados):
    """Aplica o template do Modelo 2 (Didático e Acessível) sobre um registro verificado."""
    bloco = [
        "=" * 68,
        f"TEMA: {registro['tema'].upper()}  |  REGISTRO #{registro['id']}",
        f"Dúvida atendida: {registro['pergunta']}",
        "-" * 68,
        "COMO PROCEDER:",
        f"  {registro['orientacao']}",
        "",
        "CONFIABILIDADE E FONTE:",
        f"  • Canal oficial: {registro['fonte']}",
        f"  • Última verificação da equipe: {registro['data_verificacao']}",
        f"  • {AVISO_NAO_OFICIAL}",
    ]
    if relacionados:
        bloco.append("")
        bloco.append("PARA CONTINUAR SUA CONSULTA (TEMAS RELACIONADOS):")
        for rel in relacionados:
            bloco.append(f"  -> {rel['tema']}: {rel['motivo']}")
    bloco.append("=" * 68)
    return "\n".join(bloco)


def formatar_registro(registro, base, modelo="didatico"):
    """Formata um único registro conforme o modelo de prompt escolhido."""
    if modelo not in MODELOS_PROMPT:
        raise ValueError(f"Modelo de prompt inválido: '{modelo}'. Use 'objetivo' ou 'didatico'.")
    relacionados = temas_relacionados(base, registro["tema"])
    if modelo == "objetivo":
        return _formatar_resposta_objetiva(registro, relacionados)
    return _formatar_resposta_didatica(registro, relacionados)


def responder_consulta(base, consulta, modelo="didatico", tema=None):
    """Processa uma consulta cidadã de ponta a ponta (RAG determinístico + Guardrails).

    Retorna um dicionário estruturado para exibição na interface e coleta de métricas
    na etapa de testes (Parte 4):
      - status: 'sucesso', 'ambiguo', 'sem_resultado' ou 'entrada_invalida'
      - modelo_prompt: 'objetivo' ou 'didatico'
      - resposta_formatada: texto final pronto para exibição
      - registros_encontrados: lista de dicionários retornados pela busca
      - id_principal: ID do primeiro registro correspondente (ou None)
      - temas_relacionados: sugestões de continuidade no grafo de temas
      - alerta_privacidade: bool indicando se houve bloqueio preventivo de CPF
      - tempo_ms: tempo de processamento da consulta em milissegundos
    """
    inicio = time.perf_counter()

    if modelo not in MODELOS_PROMPT:
        raise ValueError(f"Modelo de prompt inválido: '{modelo}'. Use 'objetivo' ou 'didatico'.")

    alerta_privacidade = _contem_dado_pessoal(consulta) if isinstance(consulta, str) else False
    consulta_limpa = _sanitizar_consulta(consulta) if isinstance(consulta, str) else ""
    estado_entrada = _classificar_entrada(consulta_limpa)
    temas_disponiveis = ", ".join(listar_temas(base))

    # tratamento de entradas vazias, inválidas ou muito vagas
    if estado_entrada != "valida":
        mensagens = {
            "vazia": "Nenhuma pergunta foi digitada. Por favor, escreva sua dúvida ou escolha um tema no menu.",
            "invalida": "Não foi possível identificar palavras válidas na sua entrada. Evite enviar apenas símbolos.",
            "vaga": (
                "Sua consulta ficou muito genérica para localizar uma orientação segura. "
                "Tente incluir o nome do documento, serviço ou direito (ex.: 'consultar CPF', 'CadÚnico', 'Procon')."
            ),
        }
        corpo = f"{mensagens[estado_entrada]}\nTemas disponíveis na base: {temas_disponiveis}."
        if alerta_privacidade:
            corpo = f"{AVISO_PRIVACIDADE}\n\n{corpo}"
        tempo_ms = (time.perf_counter() - inicio) * 1000
        return {
            "status": "entrada_invalida",
            "modelo_prompt": modelo,
            "resposta_formatada": corpo,
            "registros_encontrados": [],
            "id_principal": None,
            "temas_relacionados": [],
            "alerta_privacidade": alerta_privacidade,
            "tempo_ms": round(tempo_ms, 4),
        }

    # busca na base de conhecimento verificada
    resultados = buscar_por_palavras_chave(base, consulta_limpa, tema=tema)

    # tratamento de ausência de correspondência (limite transparente)
    if not resultados:
        escopo = f" no tema '{tema}'" if tema else ""
        corpo = (
            f"Não encontrei orientações verificadas{escopo} para '{consulta_limpa}' na minha base atual.\n"
            "Para manter a confiabilidade, não gero respostas sem fonte comprovada.\n"
            f"Sugestão: tente reformular com palavras-chave mais diretas ou explore os temas disponíveis: {temas_disponiveis}."
        )
        if alerta_privacidade:
            corpo = f"{AVISO_PRIVACIDADE}\n\n{corpo}"
        tempo_ms = (time.perf_counter() - inicio) * 1000
        return {
            "status": "sem_resultado",
            "modelo_prompt": modelo,
            "resposta_formatada": corpo,
            "registros_encontrados": [],
            "id_principal": None,
            "temas_relacionados": [],
            "alerta_privacidade": alerta_privacidade,
            "tempo_ms": round(tempo_ms, 4),
        }

    # montagem da resposta (correspondência única ou múltipla/ambígua)
    principal = resultados[0]
    relacionados = temas_relacionados(base, principal["tema"])
    resposta_principal = formatar_registro(principal, base, modelo=modelo)

    if len(resultados) == 1:
        status = "sucesso"
        corpo = resposta_principal
    else:
        status = "ambiguo"
        outras_opcoes = "\n".join(
            f"  - [ID {r['id']}] ({r['tema']}) {r['pergunta']}" for r in resultados[1:]
        )
        corpo = (
            f"Encontrei {len(resultados)} orientações relacionadas à sua busca. "
            "Exibindo a mais relevante primeiro:\n\n"
            f"{resposta_principal}\n\n"
            "Outras orientações encontradas (você pode consultar pelo ID no menu para ver detalhes):\n"
            f"{outras_opcoes}"
        )

    if alerta_privacidade:
        corpo = f"{AVISO_PRIVACIDADE}\n\n{corpo}"

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return {
        "status": status,
        "modelo_prompt": modelo,
        "resposta_formatada": corpo,
        "registros_encontrados": resultados,
        "id_principal": principal["id"],
        "temas_relacionados": relacionados,
        "alerta_privacidade": alerta_privacidade,
        "tempo_ms": round(tempo_ms, 4),
    }


def consultar_por_id_assistente(base, identificador, modelo="didatico"):
    """Consulta direta por ID formatada com o modelo de prompt ativo."""
    inicio = time.perf_counter()
    registro = buscar_por_id(base, identificador)
    if not registro:
        temas_disponiveis = ", ".join(listar_temas(base))
        tempo_ms = (time.perf_counter() - inicio) * 1000
        return {
            "status": "sem_resultado",
            "modelo_prompt": modelo,
            "resposta_formatada": (
                f"Nenhum registro encontrado para o ID '{identificador}'. "
                f"Informe um número válido (ex.: 1 a {len(base)}) ou navegue pelos temas: {temas_disponiveis}."
            ),
            "registros_encontrados": [],
            "id_principal": None,
            "temas_relacionados": [],
            "alerta_privacidade": False,
            "tempo_ms": round(tempo_ms, 4),
        }

    relacionados = temas_relacionados(base, registro["tema"])
    tempo_ms = (time.perf_counter() - inicio) * 1000
    return {
        "status": "sucesso",
        "modelo_prompt": modelo,
        "resposta_formatada": formatar_registro(registro, base, modelo=modelo),
        "registros_encontrados": [registro],
        "id_principal": registro["id"],
        "temas_relacionados": relacionados,
        "alerta_privacidade": False,
        "tempo_ms": round(tempo_ms, 4),
    }