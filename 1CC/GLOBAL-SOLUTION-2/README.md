# Citizen Assist AI (Global Solution 2026.2)

Assistente de linha de comando em Python desenvolvido para consulta de informações sobre documentos, serviços públicos e direitos básicos a partir de uma base local verificada.

---

## 1. Integrantes da Equipe

| Integrante | RM |
|---|---|
| Pedro Matteo Benta dos Santos Simplicio | RM573133 |
| Christian Theodor Heisterkamp | RM571998 |
| Samuel Gissi Nogueira Gonçalves | RM568867 |
| Matheus Freitas da Silva Santos | RM574003 |

---

## 2. Problema, Público Beneficiado e Temas Abordados

Informações sobre serviços públicos e documentos costumam estar espalhadas em diferentes portais ou escritas com termos técnicos difíceis de entender. O Citizen Assist AI reúne orientações resumidas em um único ponto de consulta no terminal, indica o link oficial de cada serviço e informa quando não possui dados suficientes para responder.

- **Público beneficiado:** Cidadãos que precisam de orientação rápida sobre procedimentos e direitos básicos do cotidiano.
- **Temas abordados (15 registros divididos em 3 categorias):**
  1. **Documentação (5 registros):** Consulta de CPF, emissão da Carteira de Identidade Nacional (CIN), Carteira de Trabalho Digital, regularização do Título de Eleitor e consulta da CNH.
  2. **Serviços Públicos (5 registros):** Cadastro no CadÚnico, consulta ao Bolsa Família, benefícios do INSS, criação e acesso à conta Gov.br e Cartão de Estacionamento para Idoso.
  3. **Direitos e Orientações (5 registros):** Reclamação no Procon, denúncia de violência contra a mulher (Ligue 180), denúncia de maus-tratos contra animais, direitos da Pessoa com Deficiência (PCD) e solicitação do Seguro-Desemprego.

---

## 3. Organização da Base de Conhecimento, Estruturas e Busca

### Base de Conhecimento (`temas.json`)

Os dados ficam armazenados em um arquivo JSON externo ao código, estruturado como uma lista de dicionários. Isso permite editar ou adicionar registros sem alterar as regras do programa. Ao iniciar, a função `carregar_base()` valida a existência do arquivo e exige 7 campos em cada registro:

- `id`: número inteiro único;
- `tema`: categoria principal do registro;
- `pergunta`: dúvida de referência;
- `palavras_chave`: lista de termos usados na busca;
- `orientacao`: texto resumido com o procedimento;
- `fonte`: endereço do portal oficial consultado;
- `data_verificacao`: data em que a informação foi conferida pela equipe.

### Estruturas de Dados e Estratégia de Busca (`src/busca.py`)

- **Listas, dicionários e conjuntos (`set`):** Usados para armazenar os registros, indexar buscas por ID, filtrar temas e calcular interseções de palavras.
- **Normalização e busca léxica:** A função `normalizar()` converte o texto para minúsculas, remove acentos (via decomposição Unicode `NFKD`) e descarta pontuações. Na função `buscar_por_palavras_chave()`, palavras comuns sem valor de busca (definidas no conjunto `IGNORADAS`) são retiradas. Para evitar falsos positivos, o algoritmo exige que todos os termos relevantes de uma expressão-chave estejam presentes na pergunta (`issubset`). Por exemplo, "receita de bolo" não retorna o registro da "receita federal".
- **Critério de desempate:** Quando mais de um registro corresponde à consulta, os resultados são ordenados pela maior quantidade de termos coincidentes e, em caso de empate, pelo menor `id`.
- **Grafo de navegação entre temas:** O dicionário `RELACOES` representa um grafo não direcionado que conecta os três temas da base. Cada ligação guarda uma justificativa textual usada para sugerir o próximo tema ao usuário.

---

## 4. Regras de Resposta, Modelos de Prompt e Limitações

O assistente consulta exclusivamente os registros carregados de `temas.json` e monta as respostas por meio de regras determinísticas e modelos de instrução documentados em `src/assistente.py`. O sistema não cria orientações fora da base.

### Modelos de Prompt Documentados

| Critério | Modelo 1: Assistente Objetivo (`objetivo`) | Modelo 2: Assistente Didático (`didatico`) |
| :--- | :--- | :--- |
| **Papel** | Assistente informativo voltado a respostas curtas e diretas. | Orientador cidadão que apresenta o conteúdo de forma estruturada e detalhada. |
| **Regras** | 1. Usar apenas dados do registro encontrado.<br>2. Exibir a orientação em texto curto.<br>3. Citar fonte oficial e data de verificação.<br>4. Exibir aviso de que não é canal oficial.<br>5. Não inventar resposta quando não houver correspondência. | 1. Identificar o tema e repetir a dúvida atendida.<br>2. Separar orientação, fonte e sugestões em blocos.<br>3. Destacar link oficial e data de verificação.<br>4. Sugerir até dois temas relacionados do grafo.<br>5. Reforçar limites do sistema e privacidade. |

- **Comparação entre os modelos:** O Modelo 1 (`objetivo`) funciona bem para consultas rápidas quando o usuário quer apenas o link e o resumo em poucas linhas, mas não orienta os próximos passos. O Modelo 2 (`didatico`) mostrou-se mais claro e consistente para o público do projeto, pois separa o procedimento, a fonte oficial, o aviso de não oficialidade e as sugestões de temas relacionados em blocos distintos, facilitando a leitura no terminal.

### Tratamento de Entradas Inválidas e Limitações

- **Entrada vazia ou com símbolos:** Identificada antes da busca, exibindo aviso e a lista de temas disponíveis.
- **Consulta vaga:** Perguntas formadas apenas por palavras genéricas (como "como consultar") recebem pedido de reformulação com exemplos de termos específicos.
- **Ambiguidade:** Quando uma consulta retorna mais de um registro (como "denúncia"), o sistema exibe o primeiro resultado por relevância, lista os demais IDs encontrados e permite abrir qualquer um deles.
- **Ausência de resposta:** Perguntas fora dos temas cadastrados recebem aviso informando que não há base verificada para aquele assunto.

---

## 5. Como Executar

O projeto utiliza apenas a biblioteca padrão do Python (versão 3.10 ou superior). Na pasta raiz do repositório, execute:

```bash
python src/sistema.py
```

Para executar os testes unitários da camada de busca e a avaliação da Parte 4:

```bash
python -m unittest
python -m tests.avaliacao_parte4
```

---

## 6. Exemplos de Funcionamento

### Exemplo 1: Consulta válida (Modelo Didático)

Entrada:
```text
Como tirar a nova carteira de identidade CIN?
```

Saída:
```text
====================================================================
TEMA: DOCUMENTAÇÃO  |  REGISTRO #2
Dúvida atendida: Como emitir a CIN?
--------------------------------------------------------------------
COMO PROCEDER:
  A emissão da Carteira de Identidade Nacional (CIN) pode ser realizada com um agendamento prévio no site do Poupatempo, onde o cidadão deve comparecer ao posto de atendimento para concluir o processo.

CONFIABILIDADE E FONTE:
  • Canal oficial: [https://www.poupatempo.sp.gov.br/carta/D97C3844-A2D9-4C9E-B364-CB4FEB26A1FB](https://www.poupatempo.sp.gov.br/carta/D97C3844-A2D9-4C9E-B364-CB4FEB26A1FB)
  • Última verificação da equipe: 2026-11-09
  • Aviso: Este assistente tem caráter exclusivamente informativo e não substitui canais oficiais. Confirme prazos e requisitos atualizados na fonte indicada.

PARA CONTINUAR SUA CONSULTA (TEMAS RELACIONADOS):
  -> Serviços Públicos: Documentos são utilizados para acessar serviços e benefícios.
  -> Direitos e Orientações: Documentos ajudam no exercício de direitos e em solicitações.
====================================================================
```

### Exemplo 2: Consulta fora da base

Entrada:
```text
Qual a receita de bolo de cenoura?
```

Saída:
```text
Não encontrei orientações verificadas para 'Qual a receita de bolo de cenoura' na minha base atual.
Para manter a confiabilidade, não gero respostas sem fonte comprovada.
Sugestão: tente reformular com palavras-chave mais diretas ou explore os temas disponíveis: Documentação, Serviços Públicos, Direitos e Orientações.
```

### Exemplo 3: Proteção de dados pessoais

Entrada:
```text
Consultar meu CPF 123.456.789-00
```

Saída: O sistema exibe um alerta informando que o número de CPF foi removido antes da consulta e retorna a orientação do Registro #1 (Receita Federal).

---

## 7. Plano de Testes, Indicadores e Resultados

### Perguntas Testadas (Mínimo 12 perguntas e 3 cenários de limite)

Os casos abaixo foram executados via `tests/avaliacao_parte4.py` sobre a base estruturada (`temas.json`), gerando os dados consolidados em `tests/resultados_parte4.csv`:

| # | Pergunta / Entrada | Tipo | Esperado | Obtido | Resultado | Tempo (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `"Como consultar o CPF?"` | Direta | ID 1 | ID 1 | Acerto | 0,2686 |
| 2 | `"Como emitir a CIN?"` | Direta | ID 2 | ID 2 | Acerto | 0,1808 |
| 3 | `"Como se cadastrar no CadÚnico?"` | Direta | ID 6 | ID 6 | Acerto | 0,1752 |
| 4 | `"Como solicitar o seguro-desemprego?"` | Direta | ID 15 | ID 15 | Acerto | 0,1714 |
| 5 | `"9"` | Direta (ID) | ID 9 | ID 9 | Acerto | 0,0423 |
| 6 | `"Documentação"` | Direta (Tema) | 5 registros | 5 registros | Acerto | 0,0673 |
| 7 | `"SITUAÇÃO CADASTRAL CPF"` | Variação de escrita | ID 1 | IDs [1, 5] (1º: ID 1) | Acerto | 0,1733 |
| 8 | `"titulo de eleitor regularizacao"` | Variação de escrita | ID 4 | ID 4 | Acerto | 0,1719 |
| 9 | `"credencial de estacionamento para pessoa idosa"` | Variação de escrita | ID 10 | ID 10 | Acerto | 0,1720 |
| 10 | `"Como preparar uma receita de bolo de chocolate?"` | Fora do assunto | Vazio | Vazio | Acerto | 0,1739 |
| 11 | `"Qual a previsão do tempo para amanhã?"` | Fora do assunto | Vazio | Vazio | Acerto | 0,1694 |
| 12 | `"   "` | Limite (Entrada vazia) | Vazio | Vazio | Acerto | 0,0018 |
| 13 | `"como posso consultar"` | Limite (Consulta vaga) | Vazio | Vazio | Acerto | 0,0033 |
| 14 | `"denúncia"` | Limite (Ambígua) | IDs [11, 12, 13] | IDs [11, 12, 13] | Acerto | 0,1790 |
| 15 | `"Como tirar passaporte de emergência na Polícia Federal?"` | Limite (Sem base) | Vazio | Vazio | Acerto | 0,1745 |

### Indicadores

- **Total de perguntas avaliadas:** `15`
- **Taxa de acerto:** `100,0%` (15/15)
- **Tempo médio de consulta:** `0,1440 ms`

### Teste de Facilidade de Uso

- **Roteiro aplicado:** Teste prático realizado remotamente com 1 usuário externo à equipe na interface em terminal (`python src/sistema.py`), incluindo busca por palavra-chave para consultar orientações sobre a Carteira de Identidade Nacional (CIN — referida pelo usuário como `"SIM"` em seu relato), navegação por temas (incluindo *Serviços Públicos*) e inserção de opção inválida no menu.
- **Resultados e dificuldades observadas:** O usuário relatou que o sistema é intuitivo, prático e fácil de utilizar, destacando a rapidez da busca por palavra-chave (*"só digitou e apareceu já"*), a exploração da seção de *Serviços Públicos* e a apresentação automática das alternativas válidas ao digitar uma opção inválida. Como limitação observada no uso, a busca lexical depende dos termos cadastrados e pode não corresponder a entradas fora das palavras-chave ou digitadas de forma imprecisa (como `"SIM"` em vez de `"CIN"`).

### Interpretação dos Resultados

- A taxa de acerto de **100,0%** (15/15) indica que o motor de busca lida adequadamente com variações de caixa e acentos, filtra consultas vazias ou compostas apenas por *stopwords*, retorna múltiplos registros em termos ambíguos como `"denúncia"` e não inventa respostas quando não há correspondência. O tempo médio em escala de décimos de milissegundo (`~0,14–0,16 ms`) reflete execução local em memória sobre a base JSON, sem incluir eventual latência de rede ou serviços externos.

---

## 8. Clareza, Privacidade e Informação Não Oficial

- **Privacidade:** O sistema não solicita nome, CPF, telefone ou qualquer dado pessoal. Caso o usuário digite uma sequência no formato de CPF, uma expressão regular apaga o número antes da busca e exibe um alerta preventivo.
- **Informação não oficial:** O cabeçalho inicial e todas as respostas exibem aviso informando que o sistema é um protótipo informativo e não substitui órgãos públicos.
- **Rastreabilidade:** Toda orientação exibida acompanha o endereço da fonte consultada e a data de verificação.

---

## 9. Vídeo de Apresentação

- **YouTube (Não Listado):** https://youtu.be/xH5yPYH9-yc?is=m9ssLstG22D_0k6

---

## 10. Conclusões, Limitações e Melhorias Futuras

### Conclusões

O protótipo atende ao objetivo de organizar informações verificadas em uma base local e disponibilizá-las por meio de buscas e navegação entre temas relacionados, mantendo controle sobre fontes, privacidade e limites de resposta.

### Limitações

- **Busca restrita a palavras-chave:** Como a correspondência depende dos termos cadastrados em `palavras_chave`, perguntas formuladas com sinônimos muito diferentes podem não retornar resultados.
- **Atualização manual:** Alterações em leis, prazos ou links governamentais exigem revisão manual do arquivo `temas.json`.
- **Escopo da avaliação:** As medições de tempo ocorrem apenas em ambiente local em memória e a avaliação de usabilidade contou com 1 usuário externo remoto.

### Melhorias Futuras

1. **Dicionário de sinônimos ou busca semântica:** Ampliar o reconhecimento de variações de vocabulário sem perder a restrição aos registros verificados.
2. **Registro local de termos sem correspondência:** Salvar apenas as palavras-chave que não retornaram resultados (sem armazenar dados pessoais) para orientar a inclusão de novos registros na base.
3. **Sugestão de termos próximos e listagem completa na navegação:** Oferecer sugestões de termos semelhantes quando a busca não encontrar correspondência e manter a opção de listar todos os temas durante a navegação por temas relacionados.