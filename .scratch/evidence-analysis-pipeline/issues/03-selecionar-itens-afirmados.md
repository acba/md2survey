# Selecionar itens afirmados por evidencia

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Extend the pipeline so each evidence candidate determines the itens afirmados it is expected to support. The behavior must follow the response semantics in the PRD: adoption responses, adoption detail items, array `sim/nao` items and item-specific evidence.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should produce item-level analysis targets while excluding weak, negative, non-applicable or empty adoption states.

## Acceptance criteria

- [ ] Adoption questions produce targets only for `adpar` and `admai`.
- [ ] Adoption detail values `ext[...] == Y` become item-level targets.
- [ ] Array subitems answered as `sim` become item-level targets.
- [ ] Item-specific evidence such as `q2804eviA` targets only the matching item.
- [ ] Responses `naoad`, `adfor`, `admen`, `naoap`, blank values and `nao` subitems do not produce conclusions.
- [ ] Item labels are derived from the questionnaire context where available.
- [ ] Automated tests cover each included and excluded response class.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/01-inventariar-analises-de-evidencia.md
