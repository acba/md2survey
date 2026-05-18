# Extrair abstracao de Provedor de IA

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Introduce a provider abstraction for model-backed Julgamento consolidado. The abstraction must hide provider-specific API details while preserving provider name, model, API credential source, prompt sending and canonical JSON result handling.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should keep FakeProvider as the offline deterministic provider and route the CLI through the same provider interface used by real providers.

## Acceptance criteria

- [ ] A provider interface exists for analyzing one Prompt de analise and one Pacote de evidencia.
- [ ] Provider selection is driven by CLI `--provider`.
- [ ] Model selection is driven by CLI `--model`.
- [ ] API token can be provided by environment variable or a documented configuration path.
- [ ] FakeProvider implements the same interface as real providers.
- [ ] Provider result is validated through the canonical JSON contract.
- [ ] Provider name and model flow into Identidade da analise and Registro de analise.
- [ ] Tests verify provider selection, fake execution and provider/model identity changes without network calls.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/12-criar-contrato-json-canonico.md
