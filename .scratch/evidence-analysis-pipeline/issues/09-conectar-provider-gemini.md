# Conectar provider Gemini real

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Implement a Gemini provider adapter behind the provider-neutral analysis interface. The adapter should be optional at runtime and must not make network calls in the default automated test suite.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should allow real IA execution when credentials and model are configured, while preserving the fake-provider path for deterministic tests.

## Acceptance criteria

- [ ] Gemini is selectable through the CLI provider option.
- [ ] The adapter uses the same provider-neutral request and response contract as the fake provider.
- [ ] Missing credentials or configuration produce a clear error.
- [ ] Provider/model identity flows into checkpoint identity and registros de analise.
- [ ] Network/API errors are recorded as analysis errors without corrupting the checkpoint.
- [ ] Automated tests use mocks or fakes and do not call the Gemini API.
- [ ] Documentation or CLI help states the required environment/configuration for real Gemini execution.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/07-julgamento-consolidado-provider-fake.md
