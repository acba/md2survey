# Resolver evidencia enviada no diretorio do auditado

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Extend the pipeline so each candidate analise de evidencia resolves its physical evidencia enviada from the auditado directory. File lookup must use the upload object's `name` attribute, not the internal LimeSurvey `filename`.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

The slice should turn upload metadata and raiz de evidencias rules into either a located file with metadata or an error record that later stages can persist.

## Acceptance criteria

- [ ] Evidence lookup uses `evidencias/<firstname>/<name>`.
- [ ] URL-encoded `name` values are decoded for physical lookup.
- [ ] The original upload metadata is preserved for later registro de analise output.
- [ ] The internal `filename` attribute is not used as the physical lookup key.
- [ ] Upload cells with more than one file object produce an `erro`.
- [ ] Missing files produce an `erro` without stopping the run.
- [ ] Initial lookup is not recursive outside the direct auditado directory.
- [ ] Automated tests cover decoded names, missing files, multiple upload objects and ignoring `filename`.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/01-inventariar-analises-de-evidencia.md
