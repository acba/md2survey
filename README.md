# md2survey - Conversores SurveyMD para DOCX e LSS

Este repositorio contem conversores CLI para transformar questionarios escritos
em SurveyMD (`.md`) nos artefatos usados no fluxo de trabalho:

- `.docx`: documento de revisao e impressao.
- `.lss`: arquivo importavel no LimeSurvey.

O fluxo principal de autoria e processamento deve partir do `.md`. O fluxo por
planilha (`.xlsx` -> `.md`) esta deprecated e permanece apenas como apoio
legado para migrar conteudo antigo.

## Sumario

- [Uso basico](#uso-basico)
- [Estrutura de um SurveyMD](#estrutura-de-um-surveymd)
- [Cabecalho do questionario](#cabecalho-do-questionario)
- [Variantes por target](#variantes-por-target)
- [Grupos](#grupos)
- [Escalas](#escalas)
- [Tipos de questao](#tipos-de-questao)
- [Estruturas auxiliares](#estruturas-auxiliares)
- [Atributos gerais de questao](#atributos-gerais-de-questao)
- [Atributos por tipo de questao](#atributos-por-tipo-de-questao)
- [Condicoes de exibicao](#condicoes-de-exibicao)
- [Macro adoption](#macro-adoption)
- [Recomendacoes de autoria](#recomendacoes-de-autoria)

## Uso basico

Crie e ative um ambiente virtual antes de executar os conversores:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Gere os artefatos a partir do `.md`:

```bash
python md2docx.py modelo_teste.md modelo_teste.docx --template-docx exemplo\TSID03-ANEXO_QUESTIONARIO.docx
python md2lss.py modelo_teste.md modelo_teste.lss
```

Use `python <script>.py --help` para conferir as opcoes atuais de cada CLI.

O `.docx` serve para revisao humana e impressao. O `.lss` e o artefato correto
para importacao no LimeSurvey.

## Estrutura de um SurveyMD

Um arquivo SurveyMD e composto por:

1. Cabecalho opcional em frontmatter YAML simples.
2. Titulo principal opcional.
3. Escalas reutilizaveis opcionais.
4. Grupos.
5. Questoes dentro dos grupos.

Exemplo minimo:

```md
---
title: Questionario de exemplo
language: pt-BR
---

# Questionario de exemplo

## Escala: sim_nao
type: single
- sim | Sim
- nao | Nao

## Grupo: g1 | Planejamento de TI
> Este grupo trata de planejamento, governanca e acompanhamento de TI.

### q1 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
scale: sim_nao
```

Cada questao deve usar o formato:

```md
### codigo_da_questao [tipo]
question: Texto da pergunta
```

No `.lss`, uma questao fora de um grupo gera erro. No `.docx`, o conversor pode
criar um grupo padrao, mas a recomendacao e sempre declarar `## Grupo:`.

## Cabecalho do questionario

O cabecalho fica no inicio do arquivo, entre `---`.

```md
---
title: Questionario de Governanca de TI
target: municipal, estadual
sid: 431594
language: pt-BR
admin: Administracao
adminemail: admin@example.com
template: vanilla
format: G
---
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `title` | Titulo do questionario. | Sim | Sim |
| `target` | Lista de variantes de saida. | Sim | Sim |
| `sid` | ID base do survey no `.lss`. | Nao | Sim |
| `language` / `lang` | Idioma do survey. Padrao: `pt-BR`. | Nao | Sim |
| `admin` | Nome do administrador. No LimeSurvey, mantenha ate 50 caracteres. | Nao | Sim |
| `adminemail` / `admin_email` | E-mail do administrador. | Nao | Sim |
| `template` | Tema/template do LimeSurvey. Padrao: `vanilla`. | Nao | Sim |
| `format` | Formato de navegacao do LimeSurvey. Padrao: `G`. | Nao | Sim |
| `expires` | Data de expiracao do survey. | Nao | Sim |
| `startdate` / `start_date` | Data de inicio do survey. | Nao | Sim |

Voce nao precisa informar `sid` no uso normal. Se o SID nao existir no ambiente
de destino, o LimeSurvey pode gerar ou atribuir um ID automaticamente durante a
importacao. Use `sid:` no cabecalho ou `--sid` apenas quando quiser controlar a
base numerica usada no `.lss` gerado.

## Variantes por target

Use `target` no cabecalho para gerar variantes do mesmo questionario:

```md
---
title: Questionario
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
esse SID base e os targets seguintes usam SIDs incrementais na ordem do
cabecalho. Se uma questao de um target depender via `visible_if` de uma questao
que nao existe nesse mesmo target, a geracao falha com erro.

## Grupos

Declare grupos com:

```md
## Grupo: codigo | Titulo do grupo
> Descricao opcional do grupo.
```

No `.lss`, grupos sem questoes nao sao descartados. O conversor cria
automaticamente uma questao obrigatoria de ciencia, permitindo usar o grupo como
pagina de contexto.

Exemplo de grupo vazio:

```md
## Grupo: g2000 | Gestao de Tecnologia da Informacao
> Texto introdutorio que apresenta o contexto das paginas seguintes.
```

Questao criada automaticamente no `.lss`:

```md
### qg2000_ciencia [multi]
question: Confirme para prosseguir para a proxima secao.
mandatory: true

subquestions:
- ciente | Estou ciente das informacoes apresentadas.
```

### Repeticao da descricao do grupo

Use `repeat_group_description: true` quando uma questao deve ser exportada no
`.lss` em um grupo proprio, repetindo o titulo e a descricao do grupo original.
Isso e util quando o texto do grupo apresenta um contexto que deve aparecer
imediatamente antes daquela questao.

```md
## Grupo: g2000 | Gestao de Tecnologia da Informacao
> Este grupo apresenta o contexto de gestao de TI que deve orientar as respostas.

### q2111 [adoption]
repeat_group_description: true
question: **A organizacao executa processo de planejamento de TI.**
mandatory: true
```

As questoes seguintes sem `repeat_group_description` permanecem no mesmo grupo
repetido ate outra questao iniciar novo grupo repetido ou ate o proximo
`## Grupo:`.

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `repeat_group_description` | Cria/reusa grupo proprio repetindo a descricao do grupo original. | Ignorado | Sim |

## Escalas

Escalas permitem reutilizar conjuntos de alternativas:

```md
## Escala: sim_nao
type: single
- sim | Sim
- nao | Nao
```

Uso em uma questao:

```md
### q2001 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
scale: sim_nao
```

O parser aceita itens no formato `codigo | texto` ou `codigo: texto`. No
`.lss`, itens de opcoes e subquestoes podem ser escritos com ou sem hifen,
desde que mantenham um desses separadores.

## Tipos de questao

Declare cada questao com:

```md
### codigo [tipo]
```

| Tipo canonico | Aliases aceitos | Descricao | DOCX | LSS |
|---|---|---|---:|---:|
| `single` | `list`, `radio`, `lista` | Escolha unica. Use `scale` ou `options`. | Parcial | Sim |
| `multi` | `multiple`, `checkbox`, `multipla`, `múltipla` | Multiplos checkboxes. Use `subquestions`. | Parcial | Sim |
| `short` | `text`, `texto_curto` | Resposta curta em texto. | Parcial | Sim |
| `long` | `textarea`, `texto_longo` | Resposta longa em texto. | Parcial | Sim |
| `upload` | `file`, `arquivo` | Envio de arquivo no LimeSurvey. | Parcial | Sim |
| `multi_text` | `multitext`, `varios_textos` | Varios campos de texto. Use `subquestions`. | Parcial | Sim |
| `array` | `matrix`, `matriz` | Matriz/tabela. Use linhas em `subquestions` e colunas em `scale` ou `options`. | Parcial | Sim |
| `array_numbers` | `array_number`, `numeric_array`, `array_numeros`, `matriz_numerica` | Matriz numerica. Use linhas em `subquestions` e colunas em `scale` ou `options`. | Sim | Sim |
| `adoption` | `adocao`, `adoção` | Macro de grau de adocao. | Parcial | Sim |

`Parcial` significa que o `.docx` renderiza a questao para revisao/impressao,
mas nao representa toda a logica ou todos os aliases aceitos pelo `.lss`.

## Estruturas auxiliares

### `options`

Define alternativas ou colunas de resposta.

```md
options:
- sim | Sim
- nao | Nao
```

No `.lss`, tambem sao aceitos: `alternatives`, `alternativas`, `opcoes`,
`opções`, `columns`, `colunas`.

| Uso | DOCX | LSS |
|---|---:|---:|
| Alternativas de `single` | Sim | Sim |
| Colunas de `array` e `array_numbers` | Sim | Sim |
| Alternativas diretas de `multi` | Parcial | Sim |

### `subquestions`

Define subquestoes, linhas ou itens de checkbox.

```md
subquestions:
- plano | Plano de TI
- relatorio | Relatorio de acompanhamento
- ata | Ata de aprovacao
```

No `.lss`, tambem sao aceitos: `subquestoes`, `subquestões`,
`rows`, `linhas`, `detail_options`, `detalhamento`.

| Uso | DOCX | LSS |
|---|---:|---:|
| Itens de `multi` | Sim | Sim |
| Campos de `multi_text` | Sim | Sim |
| Linhas de `array` e `array_numbers` | Sim | Sim |
| Detalhamento de `adoption` | Sim | Sim |

## Atributos gerais de questao

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `question` | Texto/enunciado da pergunta. | Sim | Sim |
| `title` | Alias de `question` no `.lss`; no `.docx`, prefira `question`. | Parcial | Sim |
| Texto livre abaixo do cabecalho | Tambem vira enunciado da pergunta. | Sim | Sim |
| `mandatory` | Torna a resposta obrigatoria. Aceita `true`, `false`, `sim`, `nao`, `1`, `0`, etc. | Parcial | Sim |
| `scale` | Referencia uma escala criada com `## Escala:`. | Sim | Sim |
| `help` | Texto de ajuda da questao. | Sim | Sim |
| `subgroup` | Titulo visual interno antes da questao. | Sim | Sim |
| `visible_if` | Condicao de exibicao. | Parcial | Sim |
| `relevance` | Alias de `visible_if` no `.lss`. | Nao | Sim |
| `other` | Habilita opcao "Outro" quando aplicavel no LimeSurvey. | Nao | Sim |
| `target` | Restringe a questao a uma ou mais variantes do cabecalho. | Sim | Sim |
| `explain` | Texto explicativo junto da pergunta. | Sim | Sim |
| `evidence_text` | Texto de evidencia documental. No `.lss`, gera pergunta `upload` automatica; no `.docx`, aparece como chamada visual. | Sim | Sim |
| `evidence_if` | Condicao explicita para exibir upload automatico criado por `evidence_text`. | Nao | Sim |

### Exemplo de `explain`

```md
### q2001 [single]
question: **A organizacao possui processo formal de planejamento de TI?**
mandatory: true
scale: sim_nao
explain: Considere processos documentados, aprovados e usados de forma recorrente.
```

### Exemplo de `evidence_text`

```md
### q2002 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
scale: sim_nao
evidence_text: Anexe evidencia documental do plano de TI.
```

No `.docx`, o texto aparece como chamada de evidencia. No `.lss`, o conversor
cria uma questao de upload automatica com sufixo `evi`, usando regras padrao de
arquivo.

## Atributos por tipo de questao

### `single`

Tipos: `single`, `list`, `radio`, `lista`.

```md
### q1 [single]
question: A organizacao possui plano?
mandatory: true
scale: sim_nao
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `scale` | Usa alternativas de uma escala. | Sim | Sim |
| `options` | Define alternativas diretamente. | Sim | Sim |
| `other` | Habilita "Outro". | Nao | Sim |
| `evidence_text` | Solicita evidencia vinculada a resposta. | Sim | Sim |

### `multi`

Tipos: `multi`, `multiple`, `checkbox`, `multipla`, `múltipla`.

```md
### q2 [multi]
question: Quais documentos existem?
mandatory: true
min_answers: 1
max_answers: 3
hide_tip: 1

subquestions:
- plano | Plano de TI
- ata | Ata de aprovacao
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `subquestions` | Itens marcaveis. | Sim | Sim |
| `min_answers` | Numero minimo de respostas. | Nao | Sim |
| `max_answers` | Numero maximo de respostas. | Nao | Sim |
| `hide_tip` | Oculta dica padrao do LimeSurvey. Padrao pratico: `1`. | Nao | Sim |
| `evidence_text` | Solicita evidencia quando algum item for marcado, salvo `evidence_if`. | Sim | Sim |

### `short` e `long`

Tipos curtos: `short`, `text`, `texto_curto`.

Tipos longos: `long`, `textarea`, `texto_longo`.

```md
### q3 [short]
question: Informe o numero do processo.
mandatory: true
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `mandatory` | Campo obrigatorio. | Parcial | Sim |
| `help` | Texto de ajuda. | Sim | Sim |
| `visible_if` | Condicao de exibicao. | Parcial | Sim |
| `evidence_text` | Gera ou mostra solicitacao de evidencia. | Sim | Sim |

### `upload`

Tipos: `upload`, `file`, `arquivo`.

```md
### q4evi [upload]
question: Anexe evidencia documental.
mandatory: true
allowed_filetypes: pdf, doc, docx, zip
min_files: 1
max_files: 3
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `allowed_filetypes` | Extensoes permitidas. | Nao | Sim |
| `min_files` | Quantidade minima de arquivos. | Nao | Sim |
| `max_files` | Quantidade maxima de arquivos. | Nao | Sim |
| `mandatory` | Upload obrigatorio. | Parcial | Sim |
| `visible_if` | Condicao para exibir upload. | Parcial | Sim |

### `multi_text`

Tipos: `multi_text`, `multitext`, `varios_textos`.

```md
### q5 [multi_text]
question: Informe os responsaveis por area.

subquestions:
- ti | TI
- contratos | Contratos
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `subquestions` | Cada item vira um campo de texto. | Sim | Sim |
| `mandatory` | Obrigatoriedade da questao. | Parcial | Sim |
| `help` | Ajuda da questao. | Sim | Sim |

### `array`

Tipos: `array`, `matrix`, `matriz`.

```md
### q6 [array]
question: Avalie cada pratica.
scale: sim_nao

subquestions:
- p1 | Pratica 1
- p2 | Pratica 2
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `subquestions` / `rows` | Linhas da matriz. | Sim | Sim |
| `scale` | Colunas da matriz. | Sim | Sim |
| `options` / `columns` | Colunas declaradas diretamente. | Sim | Sim |
| `visible_if` | Condicao de exibicao. | Parcial | Sim |

### `array_numbers`

Tipos: `array_numbers`, `array_number`, `numeric_array`, `array_numeros`,
`matriz_numerica`.

```md
### q7 [array_numbers]
question: Informe quantitativos por area e vinculo.
mandatory: true
input_boxes: 1
multiflexible_min: 0
multiflexible_max: 1000
multiflexible_step: -1

subquestions:
- TI | Tecnologia da Informacao
- SI | Seguranca da Informacao

options:
- efetivos | Efetivos
- terceirizados | Terceirizados
```

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `subquestions` | Linhas da matriz. | Sim | Sim |
| `scale` ou `options` | Colunas da matriz. | Sim | Sim |
| `input_boxes` | Controla caixas de entrada visiveis no LimeSurvey. Padrao: `1`. | Nao | Sim |
| `multiflexible_min` | Valor minimo permitido. Padrao: `0`. | Nao | Sim |
| `multiflexible_max` | Valor maximo permitido. Padrao: `1000`. | Nao | Sim |
| `multiflexible_step` | Passo permitido. Padrao: `-1`, livre. | Nao | Sim |

## Condicoes de exibicao

Use `visible_if` para declarar condicoes amigaveis que o conversor transforma em
ExpressionScript do LimeSurvey.

Exemplos aceitos no `.lss`:

```md
visible_if: q1011 == sim
visible_if: q1022 != naoap
visible_if: q1022 in [adpar, admai]
visible_if: q1022 not in [naoad, adfor]
visible_if: q2112ext.B == Y
visible_if: q2112ext[B] == Y
visible_if: (q1 == sim and q2 in [A, B]) or q3.C == Y
visible_if: raw: ((431594X1000X10000.NAOK == "sim"))
```

| Recurso | DOCX | LSS |
|---|---:|---:|
| Condicao simples `q == valor` | Sim, como dependencia visual | Sim |
| Checkbox `q.item == Y` ou `q[item] == Y` | Parcial | Sim |
| Expressoes compostas com `and` / `or` | Nao como logica visual completa | Sim |
| `raw:` com ExpressionScript manual | Nao | Sim |

## Macro adoption

Tipos: `adoption`, `adocao`, `adoção`.

A macro `adoption` representa grau de adocao. No `.lss`, ela e expandida em um
bloco de questoes comuns: pergunta principal, nao aplicabilidade,
justificativas, detalhamento e upload de evidencia quando configurado.

```md
### q8 [adoption]
question: A organizacao executa processo formal de planejamento de TI.
mandatory: true
explain: Considere processos documentados e recorrentes.
evidence_text: Anexe evidencia documental do processo.

subquestions:
- plano | Existe plano aprovado
- monitoramento | Ha monitoramento periodico
```

### Escalas internas da macro

Se nenhuma escala for informada, a macro usa a escala interna `adocao`:

| Codigo | Texto |
|---|---|
| `naoad` | Nao adota. |
| `adfor` | Ha decisao formal ou plano aprovado para adota-lo. |
| `admen` | Adota em menor parte. |
| `adpar` | Adota parcialmente. |
| `admai` | Adota em maior parte ou totalmente. |
| `naoap` | Nao se aplica. |

Para justificativa de nao aplicabilidade, usa a escala interna
`nao_aplicabilidade`:

| Codigo | Texto |
|---|---|
| `A` | Nao se aplica porque ha lei e/ou norma, externa a organizacao, que impede a implementacao desta pratica. |
| `B` | Nao se aplica porque ha estudos que demonstram que o custo de implementar este controle e maior que o beneficio que seria obtido. |
| `C` | Nao se aplica por outras razoes. |

### Atributos da macro

| Atributo | Descricao | DOCX | LSS |
|---|---|---:|---:|
| `scale` | Escala da pergunta principal. Se omitido, usa `adocao`. | Parcial | Sim |
| `adoption_scale` | Escala da pergunta principal. | Nao | Sim |
| `nsa_scale` | Escala da justificativa de nao aplicabilidade. Padrao: `nao_aplicabilidade`. | Nao | Sim |
| `nsa` | Habilita/desabilita bloco de nao aplicabilidade. Padrao: `true`. | Nao | Sim |
| `nsa_text` | Texto da pergunta de justificativa de nao aplicabilidade. | Nao | Sim |
| `lei` | Habilita pergunta sobre lei/norma impeditiva. Padrao: `true`. | Nao | Sim |
| `lei_text` | Texto da pergunta sobre lei/norma. | Nao | Sim |
| `est` | Habilita pergunta sobre estudos de custo-beneficio. Padrao: `true`. | Nao | Sim |
| `est_text` | Texto da pergunta sobre estudos. | Nao | Sim |
| `raz` | Habilita pergunta de outras razoes. Padrao: `true`. | Nao | Sim |
| `raz_text` | Texto da pergunta de outras razoes. | Nao | Sim |
| `detail` | Habilita detalhamento/checklist. Padrao: `true`. | Sim | Sim |
| `detail_text` | Texto introdutorio do detalhamento. | Nao | Sim |
| `detail_mandatory` | Torna detalhamento obrigatorio. | Nao | Sim |
| `detail_min_answers` | Minimo de itens no detalhamento. | Nao | Sim |
| `detail_max_answers` | Maximo de itens no detalhamento. | Nao | Sim |
| `detail_hide_tip` | Oculta dica do LimeSurvey no detalhamento. Padrao: `1`. | Nao | Sim |
| `subquestions` / `detail_options` | Itens do detalhamento. | Sim | Sim |
| `evidence_text` | Texto da evidencia; no `.lss`, cria upload automatico `qcodeevi`. | Sim | Sim |
| `nsa_suffix` | Sufixo do codigo da questao de nao aplicabilidade. Padrao: `nsa`. | Nao | Sim |
| `lei_suffix` | Sufixo da questao de lei. Padrao: `lei`. | Nao | Sim |
| `est_suffix` | Sufixo da questao de estudos. Padrao: `est`. | Nao | Sim |
| `raz_suffix` | Sufixo da questao de razoes. Padrao: `raz`. | Nao | Sim |
| `detail_suffix` | Sufixo do detalhamento. Padrao: `ext`. | Nao | Sim |

### Atributos obsoletos de evidencia

Nao use estes atributos em questoes `adoption`. Os conversores rejeitam esses
campos e orientam o uso de `evidence_text`.

| Atributo obsoleto | Substituicao |
|---|---|
| `evidence` | Use `evidence_text`. |
| `evidence_type` | Use `evidence_text`. |
| `evidence_mandatory` | Use `evidence_text`; uploads automaticos sao obrigatorios. |
| `evidence_allowed_filetypes` | Use questao `upload` explicita se precisar customizar. |
| `evidence_min_files` | Use questao `upload` explicita se precisar customizar. |
| `evidence_max_files` | Use questao `upload` explicita se precisar customizar. |
| `evidence_suffix` | O sufixo automatico atual e `evi`. |

## Uploads e evidencias

Ha duas formas de solicitar arquivos.

### Questao `upload` explicita

Use quando precisar controlar tipos e quantidades de arquivos.

```md
### q2004evi [upload]
question: **Anexe evidencia documental do plano de TI.**
mandatory: true
visible_if: q2001 == sim
allowed_filetypes: pdf, doc, docx, zip
min_files: 1
max_files: 3
```

### Evidencia automatica com `evidence_text`

Use quando a evidencia acompanha uma questao comum ou `adoption`.

```md
### q2004 [single]
question: **A organizacao possui plano de TI vigente?**
mandatory: true
scale: sim_nao
evidence_text: Anexe evidencia documental do plano de TI.
```

No `.lss`, uploads automaticos usam por padrao:

| Atributo LimeSurvey | Valor |
|---|---|
| `allowed_filetypes` | `pdf, docx, zip` |
| `min_num_of_files` | `1` |
| `max_num_of_files` | `1` |

## Recomendacoes de autoria

Para maxima compatibilidade entre `.docx` e `.lss`, prefira os nomes canonicos:

- Tipos: `single`, `multi`, `short`, `long`, `upload`, `multi_text`, `array`,
  `array_numbers`, `adoption`.
- Listas: `options` e `subquestions`.
- Texto da pergunta: `question`.
- Condicao: `visible_if`.
- Evidencia: `evidence_text`.
- Obrigatoriedade: `mandatory: true` ou `mandatory: false`.

Evite depender de aliases portugueses quando o mesmo arquivo precisa gerar
`.docx` e `.lss`, porque o `.lss` aceita mais aliases que o `.docx`.

Trate o `.docx` como documento de revisao visual. A representacao completa de
regras, obrigatoriedade, condicoes, atributos LimeSurvey e uploads fica no
`.lss`.

## Validacao manual recomendada

Apos alterar um questionario ou os conversores, execute ao menos uma geracao
manual:

```bash
python md2docx.py modelo_teste.md output.docx --template-docx exemplo\TSID03-ANEXO_QUESTIONARIO.docx
python md2lss.py modelo_teste.md output.lss --sid 431594
```

Confira especialmente:

- Se todas as questoes aparecem no `.docx`.
- Se o `.lss` importa no LimeSurvey.
- Se `visible_if` referencia apenas questoes existentes no mesmo target.
- Se uploads e evidencias foram gerados com os limites esperados.
