# Aplicar catalogo de checklists versionados

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Add checklist resolution to the pipeline. Each analise de evidencia must resolve a checklist de analise before any IA call can happen. Item-specific checklists take precedence over base-question checklists, and missing checklists block model execution.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should expose checklist content and a stable checklist hash for checkpoint identity.

## Acceptance criteria

- [ ] The CLI accepts or defaults a checklist directory.
- [ ] Item-specific evidence first tries a checklist keyed by question and item.
- [ ] Base-question checklist fallback is used when no item-specific checklist exists.
- [ ] Missing checklist produces an error state for that analysis and does not call IA.
- [ ] Checklist content is available to prompt assembly.
- [ ] A stable checklist hash is computed for identidade da analise.
- [ ] Automated tests cover item-specific precedence, fallback, missing checklist and hash changes.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/01-inventariar-analises-de-evidencia.md
- .scratch/evidence-analysis-pipeline/issues/03-selecionar-itens-afirmados.md
