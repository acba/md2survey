# Rodar fluxo end-to-end com fixture minima

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Add a miniature end-to-end fixture and test that runs the CLI through inventory, evidence resolution, item selection, checklist resolution, normalization, fake-provider judgment, checkpointing and report generation.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

The fixture should prove the full offline path with representative cases: valid evidence, ZIP evidence, missing checklist and missing file.

## Acceptance criteria

- [ ] A miniature response spreadsheet fixture includes at least one submitted row and one unsubmitted row.
- [ ] The fixture raiz de evidencias includes one directly readable evidence file.
- [ ] The fixture raiz de evidencias includes one ZIP evidence with supported internal content.
- [ ] The fixture includes one missing-file case.
- [ ] The fixture includes one missing-checklist case.
- [ ] The CLI can run end to end with the fake provider and no network.
- [ ] The first run writes checkpoint records and a relatorio de conformidade.
- [ ] A second identical run skips completed analyses.
- [ ] The report includes rows for successful conclusions and error cases.
- [ ] The test demonstrates that the pipeline remains a single user-facing command.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/01-inventariar-analises-de-evidencia.md
- .scratch/evidence-analysis-pipeline/issues/02-resolver-evidencia-enviada.md
- .scratch/evidence-analysis-pipeline/issues/03-selecionar-itens-afirmados.md
- .scratch/evidence-analysis-pipeline/issues/04-aplicar-catalogo-checklists.md
- .scratch/evidence-analysis-pipeline/issues/05-normalizar-evidencias.md
- .scratch/evidence-analysis-pipeline/issues/06-gravar-checkpoint-idempotente.md
- .scratch/evidence-analysis-pipeline/issues/07-julgamento-consolidado-provider-fake.md
- .scratch/evidence-analysis-pipeline/issues/08-gerar-relatorio-conformidade.md
