# Pipeline de analise de evidencias enviadas por auditados

Data: 2026-05-17

## Objetivo

Criar um CLI unico para pre-analisar evidencias enviadas em respostas de questionario. Para cada evidencia enviada, o script deve comparar o que o auditado afirmou adotar com o que a evidencia suporta, usando um checklist especifico e um modelo de IA.

A saida deve produzir conclusoes por item afirmado, com estado de conformidade e fundamentacao revisavel por auditor humano.

## Escopo

Incluido:

- Ler uma planilha de respostas no formato de `kimi_dummy.xlsx`.
- Processar apenas respostas com `submitdate` preenchido.
- Usar `firstname` como identificador do auditado e como nome do subdiretorio em uma raiz de evidencias.
- Detectar colunas de evidencia por um segmento `evi` no codigo da coluna, excluindo colunas `[filecount]`.
- Localizar o arquivo fisico pelo atributo `name` do objeto de upload armazenado na celula da planilha.
- Normalizar evidencias, incluindo ZIPs com multiplos arquivos internos.
- Executar uma chamada principal de IA por analise de evidencia, usando checklist especifico.
- Persistir checkpoint para retomar processamento sem reavaliar evidencias ja concluidas para o mesmo provedor/modelo/configuracao.
- Gerar trilha auditavel e relatorio consolidado.

Fora do escopo inicial:

- Interface web de revisao.
- Decisao final automatizada de auditoria.
- Busca recursiva de arquivos fora do diretorio direto do auditado.
- Uso de conhecimento externo para suprir lacunas da evidencia.

## Linguagem de dominio

Os termos canonicos ficam em `CONTEXT.md`. Em especial:

- **Auditado**: organizacao cuja resposta sera analisada.
- **Resposta analisavel**: resposta com `submitdate` preenchido.
- **Coluna de evidencia**: coluna cujo codigo contem segmento `evi`, exceto `[filecount]`.
- **Evidencia enviada**: arquivo unico enviado em uma coluna de evidencia; pode ser um ZIP.
- **Pacote de evidencia**: representacao normalizada da evidencia antes da IA.
- **Checklist de analise**: criterios versionados que orientam o julgamento.
- **Conclusao de conformidade**: resultado por item afirmado.
- **Pre-analise de auditoria**: natureza da decisao assistida por IA.

## Interface do CLI

Forma proposta:

```bash
python analisar_evidencias.py respostas.xlsx evidencias/ --questionario igovti_2026.md --provider gemini --model gemini-*
```

Argumentos principais:

- `respostas.xlsx`: planilha exportada do LimeSurvey.
- `evidencias/`: raiz de evidencias, com um subdiretorio por auditado.
- `--questionario`: arquivo SurveyMD usado para mapear questoes, itens, textos e evidencias.
- `--provider`: provedor de IA, inicialmente `gemini`.
- `--model`: modelo especifico do provedor.
- `--checklists-dir`: diretorio dos checklists, padrao `checklists/`.
- `--out-dir`: diretorio de saida, padrao `.saida_analise/`.
- `--prompt-version`: versao fixa do template de prompt.
- `--skip-errors`: opcional; quando presente, pula erros ja registrados.

## Fluxo principal

O script deve ser unico na experiencia de uso, mas internamente executar as fases abaixo no mesmo comando:

1. Carregar a planilha e manter apenas respostas com `submitdate`.
2. Carregar o questionario para obter metadados das questoes.
3. Identificar colunas de evidencia.
4. Para cada resposta analisavel, resolver o diretorio `evidencias/<firstname>/`.
5. Para cada coluna de evidencia com valor preenchido, ler o objeto de upload.
6. Validar que ha exatamente um arquivo no objeto de upload.
7. Usar o atributo `name` para localizar o arquivo fisico no diretorio do auditado.
8. Determinar os itens afirmados vinculados aquela evidencia.
9. Resolver o checklist aplicavel.
10. Normalizar a evidencia em um pacote de evidencia.
11. Calcular a identidade da analise.
12. Consultar o checkpoint; se ja houver resultado `completed`, pular a chamada de IA.
13. Chamar o provedor de IA quando necessario.
14. Validar a resposta JSON contra o schema esperado.
15. Gravar imediatamente o registro de analise.
16. Ao final, gerar ou atualizar o relatorio consolidado.

## Resolucao de arquivos

A celula da coluna de evidencia contem uma lista JSON-like com metadados do upload. O pipeline deve usar o atributo `name` do unico objeto da lista.

Exemplo de valor:

```json
[
  {
    "title": "Regimento interno",
    "comment": "",
    "name": "Regimento%20Interno.pdf",
    "filename": "fu_8kvbt3jmj3eigg5",
    "ext": "pdf"
  }
]
```

Regras:

- O lookup fisico usa `name`, nao `filename`.
- Se `name` estiver URL-encoded, o script deve decodificar para procurar o arquivo.
- O caminho esperado e `evidencias/<firstname>/<name_decodificado>`.
- A busca inicial nao deve ser recursiva.
- A ausencia do arquivo gera registro com estado `erro`.
- Mais de um objeto de upload gera `erro`, pois a regra do questionario e um arquivo por resposta.

## Itens afirmados

O script deve gerar conclusoes apenas para afirmacoes que exigem suporte evidencial.

Regras:

- Em questoes de adocao, considerar apenas respostas principais `adpar` e `admai`.
- Para questoes de adocao, incluir tambem os detalhamentos `ext[...]` marcados como `Y`.
- Em questoes `array` com respostas `sim/nao`, considerar subitens respondidos como `sim`.
- Em evidencias especificas, como `q2804eviA`, considerar apenas o item especifico, como `q2804[A]`.
- Respostas `naoad`, `adfor`, `admen`, `naoap`, vazias e subitens `nao` nao produzem conclusao de conformidade.

## Checklists

Os checklists devem ser arquivos versionados, separados do questionario.

Estrutura inicial:

```text
checklists/
  q1001.md
  q2102.md
  q2708.md
  q2804_A.md
```

Resolucao:

1. Para evidencia especifica de item, tentar `checklists/<questao>_<item>.md`.
2. Se nao existir, tentar `checklists/<questao>.md`.
3. Se nenhum checklist existir, registrar erro sem chamar IA.

Cada checklist deve conter:

- contexto da questao;
- itens que pode avaliar;
- criterios de conformidade;
- evidencias aceitaveis;
- sinais de insuficiencia;
- observacoes de interpretacao;
- restricoes especificas.

## Normalizacao de evidencias

O modelo nao deve receber ZIP bruto como unica fonte. O script deve criar um pacote de evidencia antes do julgamento.

Tratamento inicial por tipo:

- PDF: texto por pagina e metadados disponiveis.
- DOCX: texto de paragrafos e tabelas.
- XLSX/CSV: abas, colunas, dimensoes e conteudo relevante.
- TXT/MD: texto direto.
- PNG/JPG: OCR ou descricao multimodal, conforme provedor.
- ZIP: inventario, validacao contra path traversal, extracao dos arquivos suportados e registro dos nao suportados.

Arquivos protegidos por senha, ilegíveis ou nao suportados devem gerar `erro` ou aparecer como lacuna no pacote, conforme o ponto de falha.

## Chamada de IA

Havera uma chamada principal por analise de evidencia. A entrada deve incluir:

- auditado;
- questao base;
- coluna de evidencia;
- resposta declarada;
- itens afirmados;
- checklist aplicavel;
- pacote de evidencia;
- schema JSON esperado.

Se o pacote exceder limites praticos do modelo, o script pode fazer uma fase previa de fichamento por documento, pagina, aba ou fatia. Mesmo nesse caso, o julgamento final continua sendo consolidado por evidencia.

O prompt deve instruir o modelo a:

- avaliar somente os criterios do checklist;
- comparar afirmacoes do auditado com as evidencias;
- nao preencher lacunas com conhecimento externo;
- produzir uma conclusao para cada item afirmado;
- fundamentar cada conclusao com arquivo, pagina, trecho ou elemento observado;
- declarar lacunas quando a evidencia nao comprovar o item;
- devolver apenas JSON aderente ao schema.

## Schema de resultado

Cada analise deve retornar uma lista de conclusoes por item afirmado.

Estados permitidos:

- `conforme`: a evidencia suporta diretamente o item afirmado.
- `nao_conforme`: a evidencia contradiz ou nao comprova o item afirmado.
- `inconclusivo`: a evidencia foi analisada, mas e ambigua, parcial, ilegivel em parte ou depende de contexto externo.
- `erro`: a analise nao pode ser executada corretamente.

Campos por conclusao:

- `item_codigo`;
- `item_texto`;
- `afirmacao_auditado`;
- `estado`;
- `justificativa`;
- `lacunas`;
- `arquivos_referenciados`;
- `trechos_ou_elementos`;
- `paginas_ou_localizacao`;
- `confianca`, se o provedor permitir uma estimativa controlada.

## Checkpoint e deduplicacao

O script deve gravar um checkpoint incremental em `.saida_analise/analyses.jsonl`.

A identidade da analise deve incluir:

```text
auditado
+ coluna_evidencia
+ nome_original_arquivo
+ hash_conteudo
+ provider
+ model
+ checklist_hash
+ prompt_version
```

Comportamento:

- Se a identidade ja existir com status `completed`, pular a chamada de IA.
- Se existir com status `error`, tentar novamente por padrao.
- Se `--skip-errors` for usado, pular tambem identidades com status `error`.
- Gravar o registro imediatamente ao final de cada analise, antes de passar para a proxima.

Esse desenho permite continuar de onde parou e impede que a mesma evidencia do mesmo auditado seja avaliada mais de uma vez para o mesmo provedor, modelo, checklist e versao de prompt.

## Saidas

Diretorio padrao:

```text
.saida_analise/
  analyses.jsonl
  relatorio_conformidade.xlsx
```

`analyses.jsonl` deve conter uma linha por analise de evidencia:

- identidade da analise;
- status `completed` ou `error`;
- auditado;
- identificadores da resposta;
- questao e coluna de evidencia;
- metadados do upload;
- caminho do arquivo e hash;
- checklist e hash;
- provedor, modelo e prompt version;
- resumo do pacote de evidencia;
- resultado JSON ou erro;
- timestamps.

`relatorio_conformidade.xlsx` deve conter uma linha por conclusao de conformidade:

- auditado;
- questao;
- item;
- afirmacao do auditado;
- estado;
- justificativa;
- lacunas;
- arquivos, paginas, trechos ou elementos referenciados;
- evidencia enviada;
- provedor e modelo;
- data da analise;
- status de revisao humana vazio.

## Provedores

A arquitetura deve expor uma interface interna simples:

```text
analisar(prompt, pacote, schema) -> JSON
```

Implementacao inicial: Gemini.

OpenRouter deve ser previsto como adaptador posterior, porque o suporte a arquivos, visao e limites varia por modelo.

## Erros e seguranca

O pipeline deve tratar arquivos de evidencia como entrada nao confiavel.

Regras obrigatorias:

- Nao executar conteudo embutido em XLSX, DOCX, PDF ou ZIP.
- Validar ZIP contra path traversal.
- Limitar tamanho total extraido.
- Limitar quantidade de arquivos internos por ZIP.
- Registrar arquivos ignorados ou nao suportados.
- Nunca inventar conclusao quando a evidencia nao pode ser lida.
- Manter prompts, metadados e resultados no checkpoint local para rastreabilidade; redacao ou mascaramento de dados sensiveis fica fora do escopo inicial e deve ser tratado como requisito separado.

## Criterios de aceite

- Processa somente linhas com `submitdate`.
- Usa `firstname` para localizar o diretorio do auditado.
- Usa `name` do objeto de upload para localizar o arquivo fisico.
- Detecta `q2804eviA` como coluna de evidencia.
- Rejeita celula com multiplos arquivos.
- Nao chama IA quando nao ha checklist.
- Gera checkpoint incremental.
- Ao rodar duas vezes com a mesma entrada, nao reavalia analises `completed`.
- Reprocessa quando arquivo, modelo, checklist ou `prompt_version` mudam.
- Gera relatorio XLSX com uma linha por conclusao.
- Distingue `nao_conforme`, `inconclusivo` e `erro`.
