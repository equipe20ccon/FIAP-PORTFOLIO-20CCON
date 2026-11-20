try:
    from .assistente import (
        MODELOS_PROMPT, 
        consultar_por_id_assistente,
        formatar_registro,
        responder_consulta
    )
    from .busca import (
        carregar_base,
        listar_temas,
        buscar_por_tema,
        temas_relacionados
    )
except ImportError:
    from assistente import (
            MODELOS_PROMPT, 
            consultar_por_id_assistente,
            formatar_registro,
            responder_consulta
        )
    from busca import (
            carregar_base,
            listar_temas,
            buscar_por_tema,
            temas_relacionados
        )

def aguardar_enter_menu():
    """Pausa antes de retornar ao menu principal."""
    input("\nPressione Enter para voltar ao menu principal...")

def exibir_cabecalho(modelo_atual):
    nome_modelo = MODELOS_PROMPT[modelo_atual]["nome"]
    print("\n" + "=" * 68)
    print("CITIZEN ASSIST AI - Orientação Cidadã Baseada em Fontes Verificadas")
    print("=" * 68)
    print("Privacidade: Não informe CPF, RG ou dados pessoais nas perguntas.")
    print("Aviso: Protótipo informativo que não representa canal oficial do governo.")
    print(f"Modelo de resposta ativo: {nome_modelo}")
    print("=" * 68)

def selecionar_modelo_prompt(modelo_atual):
    chaves = list(MODELOS_PROMPT.keys())
    print("\n--- Escolha o Modelo de Prompt / Instrução ---")
    for indice, chave in enumerate(chaves, start=1):
        info = MODELOS_PROMPT[chave]
        marcador = " (ATIVO)" if chave == modelo_atual else ""
        print(f"{indice}. {info['nome']}{marcador}")
        print(f"   Papel: {info['papel']}")

    escolha = input("Digite o número do modelo (ou 0 para manter o atual): ").strip()
    if escolha == "0" or not escolha:
        print(f"Mantendo o modelo atual: {MODELOS_PROMPT[modelo_atual]['nome']}")
        aguardar_enter_menu()
        return modelo_atual

    if escolha.isascii() and escolha.isdigit() and 1 <= int(escolha) <= len(chaves):
        novo_modelo = chaves[int(escolha) - 1]
        print(f"Modelo alterado para: {MODELOS_PROMPT[novo_modelo]['nome']}")
        aguardar_enter_menu()
        return novo_modelo

    print("Opção inválida. Mantendo o modelo anterior.")
    aguardar_enter_menu()
    return modelo_atual

def navegar_por_temas(base, modelo_atual):
    """Navegação guiada entre os 3 temas e seus assuntos relacionados."""
    opcoes_temas = listar_temas(base)
    while True:
        print("\n--- Navegação por Temas ---")
        for numero, tema in enumerate(opcoes_temas, start=1):
            print(f"{numero}. {tema}")
        print("0. Voltar ao menu principal")

        escolha = input("Escolha o número do tema: ").strip()
        if escolha == "0":
            main()
            return

        if not escolha.isascii() or not escolha.isdigit() or not 1 <= int(escolha) <= len(opcoes_temas):
            print("Opção inválida. Digite apenas o número correspondente ao tema.")
            continue

        tema_selecionado = opcoes_temas[int(escolha) - 1]
        registros_tema = buscar_por_tema(base, tema_selecionado)

        print(f"\nOrientações disponíveis em '{tema_selecionado}' ({len(registros_tema)} registros):")
        for reg in registros_tema:
            print(f"  [ID {reg['id']}] {reg['pergunta']}")

        sub_escolha = input(
            "\nDigite o ID para ler a orientação completa (ou Enter para ver os temas relacionados): "
        ).strip()
        if sub_escolha:
            resultado_id = consultar_por_id_assistente(base, sub_escolha, modelo=modelo_atual)
            print(f"\n{resultado_id['resposta_formatada']}")

        relacionados = temas_relacionados(base, tema_selecionado)
        if relacionados:
            print(f"\nA partir de '{tema_selecionado}', você pode continuar explorando:")
            for rel in relacionados:
                print(f"  -> {rel['tema']}: {rel['motivo']}")
            # Atualiza as opções para priorizar os temas conectados no grafo
            opcoes_temas = [r["tema"] for r in relacionados]
        else:
            opcoes_temas = listar_temas(base)

def realizar_pergunta_livre(base, modelo_atual):
    print("\n--- Consulta por Pergunta Livre ---")
    print("Exemplos: 'Como consultar o CPF?', 'Preciso de ajuda com CadÚnico', 'Direitos PCD'")
    pergunta = input("Digite sua dúvida (ou 0 para voltar): ")
    if pergunta.strip() == "0":
        main()
        return

    resultado = responder_consulta(base, pergunta, modelo=modelo_atual)
    print(f"\n{resultado['resposta_formatada']}")

    # Se houve ambiguidade (múltiplos registros), permite abrir um ID específico na hora
    if resultado["status"] == "ambiguo":
        escolha_id = input(
            "\nDeseja abrir algum dos IDs listados acima? Digite o ID (ou Enter para voltar): "
        ).strip()
        if escolha_id:
            detalhe = consultar_por_id_assistente(base, escolha_id, modelo=modelo_atual)
            print(f"\n{detalhe['resposta_formatada']}")
        else:
            main()

    aguardar_enter_menu()

def main():
    try:
        base = carregar_base()
    except ValueError as erro:
        print(f"Erro crítico ao iniciar o Citizen Assist AI: {erro}")
        return

    modelo_atual = "didatico"

    while True:
        exibir_cabecalho(modelo_atual)
        print("\nMENU PRINCIPAL:")
        print("1. Fazer uma pergunta ao assistente")
        print("2. Navegar por temas e assuntos relacionados")
        print("3. Consultar orientação diretamente pelo ID")
        print("4. Trocar modelo de prompt/resposta (Objetivo vs. Didático)")
        print("0. Encerrar atendimento")

        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Atendimento encerrado. Lembre-se de sempre conferir os canais oficiais.")
            return
        elif opcao == "1":
            realizar_pergunta_livre(base, modelo_atual)
        elif opcao == "2":
            navegar_por_temas(base, modelo_atual)
        elif opcao == "3":
            identificador = input("Informe o número do ID (1 a 15) ou 0 para voltar: ").strip()
            if identificador != "0":
                resultado = consultar_por_id_assistente(base, identificador, modelo=modelo_atual)
                print(f"\n{resultado['resposta_formatada']}")
                aguardar_enter_menu()
            main()
        elif opcao == "4":
            modelo_atual = selecionar_modelo_prompt(modelo_atual)
        else:
            print("Opção inválida. Escolha 0, 1, 2, 3 ou 4.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nConsulta encerrada.")
