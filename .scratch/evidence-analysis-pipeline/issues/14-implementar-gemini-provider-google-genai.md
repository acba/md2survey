# Implementar GeminiProvider com google-genai e upload de arquivos

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Implement the Gemini Provedor de IA using the `google-genai` package. Gemini should upload compatible evidence files through the Gemini Files API and include textual context for ZIP inventory, unsupported files and normalized extracted content where needed.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

For ZIP Evidencia enviada, the pipeline must safely extract the ZIP and upload compatible Evidencias internas individually. The ZIP inventory and unsupported internal files must be included as context.

## Acceptance criteria

- [ ] `google-genai` is added to project dependencies.
- [ ] GeminiProvider reads `GEMINI_API_KEY` when no explicit token is provided.
- [ ] GeminiProvider uses the configured model.
- [ ] Compatible direct evidence files are uploaded with the Gemini Files API.
- [ ] Compatible files extracted from ZIP evidence are uploaded individually.
- [ ] ZIP inventory and unsupported files are included in textual context.
- [ ] Gemini requests include the Prompt de analise, item assertions, evidence metadata and canonical JSON response requirement.
- [ ] Missing API key records a clear error.
- [ ] Gemini API errors record an error without corrupting checkpoint.
- [ ] Automated tests use mocks and perform no real network calls.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/13-extrair-abstracao-provedor-ia.md
