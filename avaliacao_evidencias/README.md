# Avaliacao de evidencias

Pipeline generico para pre-analise de evidencias enviadas por auditados em questionarios SurveyMD/LimeSurvey.

O pipeline e generico. Os prompts nao sao genericos: cada questionario deve ter seu proprio diretorio de prompts, com um arquivo por questao ou item especifico.

## O que o pipeline faz

1. Le a planilha de respostas `.xlsx`.
2. Processa somente linhas com `submitdate`, salvo quando `--include-unsubmitted` for informado.
3. Identifica colunas de evidencia, isto e, colunas cujo nome contem `evi` e que nao terminam em `[filecount]`.
4. Para cada evidencia, localiza o arquivo em `evidencias/<auditado>/<name>`, usando o atributo `name` do JSON de upload.
5. Resolve o prompt especifico da questao.
6. Monta o pacote de evidencia, incluindo texto extraido, inventario de ZIP e arquivos compativeis para upload no Gemini.
7. Chama o provider configurado: `fake`, `gemini` ou `openrouter`.
8. Valida a resposta JSON do modelo.
9. Grava checkpoint incremental em JSONL.
10. Gera `relatorio_conformidade.xlsx`.

## Estrutura esperada

Exemplo:

```text
respostas.xlsx
igovti_2026.md
evidencias/
  SEFAZ/
    q0101.zip
    fu_8ks.png
  SEEDUC/
    q0102.zip
avaliacao_evidencias/
  prompt_catalogs/
    igovti_2026_conservador_v2.yml
  prompts/
    igovti_2026_conservador_v2/
      q0101.md
      q1001.md
      q2804_A.md
```

O valor de `firstname` na planilha identifica o auditado e deve corresponder ao subdiretorio em `evidencias/<auditado>/`.

O arquivo fisico de evidencia e localizado primeiro pelo atributo `name` do objeto JSON existente na coluna de evidencia. O atributo `filename` do LimeSurvey nao e usado como chave de busca.

Quando o arquivo exportado pelo LimeSurvey nao preserva exatamente esse nome, o pipeline tambem procura variantes com o padrao de exportacao do LimeSurvey, por exemplo:

```text
name na planilha:
Resolu%C3%A7%C3%A3o%20SECTI%20159-2023%20Pol%C3%ADtica%20de%20Seguran%C3%A7a%20da%20Informa%C3%A7%C3%A3o.pdf

arquivo exportado:
00006_11_resolução-secti-159-2023-pol-tica-de-segurança-da-informação.pdf
```

Essa resolucao tenta, nesta ordem: nome exato decodificado, prefixo numerico inferido do id da resposta e da ordem da coluna de evidencia, e fallback por nome normalizado.

Cada coluna de evidencia deve conter exatamente um arquivo. Esse arquivo pode ser `.zip`; nesse caso, o ZIP pode conter varios arquivos internos.

## Instalar dependencias

Na raiz do repositorio:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Se a venv ja existir:

```bash
.venv/bin/pip install -r requirements.txt
```

## Gerar prompts

Para o iGovTI 2026, a versao recomendada e `igovti_2026_conservador_v2`.

Fonte de verdade:

```text
avaliacao_evidencias/prompt_catalogs/igovti_2026_conservador_v2.yml
```

Prompts gerados:

```text
avaliacao_evidencias/prompts/igovti_2026_conservador_v2/
```

Para regenerar:

```bash
.venv/bin/python -m avaliacao_evidencias.prompt_catalog build \
  avaliacao_evidencias/prompt_catalogs/igovti_2026_conservador_v2.yml \
  igovti_2026.md \
  avaliacao_evidencias/prompts/igovti_2026_conservador_v2
```

Edite o YAML, nao os Markdown gerados. O gerador e deterministico: se o YAML e o questionario nao mudarem, os Markdown gerados devem ser identicos.

## Validar sem chamar IA

Use o provider `fake` para validar inventario, resolucao de arquivos, prompts, checkpoint e relatorio:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --prompt-version v2 \
  --provider fake \
  --model fake \
  --out-dir .saida_analise
```

O provider `fake` nao faz julgamento substantivo. Ele retorna conclusoes `inconclusivo` para testar o fluxo sem rede.

## Processar respostas sem submitdate

Por padrao, o pipeline ignora respostas sem `submitdate`, porque elas normalmente representam respostas nao submetidas ou rascunhos.

Para incluir essas respostas mesmo assim, use `--include-unsubmitted`:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --prompt-version v2 \
  --provider fake \
  --model fake \
  --out-dir .saida_analise \
  --include-unsubmitted
```

Essa flag afeta o inventario inicial de analises. A deduplicacao por checkpoint continua valendo normalmente.

## Executar com Gemini

Configure a chave:

```bash
export GEMINI_API_KEY="..."
```

Execute:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --prompt-version v2 \
  --provider gemini \
  --model gemini-2.5-flash \
  --out-dir .saida_analise
```

O Gemini usa `google-genai`. Arquivos compativeis sao enviados pela Files API. Evidencias ZIP sao validadas contra path traversal e arquivos internos compativeis sao extraidos temporariamente para upload.

## Executar com OpenRouter

Configure a chave:

```bash
export OPENROUTER_API_KEY="..."
```

Execute:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --prompt-version v2 \
  --provider openrouter \
  --model google/gemini-2.5-flash \
  --out-dir .saida_analise
```

O OpenRouter recebe o prompt e o pacote de evidencia normalizado em texto pela API de Chat Completions. O request inclui `response_format` com JSON schema quando suportado pelo modelo.

## Listar analises sem processar

Para conferir quais evidencias seriam processadas:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --list-only
```

## Retomada e deduplicacao

O pipeline grava um checkpoint incremental em:

```text
.saida_analise/analyses.jsonl
```

Uma analise com `status = completed` nao e reprocessada se a identidade for a mesma.

A identidade considera:

- auditado;
- coluna de evidencia;
- nome original da evidencia;
- hash do arquivo de evidencia;
- provider;
- model;
- hash do prompt;
- `prompt_version`.

Erros sao retentados por padrao. Use `--skip-errors` para pular erros ja registrados:

```bash
.venv/bin/python -m avaliacao_evidencias respostas.xlsx evidencias/ \
  --questionario igovti_2026.md \
  --prompts-dir avaliacao_evidencias/prompts/igovti_2026_conservador_v2 \
  --prompt-version v2 \
  --provider gemini \
  --model gemini-2.5-flash \
  --out-dir .saida_analise \
  --skip-errors
```

## Saidas

```text
.saida_analise/
  analyses.jsonl
  relatorio_conformidade.xlsx
```

`analyses.jsonl` contem uma linha por analise tentada, incluindo metadados, provider, modelo, resultado e erro quando houver.

`relatorio_conformidade.xlsx` contem uma linha por conclusao de conformidade, com estado, justificativa, lacunas e referencias.

Estados possiveis:

- `conforme`: a evidencia suporta diretamente o item afirmado.
- `nao_conforme`: a evidencia nao comprova ou contradiz o item afirmado.
- `inconclusivo`: ha indicios, mas falta elemento essencial para concluir.
- `erro`: a analise nao pode ser realizada por falha tecnica.

## Manutencao de prompts

Para melhorar prompts:

1. Edite `avaliacao_evidencias/prompt_catalogs/igovti_2026_conservador_v2.yml`.
2. Regenere os Markdown com `python -m avaliacao_evidencias.prompt_catalog build ...`.
3. Rode os testes.
4. Execute o pipeline com novo `--prompt-version` se quiser forcar reprocessamento mesmo quando os arquivos de evidencia nao mudaram.

Exemplo:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias.PromptCatalogV2Tests
```

Para rodar todos os testes do pacote:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias
```

## Observacoes de auditoria

O resultado e uma pre-analise automatizada. O relatorio deve ser tratado como insumo para revisao humana, nao como decisao final de auditoria.

Os prompts v2 adotam postura conservadora: na duvida entre `conforme` e `inconclusivo`, o modelo deve usar `inconclusivo`; na ausencia de suporte direto, deve usar `nao_conforme`.
