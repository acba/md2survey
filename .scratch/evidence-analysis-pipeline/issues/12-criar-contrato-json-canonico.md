# Criar contrato JSON canonico de saida

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Define the canonical JSON output contract for all Provedores de IA and validate every provider response against it before writing completed analysis records. The same contract must be used by Fake, Gemini and OpenRouter paths.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

The contract should produce one Conclusao de conformidade per Item afirmado, with controlled Estado de conformidade values and Fundamentacao da conclusao fields.

## Acceptance criteria

- [ ] The canonical schema is defined in the pipeline code.
- [ ] Valid provider responses with `status` and `conclusoes` are accepted.
- [ ] Each conclusion requires `item_codigo`, `item_texto`, `afirmacao_auditado`, `estado`, `justificativa`, `lacunas`, `arquivos_referenciados`, `trechos_ou_elementos` and `paginas_ou_localizacao`.
- [ ] `estado` is restricted to `conforme`, `nao_conforme`, `inconclusivo` and `erro`.
- [ ] Invalid provider JSON is recorded as an error without corrupting the checkpoint.
- [ ] The report continues to read records produced through the canonical schema.
- [ ] Tests cover valid output, invalid output and unsupported estado.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/11-substituir-checklists-por-prompts.md
