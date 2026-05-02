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
importacao. Grupos que ficarem sem questoes apos o filtro sao omitidos. Se uma
questao de um target depender via `visible_if` de uma questao que nao existe
nesse mesmo target, a geracao falha com erro.

## Macro adoption

Use `[adoption]` para gerar a pergunta principal de grau de adocao, as
justificativas de nao aplicabilidade e, quando informado, o checklist de
detalhamento.

O macro `[adoption]` nao cria pergunta de evidencia automaticamente. Quando uma
evidencia for necessaria, declare uma pergunta normal no `.md`, com o tipo e a
condicao desejados:

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
- Checkboxes e radios renderizados para revisao humana.
- Questoes com `visible_if` simples aparecem aninhadas no DOCX de revisao.
- O `.lss` continua sendo o artefato correto para importacao no LimeSurvey.
