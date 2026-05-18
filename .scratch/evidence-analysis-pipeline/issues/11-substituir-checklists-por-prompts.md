# Substituir checklists por prompts de analise

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Update the pipeline vocabulary and CLI behavior so the question-specific artifact is a Prompt de analise rather than a checklist. The pipeline must load one prompt file per questao base or item-specific evidence, and it must not fall back to a generic judgment prompt when a prompt is missing.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should keep the pipeline generic for SurveyMD/LimeSurvey questionnaires while allowing each questionnaire to provide its own prompt directory.

## Acceptance criteria

- [ ] The CLI accepts `--prompts-dir` as the primary directory option for prompt files.
- [ ] Existing `--checklists-dir` behavior is either removed or kept only as a backward-compatible alias with clear help text.
- [ ] Prompt resolution uses `<questao>.md` for question-level evidence.
- [ ] Prompt resolution uses `<questao>_<item>.md` for item-specific evidence such as `q2804_A.md`.
- [ ] A missing Prompt de analise records an error for only that Analise de evidencia.
- [ ] Missing prompt never triggers a generic model judgment.
- [ ] Checkpoint identity uses prompt hash and prompt version terminology.
- [ ] Tests are updated from checklist vocabulary to Prompt de analise vocabulary.

## Blocked by

None - can start immediately
