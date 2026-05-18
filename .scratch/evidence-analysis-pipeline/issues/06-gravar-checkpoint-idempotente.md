# Gravar checkpoint idempotente e retomavel

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Add registro de analise persistence and idempotent resume behavior. The pipeline must compute identidade da analise before model execution and use it to skip completed work while retrying errors by default.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should make the CLI safe to stop and rerun without duplicating completed IA analysis.

## Acceptance criteria

- [ ] The CLI writes an incremental JSONL checkpoint in the configured output directory.
- [ ] Each completed or error analysis is appended immediately after the analysis finishes.
- [ ] Identidade da analise includes auditado, coluna de evidencia, nome original da evidencia, content hash, provider, model, checklist hash and prompt version.
- [ ] Existing `completed` identities are skipped on rerun.
- [ ] Existing `error` identities are retried by default.
- [ ] A CLI option can skip prior `error` identities.
- [ ] Changing file content changes identity.
- [ ] Changing checklist hash changes identity.
- [ ] Changing provider, model or prompt version changes identity.
- [ ] Automated tests cover skip, retry and identity-change behavior.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/02-resolver-evidencia-enviada.md
- .scratch/evidence-analysis-pipeline/issues/04-aplicar-catalogo-checklists.md
