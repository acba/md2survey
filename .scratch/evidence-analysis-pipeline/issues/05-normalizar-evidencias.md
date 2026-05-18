# Normalizar evidencias em pacote analisavel

Status: ready-for-agent

## Parent

.scratch/evidence-analysis-pipeline/PRD.md

## What to build

Create pacote de evidencia generation for supported evidence files. The model should receive normalized text, metadata, inventory and unsupported-file notes rather than arbitrary raw files.

All implementation for this pipeline must live under `avaliacao_evidencias/`.

This slice should include safe ZIP handling and enough extractors to support useful offline tests without network access.

## Acceptance criteria

- [ ] Text and Markdown files are normalized as direct text.
- [ ] DOCX files expose paragraphs and table text.
- [ ] XLSX/CSV files expose sheets or columns and relevant tabular content.
- [ ] PDF files are handled when the chosen dependency is available, with graceful unsupported behavior otherwise.
- [ ] Image files are represented through OCR, multimodal placeholder, or an explicit unsupported note according to the implemented capability.
- [ ] ZIP files are inventoried and supported internal files are normalized.
- [ ] ZIP path traversal is blocked.
- [ ] ZIP extraction caps total extracted size and internal file count.
- [ ] Unsupported or password-protected files produce `erro` or explicit lacunas without invented content.
- [ ] Automated tests cover safe ZIP extraction, unsupported files and at least two supported file types.

## Blocked by

- .scratch/evidence-analysis-pipeline/issues/02-resolver-evidencia-enviada.md
