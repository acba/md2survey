# Gerar prompts conservadores para o iGovTI 2026

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Create the first production Prompt de analise set for the iGovTI 2026 questionnaire using conservative Postura de julgamento. Generate one prompt file for each Coluna de evidencia detected in the questionnaire, including item-specific prompts such as `q2804_A.md`.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

The prompt set should live under `avaliacao_evidencias/prompts/igovti_2026_conservador/` and be specific to the iGovTI 2026 questionnaire. The pipeline remains generic; this prompt set does not.

## Acceptance criteria

- [ ] The prompt directory `avaliacao_evidencias/prompts/igovti_2026_conservador/` exists.
- [ ] There is one prompt for every evidence column detected from `igovti_2026.md`.
- [ ] The set includes `q2804_A.md` for `q2804eviA`.
- [ ] Each prompt uses the approved structure: Objetivo da analise, Itens afirmados a avaliar, Evidencias aceitaveis, Criterios de conformidade, Sinais de nao conformidade, Lacunas que tornam a analise inconclusiva and Instrucoes de julgamento.
- [ ] Each prompt encodes conservative Postura de julgamento.
- [ ] Each prompt reinforces the canonical JSON output requirement.
- [ ] A coverage check verifies that every evidence column has a matching prompt file.
- [ ] Prompt content is specific to the question and not a generic reused template with only the code changed.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/11-substituir-checklists-por-prompts.md
