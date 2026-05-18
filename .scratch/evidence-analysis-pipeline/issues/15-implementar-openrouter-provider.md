# Implementar OpenRouterProvider com texto normalizado

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Implement the OpenRouter Provedor de IA using the Chat Completions API. OpenRouter should receive the Prompt de analise and a textual representation of the Pacote de evidencia, because file upload support is not assumed.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

The provider should use the configured OpenRouter model and request structured JSON output when the model supports `response_format`.

## Acceptance criteria

- [ ] OpenRouterProvider reads `OPENROUTER_API_KEY` when no explicit token is provided.
- [ ] OpenRouterProvider uses the configured model.
- [ ] The request is sent to OpenRouter Chat Completions.
- [ ] The request includes Prompt de analise, item assertions, evidence metadata and normalized text from Pacote de evidencia.
- [ ] The request includes canonical JSON response instructions and `response_format` or equivalent structured output configuration when supported.
- [ ] Missing API key records a clear error.
- [ ] OpenRouter API errors record an error without corrupting checkpoint.
- [ ] Automated tests use mocks and perform no real network calls.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/13-extrair-abstracao-provedor-ia.md
