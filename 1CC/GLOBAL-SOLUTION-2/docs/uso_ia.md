# Uso de Inteligência Artificial

## Ferramenta utilizada

Durante o desenvolvimento do projeto, a equipe utilizou o **ChatGPT** como ferramenta de apoio.

## O protótipo não utiliza modelo de IA externo

O Citizen Assist AI não envia perguntas a modelos de linguagem, APIs ou serviços externos. As respostas exibidas ao usuário são montadas por regras em Python (`src/busca.py` e `src/assistente.py`) exclusivamente a partir dos registros da base `temas.json`. Os dois modelos de prompt documentados no `README.md` (`objetivo` e `didatico`) são modelos de instrução de resposta aplicados pelo próprio código.

## Validação

- Cada registro de `temas.json` possui o campo `fonte`, com o endereço do portal oficial consultado, e o campo `data_verificacao`, com a data em que a informação foi conferida pela equipe.
- O funcionamento foi verificado com os testes unitários (`python -m unittest`) e com a avaliação de 15 casos de teste (`python -m tests.avaliacao_parte4`), cujos resultados estão em `tests/resultados_parte4.csv`.
- O teste de facilidade de uso com um usuário externo à equipe está descrito no `README.md` e em `docs/parte4_testes_avaliacao.md`.
