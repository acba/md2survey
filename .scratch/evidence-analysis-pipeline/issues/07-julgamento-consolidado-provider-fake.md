# Executar julgamento consolidado com provider fake

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Add provider-neutral prompt assembly, output schema validation and a fake provider for tests. The pipeline should perform one julgamento consolidado per analise de evidencia and produce one conclusao de conformidade per item afirmado.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should prove the IA integration contract end to end without using network calls.

## Acceptance criteria

- [ ] Prompt assembly includes auditado, questao base, coluna de evidencia, declared response, itens afirmados, checklist and pacote de evidencia.
- [ ] The prompt instructs the model not to use external knowledge to fill gaps.
- [ ] The output schema accepts only controlled states: `conforme`, `nao_conforme`, `inconclusivo`, `erro`.
- [ ] Each item afirmado receives one conclusao de conformidade.
- [ ] Each conclusion includes justificativa, lacunas and evidence references fields.
- [ ] Invalid provider JSON is recorded as an error without crashing the whole run.
- [ ] Fake provider tests verify prompt content, schema validation and item-level output.
- [ ] No real network call is required for automated tests.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/03-selecionar-itens-afirmados.md
- .scratch/evidence-analysis-pipeline/issues/04-aplicar-catalogo-checklists.md
- .scratch/evidence-analysis-pipeline/issues/05-normalizar-evidencias.md
- .scratch/evidence-analysis-pipeline/issues/06-gravar-checkpoint-idempotente.md
