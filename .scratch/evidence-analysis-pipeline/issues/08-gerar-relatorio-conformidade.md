# Gerar relatorio de conformidade

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Convert registros de analise into a relatorio de conformidade spreadsheet. The report should be auditor-facing, with one row per conclusao de conformidade and enough context for human review.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should make a completed fake-provider run useful to inspect without reading JSONL manually.

## Acceptance criteria

- [ ] The CLI writes `relatorio_conformidade.xlsx` in the configured output directory.
- [ ] The report has one row per conclusao de conformidade.
- [ ] Each row includes auditado, questao, item, afirmacao do auditado, estado, justificativa and lacunas.
- [ ] Each row includes evidence filename and referenced files/pages/trechos/elements when present.
- [ ] Each row includes provider, model and analysis date.
- [ ] Each row includes an empty human review status column.
- [ ] Error records appear in the report with useful context.
- [ ] Automated tests verify row count and key columns from a sample checkpoint.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/06-gravar-checkpoint-idempotente.md
- .scratch/evidence-analysis-pipeline/issues/07-julgamento-consolidado-provider-fake.md
