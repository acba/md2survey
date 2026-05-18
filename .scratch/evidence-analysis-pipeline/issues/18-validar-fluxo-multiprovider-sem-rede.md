# Validar fluxo end-to-end multi-provider sem rede

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Add end-to-end tests that validate provider selection and Prompt de analise behavior for Fake, Gemini and OpenRouter paths without real network calls. These tests should prove that the same pipeline remains generic while providers and prompt sets vary by configuration.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should verify the integrated behavior after prompt resolution, provider abstraction, Gemini, OpenRouter and prompt set generation are in place.

## Acceptance criteria

- [ ] End-to-end tests cover FakeProvider with a real prompt file.
- [ ] End-to-end tests cover GeminiProvider through mocks, including file upload calls for compatible evidence.
- [ ] End-to-end tests cover OpenRouterProvider through mocks, including normalized text sent in the request.
- [ ] Tests verify that missing Prompt de analise blocks only that Analise de evidencia.
- [ ] Tests verify that provider name changes Identidade da analise.
- [ ] Tests verify that model changes Identidade da analise.
- [ ] Tests verify that prompt content changes Identidade da analise.
- [ ] Tests verify that the relatorio de conformidade is generated from canonical JSON output for each provider path.
- [ ] No test performs real network calls.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/14-implementar-gemini-provider-google-genai.md
- .scratch/evidence-analysis-pipeline/issues/15-implementar-openrouter-provider.md
- .scratch/evidence-analysis-pipeline/issues/16-gerar-prompts-igovti-2026-conservador.md
