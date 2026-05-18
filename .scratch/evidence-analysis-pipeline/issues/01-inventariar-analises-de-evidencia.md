# Inventariar analises de evidencia a partir da planilha

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Build the first tracer bullet of the evidence analysis CLI: it should read a response spreadsheet and questionnaire definition, process only respostas analisaveis, detect colunas de evidencia, and list candidate analises de evidencia without resolving files or calling IA.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should establish the user-facing command shape and enough internal structure for later slices to reuse the inventory output. It should support a fake/no-op execution mode suitable for tests.

## Acceptance criteria

- [ ] A CLI entrypoint exists under `avaliacao_evidencias/`.
- [ ] The CLI accepts a response spreadsheet path, a raiz de evidencias path, a questionnaire path, provider/model options, checklist directory, output directory and prompt version.
- [ ] Rows without `submitdate` are ignored.
- [ ] `firstname` is treated as the identificador do auditado.
- [ ] Colunas de evidencia are detected by an `evi` segment in the question code.
- [ ] Paired `[filecount]` columns are ignored.
- [ ] Item-specific evidence columns such as `q2804eviA` are detected.
- [ ] Empty evidence cells do not produce candidate analyses.
- [ ] Malformed upload metadata is represented as a candidate-level error without stopping the run.
- [ ] Automated tests cover submitted versus unsubmitted rows, standard evidence columns, `[filecount]` columns and `q2804eviA`.

## Blocked by

None - can start immediately
