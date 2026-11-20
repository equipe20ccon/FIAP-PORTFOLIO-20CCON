## Plano de Testes, Indicadores e Avaliação (Parte 4)

A avaliação do **Citizen Assist AI** foi estruturada para validar a precisão da recuperação de informações, o comportamento diante de variações de escrita, o tratamento de entradas fora do escopo ou ambíguas, o tempo médio de consulta e a facilidade de uso da interface em terminal (`python src/sistema.py`).

Os testes automatizados foram implementados em `tests/avaliacao_parte4.py`, executando **15 casos de teste** distintos sobre a base estruturada (`temas.json`).

### 1. Matriz de Casos de Teste e Resultados

| Caso | Categoria | Método | Entrada Testada | Resposta Esperada | Resposta Obtida | Classificação | Tempo (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | Direta | Palavra-chave | `"Como consultar o CPF?"` | ID 1 | ID 1 | Acerto | 0,2686 |
| 02 | Direta | Palavra-chave | `"Como emitir a CIN?"` | ID 2 | ID 2 | Acerto | 0,1808 |
| 03 | Direta | Palavra-chave | `"Como se cadastrar no CadÚnico?"` | ID 6 | ID 6 | Acerto | 0,1752 |
| 04 | Direta | Palavra-chave | `"Como solicitar o seguro-desemprego?"` | ID 15 | ID 15 | Acerto | 0,1714 |
| 05 | Direta | ID | `"9"` | ID 9 | ID 9 | Acerto | 0,0423 |
| 06 | Direta | Tema | `"Documentação"` | 5 registros | 5 registros | Acerto | 0,0673 |
| 07 | Variação de escrita | Palavra-chave | `"SITUAÇÃO CADASTRAL CPF"` | ID 1 | IDs [1, 5] (1º: ID 1) | Acerto | 0,1733 |
| 08 | Variação de escrita | Palavra-chave | `"titulo de eleitor regularizacao"` | ID 4 | ID 4 | Acerto | 0,1719 |
| 09 | Variação de escrita | Palavra-chave | `"credencial de estacionamento para pessoa idosa"` | ID 10 | ID 10 | Acerto | 0,1720 |
| 10 | Fora do assunto | Palavra-chave | `"Como preparar uma receita de bolo de chocolate?"` | Vazio (sem resposta) | Vazio | Acerto | 0,1739 |
| 11 | Fora do assunto | Palavra-chave | `"Qual a previsão do tempo para amanhã?"` | Vazio (sem resposta) | Vazio | Acerto | 0,1694 |
| 12 | Limite (Entrada vazia) | Palavra-chave | `"   "` | Vazio (aviso de entrada) | Vazio | Acerto | 0,0018 |
| 13 | Limite (Consulta vaga) | Palavra-chave | `"como posso consultar"` | Vazio (apenas stopwords) | Vazio | Acerto | 0,0033 |
| 14 | Limite (Ambígua) | Palavra-chave | `"denúncia"` | IDs [11, 12, 13] | IDs [11, 12, 13] | Acerto | 0,1790 |
| 15 | Limite (Sem base) | Palavra-chave | `"Como tirar passaporte de emergência na Polícia Federal?"` | Vazio (sem resposta) | Vazio | Acerto | 0,1745 |

### 2. Indicadores de Desempenho Calculados

* **Total de consultas testadas:** 15 casos (abrangendo dúvidas diretas, variações de escrita, consultas fora do assunto e cenários de limite).
* **Taxa de acerto:** **100,0%** (15/15 casos avaliados com o comportamento esperado registrados em `tests/resultados_parte4.csv`).
* **Tempo médio de consulta:** **0,1440 ms** (medido com `time.perf_counter()` em execução local sobre a base carregada em memória).

### 3. Teste de Usabilidade

Foi realizado um teste prático de usabilidade com **1 usuário externo à equipe de desenvolvimento**, executando a aplicação via terminal (`python src/sistema.py`) a partir de um roteiro de tarefas:

* **Atividades realizadas pelo usuário:**
  1. Busca direta por palavra-chave para consultar orientações sobre a Carteira de Identidade Nacional (CIN — referida pelo usuário como `"SIM"` em seu relato).
  2. Exploração da navegação por temas (`3. Navegar por temas`), acessando a categoria **Serviços Públicos**.
  3. Inserção proposital de uma opção numérica inválida no menu para verificar o tratamento de erro.
* **Resultados e percepções observadas:**
  * O usuário avaliou o sistema como intuitivo, prático e fácil de utilizar.
  * O destaque principal apontado foi a velocidade e simplicidade da busca por palavra-chave (*"só digitou e apareceu já"*), retornando imediatamente a orientação correspondente.
  * Na navegação por temas, explorou com facilidade a seção de **Serviços Públicos**.
  * Ao digitar uma opção inválida no menu, destacou positivamente o fato de o sistema informar o erro e exibir imediatamente as alternativas corretas (`0, 1, 2 ou 3`), evitando travamentos e facilitando a continuidade.

---

## Conclusões, Limitações e Possibilidades de Melhoria

### Conclusões

O protótipo **Citizen Assist AI** atingiu os objetivos propostos para a Global Solution, demonstrando que estruturas de dados nativas do Python (listas, dicionários e conjuntos) combinadas com normalização textual e regras explícitas de filtragem oferecem respostas rápidas (**0,1440 ms** em média), rastreáveis e livres de alucinações para dúvidas cidadãs cotidianas. A separação modular entre base de dados (`JSON`), motor de busca (`src/busca.py`) e interface (`src/sistema.py`) facilitou tanto a manutenção quanto a automação dos testes.

### Limitações Identificadas

1. **Dependência de correspondência exata de termos relevantes:** A função `buscar_por_palavras_chave` exige que todos os termos relevantes de uma palavra-chave composta estejam presentes na consulta (`palavras.issubset(termos)`). Embora isso elimine falsos positivos, pode deixar de retornar resultados caso o usuário digite sinônimos ausentes na base ou cometa erros de digitação (como escrever `"SIM"` em vez de `"CIN"`).
2. **Fluxo restrito na navegação encadeada por temas:** Na função `navegar(base)`, após escolher o primeiro tema, a lista de opções passa a exibir apenas os temas relacionados no grafo (`RELACOES`), exigindo retornar ao menu anterior caso o usuário deseje visualizar novamente todos os temas principais.
3. **Escopo da avaliação:** Os tempos medidos refletem apenas operações locais em memória sem latência de rede ou integração com APIs externas, e o teste de usabilidade contou com uma amostra inicial de 1 usuário externo.

### Possibilidades de Melhoria

1. **Busca aproximada (Fuzzy Matching) e tolerância a erros de digitação:** Incorporar comparação por similaridade (como `difflib.get_close_matches` da biblioteca padrão do Python) quando a busca lexical retornar vazia, permitindo sugerir termos próximos ao cidadão em casos de digitação incorreta.
2. **Aprimoramento da navegação no terminal:** Manter uma opção para listar todos os temas dentro do submenu de navegação, além de exibir os temas relacionados como sugestões complementares.
3. **Validação automatizada de fontes oficiais:** Incluir na função `carregar_base()` uma verificação que alerte caso algum registro novo seja cadastrado sem URL de domínio oficial confiável (`.gov.br`, `.jus.br`, `.leg.br`), garantindo a integridade observada na base atual.