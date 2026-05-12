# md2survey - Conversores SurveyMD para DOCX e LSS

A versao atual do app entende SurveyMD (`.md`) como arquivo de entrada. A partir
desse `.md`, o processamento gera os artefatos `.docx` e `.lss`.

O fluxo por planilha (`.xlsx` -> `.md`) esta deprecated. Ele permanece apenas
como apoio legado para migrar conteudo antigo, mas nao deve ser usado como fluxo
principal de autoria ou processamento.

## Uso

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python md2docx.py modelo_teste.md modelo_teste.docx --template-docx exemplo\TSID03-ANEXO_QUESTIONARIO.docx
python md2lss.py modelo_teste.md modelo_teste.lss
```

O `.docx` serve para revisao/impressao. O `.lss` e o artefato correto para
importacao no LimeSurvey.

Voce nao precisa se preocupar com `sid` no uso normal: se ele nao existir no
ambiente de destino, o LimeSurvey pode gerar/atribuir um ID automaticamente na
importacao. Use `sid:` no cabecalho ou `--sid` apenas quando quiser controlar a
base numerica usada no `.lss` gerado.

No cabecalho usado para `.lss`, `admin` deve ser curto: o LimeSurvey limita esse
campo a 50 caracteres. Use `adminemail` para o e-mail do responsavel.

## Variantes por target

Use `target` no cabecalho do `.md` para gerar variantes do mesmo questionario:

```md
---
title: "Questionario"
target: municipal, estadual
---
```

Por padrao, toda questao entra em todos os targets. Para restringir uma questao,
adicione `target` nela:

```md
### q2001 [short]
target: municipal

Pergunta exibida apenas no questionario municipal.
```

Com multiplos targets, os conversores geram saidas com sufixo:

```bash
python md2docx.py questionario.md questionario.docx
# questionario_municipal.docx
# questionario_estadual.docx

python md2lss.py questionario.md questionario.lss
# questionario_municipal.lss
# questionario_estadual.lss
```

No `.lss`, quando houver `--sid` ou `sid:` no cabecalho, o primeiro target usa
esse SID base e os targets seguintes usam SID incremental na ordem do cabecalho.
Se nenhum SID for informado, o conversor usa uma base interna apenas para montar
as referencias do arquivo, e o LimeSurvey pode atribuir o ID final durante a
importacao. Grupos que ficarem sem questoes apos o filtro recebem uma questao
automatica de ciencia. Se uma
questao de um target depender via `visible_if` de uma questao que nao existe
nesse mesmo target, a geracao falha com erro.

## Tipos de questao e escalas

Declare cada questao com `### codigo [tipo]`. Os tipos aceitos pelo `.lss` sao:

- `single`, `list`, `radio`, `lista`: escolha unica. Use `scale` ou `options`.
- `multi`, `multiple`, `checkbox`, `multipla`: multiplos checkboxes. Use `subquestions`.
- `short`, `text`, `texto_curto`: resposta curta em texto.
- `long`, `textarea`, `texto_longo`: resposta longa em texto.
- `upload`, `file`, `arquivo`: envio de arquivo.
- `multi_text`, `multitext`, `varios_textos`: varios campos de texto. Use `subquestions`.
- `array`, `matrix`, `matriz`: matriz/tabela. Use `subquestions` para linhas e `scale` ou `options` para colunas.
- `array_numbers`, `array_number`, `numeric_array`, `array_numeros`, `matriz_numerica`: matriz/tabela de numeros. Use `subquestions` para linhas e `scale` ou `options` para colunas.
- `adoption`, `adocao`: macro de grau de adocao.

Exemplo de escala reutilizavel:

```md
## Escala: sim_nao
type: single
- sim | Sim
- nao | Nao
```

Uso da escala em uma questao:

```md
### q2001 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
scale: sim_nao
```

Tambem e possivel declarar opcoes diretamente na questao:

```md
### q2002 [single]
question: **Qual e a situacao do plano de TI?**
mandatory: true

options:
- vigente | Plano vigente
- vencido | Plano vencido
- inexistente | Nao ha plano
```

Para `multi`, `multi_text` e `array`, use `subquestions`:

```md
### q2003 [multi]
question: **Quais artefatos existem?**
mandatory: true

subquestions:
- plano | Plano de TI
- relatorio | Relatorio de acompanhamento
- ata | Ata de aprovacao
```

No parser do `.lss`, linhas de opcoes e subquestoes podem ser escritas com ou
sem hifen, desde que usem `codigo | texto` ou `codigo: texto`.

Para matriz numerica, use `array_numbers`:

```md
### q2004 [array_numbers]
question: **Informe o quantitativo de profissionais por area e vinculo.**
mandatory: true

subquestions:
- TI | Tecnologia da Informacao
- SI | Seguranca da Informacao

options:
- efetivos | Servidores efetivos
- comissionados | Servidores comissionados
- terceirizados | Terceirizados
```

Por padrao, `array_numbers` gera campos numericos no LimeSurvey com valor minimo
`0`, maximo `1000`, passo livre (`multiflexible_step: -1`) e caixas de entrada
visiveis (`input_boxes: 1`). Esses atributos podem ser sobrescritos na questao,
se necessario.

## Atributos de questao

Os atributos gerais aceitos nas questoes sao:

- `question` ou `title`: texto/enunciado da questao.
- `mandatory`: `true`, `false`, `sim`, `nao`, `1`, `0` etc.
- `scale`: codigo de uma escala criada com `## Escala:`.
- `help`: texto de ajuda da questao.
- `subgroup`: titulo visual interno antes da questao.
- `visible_if` ou `relevance`: condicao de exibicao.
- `other`: habilita opcao "Outro" quando aplicavel.
- `target`: restringe a questao a uma ou mais variantes do cabecalho.
- `explain`: texto explicativo exibido junto da questao.
- `repeat_group_description`: cria no `.lss` um grupo proprio para a questao,
  repetindo titulo e descricao do grupo original.
- `hide_tip`: controla a dica padrao do LimeSurvey em questoes de multiplas respostas.
- `min_answers` e `max_answers`: limites para questoes de multiplas respostas.
- `allowed_filetypes`, `min_files`, `max_files`: atributos de questoes `upload`.

### `explain`

Use `explain` para adicionar um texto explicativo logo abaixo do enunciado da
questao. O texto aparece no `.docx` de revisao e tambem e incorporado ao texto
da pergunta no `.lss`.

```md
### q2001 [single]
question: **A organizacao possui processo formal de planejamento de TI?**
mandatory: true
scale: sim_nao
explain: Considere processos documentados, aprovados e usados de forma recorrente.
```

### `repeat_group_description`

Use `repeat_group_description: true` quando uma questao deve ser exportada no
`.lss` em um grupo proprio, repetindo o mesmo titulo e a mesma descricao do
grupo original. Isso e util quando o texto do grupo apresenta um contexto que
deve aparecer imediatamente antes daquela questao. As questoes seguintes sem
`repeat_group_description` permanecem nesse mesmo grupo repetido, ate que outra
questao com `repeat_group_description: true` inicie um novo grupo ou ate o
proximo `## Grupo:`.

```md
## Grupo: g2000 | Gestao de Tecnologia da Informacao
> Este grupo apresenta o contexto de gestao de TI que deve orientar as respostas.

### q2111 [adoption]
repeat_group_description: true
question: **A organizacao executa processo de planejamento de TI.**
mandatory: true

### q2112 [adoption]
repeat_group_description: true
question: **A organizacao possui plano de TI vigente.**
mandatory: true
```

No `.lss`, o exemplo acima gera dois grupos, cada um com a mesma descricao de
`g2000` e com uma questao logica. Se uma pergunta comum vier apos uma questao
com `repeat_group_description: true` e nao declarar o atributo, ela sera mantida
no mesmo grupo repetido. Em questoes `[adoption]`, a macro inteira fica no mesmo
grupo repetido: pergunta principal, nao aplicabilidade, justificativas,
detalhamento e evidencia.

Os codigos dos grupos repetidos sao ajustados automaticamente para evitar
duplicidade. Por exemplo, `g2000` com `q2111` pode gerar um grupo interno como
`g2000_q2111`.

### Grupos vazios no `.lss`

Um grupo sem questoes nao e descartado no `.lss`. O conversor cria
automaticamente uma questao obrigatoria de ciencia, permitindo usar o grupo como
pagina de contexto:

```md
## Grupo: g2000 | Gestao de Tecnologia da Informacao
> Texto introdutorio que apresenta o contexto das paginas seguintes.
```

Questao criada automaticamente no `.lss`:

```md
### qg2000_ciencia [multi]
question: Para prosseguir, confirme que tomou ciencia do contexto apresentado nesta secao.
mandatory: true

subquestions:
- ciente | Estou ciente do contexto apresentado.
```

### `upload`

Use `upload` para solicitar anexos no LimeSurvey. Os atributos principais sao:
`allowed_filetypes`, `min_files` e `max_files`.

```md
### q2004evi [upload]
question: **Anexe evidencia documental do plano de TI.**
mandatory: true
visible_if: q2001 == sim
allowed_filetypes: pdf, doc, docx, zip
min_files: 1
max_files: 3
```

No `.docx`, questoes de evidencia documental sao apresentadas como orientacao de
revisao; o envio real do arquivo acontece no LimeSurvey importado a partir do
`.lss`.

### Atributos especificos de `[adoption]`

O macro `[adoption]` aceita, alem dos atributos gerais:

- `adoption_scale`: escala da pergunta principal. Padrao: `adocao`.
- `nsa_scale`: escala da justificativa de nao aplicabilidade. Padrao: `nao_aplicabilidade`.
- `nsa`: habilita/desabilita a pergunta de nao aplicabilidade.
- `nsa_text`, `lei_text`, `est_text`, `raz_text`: textos das perguntas auxiliares.
- `lei`, `est`, `raz`: habilitam/desabilitam auxiliares de lei, estudo e razoes.
- `detail`: habilita/desabilita o detalhamento.
- `detail_text`: texto da pergunta de detalhamento.
- `detail_mandatory`: torna o detalhamento obrigatorio.
- `detail_min_answers`, `detail_max_answers`: limites do detalhamento.
- `detail_hide_tip`: controla a dica padrao do LimeSurvey no detalhamento.
- `nsa_suffix`, `lei_suffix`, `est_suffix`, `raz_suffix`, `detail_suffix`: sufixos dos codigos gerados.
- `evidence_text`: cria pergunta `upload` obrigatoria para envio de evidencia documental.
- `evidence_if`: condicao de exibicao da pergunta automatica de evidencia documental.

Campos legados `evidence`, `evidence_type`, `evidence_mandatory`,
`evidence_allowed_filetypes`, `evidence_min_files`, `evidence_max_files` e
`evidence_suffix` sao reconhecidos para diagnostico, mas nao devem ser usados em
novos questionarios. Prefira `evidence_text` ou uma questao `[upload]`
declarada explicitamente.

## Macro adoption

Use `[adoption]` para gerar a pergunta principal de grau de adocao, as
justificativas de nao aplicabilidade e, quando informado, o checklist de
detalhamento.

Quando `evidence_text` e informado em uma questao `[adoption]`, o conversor
cria automaticamente uma pergunta `upload` obrigatoria, exibida quando a resposta
indicar adocao parcial ou maior.

Nas demais questoes, `evidence_text` tambem cria uma pergunta `upload`
obrigatoria com os mesmos defaults (`pdf, docx, zip`, minimo 1 arquivo e maximo
1 arquivo). Use `evidence_if` quando precisar informar explicitamente a condicao
de exibicao da evidencia:

```md
### q2001 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
evidence_text: Caso tenha respondido que possui plano vigente, anexe evidencia documental.
evidence_if: q2001 == sim

options:
- sim | Sim
- nao | Nao
```

Quando `evidence_if` nao for informado, o conversor usa uma condicao padrao:
qualquer alternativa marcada/respondida para questoes com alternativas, ou
evidencia sempre visivel para questoes textuais ou sem alternativas discretas.
Se precisar de outro comportamento, declare uma pergunta `upload` normal no
`.md`, com o tipo e a condicao desejados:

```md
### q1022extDevi [upload]
mandatory: false
visible_if: q1022ext.D == Y
allowed_filetypes: doc, pdf, docx, zip
min_files: 1
max_files: 3

Anexe evidência documental que comprove a aprovação formal do PEDTIC.
```

## Opcoes principais

- `--template-docx`: DOCX de referencia usado como base de estilos, margens, cabecalho e rodape.
- `--sid`, `--first-gid`, `--first-qid`: parametros do arquivo LimeSurvey `.lss`.

## Planilha deprecated

A conversao de SurveyXLSX para SurveyMD esta deprecated. Use `.md` como entrada
do app e gere `.docx` e `.lss` diretamente a partir dele.

Se precisar migrar conteudo antigo de SurveyXLSX, ainda e possivel gerar um
`.md` inicial:

```bash
python xlsx2md.py modelo_teste.xlsx modelo_teste.md
```

Tambem existe um comando legado que gera `.md`, `.docx` e `.lss` a partir da
planilha. Evite esse fluxo para novos questionarios:

```bash
python survey_from_xlsx.py modelo_teste.xlsx --template-docx exemplo\TSID03-ANEXO_QUESTIONARIO.docx --force
```

Por padrao, as saidas ficam no mesmo diretorio da planilha:
`modelo_teste.md`, `modelo_teste.docx` e `modelo_teste.lss`.

## Variantes por organizacao

Use a coluna opcional `orgs` nas abas `questions`, `subquestions` e `options`
para restringir uma linha a uma ou mais organizacoes. Separe multiplos codigos
por virgula, ponto e virgula ou barra vertical, por exemplo `A,B`, `A; B` ou
`A|B`. Quando `orgs` fica vazio, a linha vale para todas as organizacoes.

As organizacoes sao descobertas automaticamente pelos valores preenchidos em
`orgs`. Quando houver mais de uma variante, a aba `survey` deve informar um SID
por organizacao com chaves como `sid_A` e `sid_B`.

Para depurar uma unica variante em Markdown:

```bash
python xlsx2md.py modelo_teste.xlsx modelo_teste_A.md --org A
```

## Scripts individuais

Os conversores separados continuam disponiveis para depuracao ou uso parcial:

- `xlsx2md.py`: converte `.xlsx` para SurveyMD.
- `md2docx.py`: converte SurveyMD para DOCX.
- `md2lss.py`: converte SurveyMD para LimeSurvey `.lss`.

## Subgrupos visuais

Use a aba opcional `subgroups` para criar titulos internos que aparecem no DOCX
sem criar grupos formais no LimeSurvey. A aba deve conter `group_code`,
`subgroup_code`, `subgroup_title` e `order`. Na aba `questions`, preencha a
coluna `subgroup_code` nas questoes pertencentes ao bloco. O titulo e emitido
uma vez, na primeira questao do subgrupo.

## Formato gerado

- Paragrafos no estilo do documento de referencia.
- Cabecalho, rodape, margens e estilos preservados quando `--template-docx` e usado.
- Texto da questao em negrito.
- Ajuda em vermelho com prefixo `?`.
- Cada grupo e cada questao comecam em nova pagina no DOCX.
- Checkboxes e radios renderizados para revisao humana.
- Blocos de evidencia documental usam icone de documento e chamada visual propria.
- Tabelas de questoes `array` usam Calibri, cabecalho em negrito tamanho 10,
  corpo tamanho 9 e primeira coluna justificada.
- Questoes com `visible_if` simples aparecem aninhadas no DOCX de revisao.
- O `.lss` continua sendo o artefato correto para importacao no LimeSurvey.
