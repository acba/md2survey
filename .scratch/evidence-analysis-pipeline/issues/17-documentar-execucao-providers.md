# Documentar execucao fake, Gemini e OpenRouter

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Document how to execute the evidence analysis pipeline with FakeProvider, GeminiProvider and OpenRouterProvider. The documentation must show how the generic pipeline is configured for a specific questionnaire by passing `--questionario` and `--prompts-dir`.

All implementation and docs for this pipeline should stay under `avaliacao_evidencias/` unless updating repository-level README is explicitly useful.

The documentation should be enough for a user to prepare evidence directories, configure API keys, run the process, resume it and inspect outputs.

## Acceptance criteria

- [ ] Documentation shows the expected `evidencias/<auditado>/` structure.
- [ ] Documentation explains that `firstname` maps the response row to the auditado directory.
- [ ] Documentation explains that evidence files are located by the upload object's `name` attribute.
- [ ] Documentation shows a fake/offline command.
- [ ] Documentation shows a Gemini command with `GEMINI_API_KEY`.
- [ ] Documentation shows an OpenRouter command with `OPENROUTER_API_KEY`.
- [ ] Documentation explains `--questionario`, `--prompts-dir`, `--provider`, `--model`, `--out-dir`, `--prompt-version` and `--skip-errors`.
- [ ] Documentation explains checkpoint resume behavior and output files.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/14-implementar-gemini-provider-google-genai.md
- .scratch/evidence-analysis-pipeline/issues/15-implementar-openrouter-provider.md
- .scratch/evidence-analysis-pipeline/issues/16-gerar-prompts-igovti-2026-conservador.md
