# PRD: Pipeline de pre-analise de evidencias enviadas por auditados

Status: ready-for-agent

## Problem Statement

Auditores recebem uma planilha de respostas de questionario e uma raiz de evidencias organizada por auditado. Cada auditado pode afirmar que adota praticas, controles ou subitens especificos, e pode enviar um arquivo de evidencia para sustentar essas afirmacoes. Hoje falta um pipeline reprodutivel para localizar cada evidencia enviada, entender quais itens afirmados ela deveria comprovar, aplicar um checklist de analise especifico e gerar conclusoes de conformidade fundamentadas.

O risco central e duplo: uma evidencia pode ser analisada de forma generica, sem aderencia ao checklist correto, ou pode ser reavaliada repetidamente quando o processamento falha no meio. O auditor precisa de uma pre-analise rastreavel, retomavel e revisavel, sem tratar a saida da IA como decisao final.

## Solution

Construir um CLI unico que leia a planilha de respostas, processe apenas respostas analisaveis, encontre as evidencias enviadas na raiz de evidencias, determine os itens afirmados vinculados a cada coluna de evidencia, normalize os arquivos em pacotes de evidencia e execute um julgamento consolidado com IA usando checklists versionados.

O CLI deve gravar um registro de analise imediatamente depois de cada analise de evidencia. Antes de chamar o provedor de IA, deve calcular uma identidade da analise e pular qualquer analise ja concluida para a mesma combinacao de auditado, coluna de evidencia, arquivo, hash de conteudo, provedor, modelo, checklist e versao de prompt. Ao final, deve gerar um relatorio de conformidade com uma linha por conclusao de conformidade.

## User Stories

1. As an auditor, I want to run a single command over a response spreadsheet and an evidence root, so that I can start the pre-analysis without orchestrating several scripts manually.
2. As an auditor, I want only responses with `submitdate` filled to be processed, so that incomplete questionnaire rows do not produce audit conclusions.
3. As an auditor, I want the auditado to be identified by the spreadsheet `firstname` value, so that the pipeline uses the same organization code as the evidence directory structure.
4. As an auditor, I want each response to map to `evidencias/<auditado>/`, so that evidence files are resolved from the organized evidence root.
5. As an auditor, I want evidence columns to be detected by an `evi` segment rather than only by an `evi` suffix, so that item-specific columns such as `q2804eviA` are not missed.
6. As an auditor, I want `[filecount]` columns to be ignored as evidence columns, so that upload metadata does not become a false analysis target.
7. As an auditor, I want the pipeline to read the upload object stored in each evidence cell, so that it can recover the original evidence metadata exported by LimeSurvey.
8. As an auditor, I want the physical evidence file to be located by the upload object's `name` attribute, so that the pipeline uses the same filename present in the organized auditado directory.
9. As an auditor, I want URL-encoded evidence names to be decoded during file lookup, so that filenames exported with spaces or accents still resolve correctly.
10. As an auditor, I want a missing evidence file to produce an `erro` record, so that the failure is visible without stopping the whole run.
11. As an auditor, I want an upload cell with more than one file object to produce an `erro`, so that the pipeline enforces the questionnaire rule of one file per response.
12. As an auditor, I want malformed upload metadata to produce an `erro`, so that bad input is reported explicitly.
13. As an auditor, I want adoption-scale questions to be analyzed only for `adpar` and `admai`, so that weak or negative adoption states do not produce unsupported compliance checks.
14. As an auditor, I want adoption detail options marked as `Y` to become item-level analysis targets, so that the evidence is compared with every detailed assertion the auditado made.
15. As an auditor, I want array subitems answered as `sim` to become item-level analysis targets, so that each claimed subpractice receives its own conclusion.
16. As an auditor, I want item-specific evidence such as `q2804eviA` to evaluate only the matching item, so that conclusions do not overreach beyond the evidence request.
17. As an auditor, I want responses such as `naoad`, `adfor`, `admen`, `naoap`, blank values and `nao` subitems to be excluded from conclusions, so that the report focuses on asserted adoption.
18. As an auditor, I want checklists to live separately from the questionnaire, so that audit criteria can evolve without changing the questionnaire definition.
19. As an auditor, I want the pipeline to prefer an item-specific checklist when evidence is item-specific, so that detailed evidence requests can have stricter criteria.
20. As an auditor, I want the pipeline to fall back to the base-question checklist when no item-specific checklist exists, so that common question-level checks are reusable.
21. As an auditor, I want the pipeline not to call IA when no checklist exists, so that the model does not perform generic unsupported audit analysis.
22. As an auditor, I want each evidence file to be normalized before IA, so that the model receives a consistent package rather than arbitrary raw files.
23. As an auditor, I want PDFs to be converted into page-aware text and metadata, so that conclusions can cite the relevant page when possible.
24. As an auditor, I want DOCX files to expose paragraphs and tables, so that formal documents can be reviewed structurally.
25. As an auditor, I want spreadsheets and CSV files to expose sheets, columns and relevant content, so that tabular evidence can be evaluated.
26. As an auditor, I want image files to be handled by OCR or multimodal description, so that screenshots and scanned evidence can still support analysis.
27. As an auditor, I want ZIP files to be inventoried and safely extracted, so that one uploaded ZIP can contain several internal evidence documents.
28. As an auditor, I want ZIP extraction to block unsafe paths and excessive contents, so that untrusted evidence cannot write outside the extraction area or exhaust resources.
29. As an auditor, I want unsupported or password-protected files to be recorded as errors or lacunas, so that the model does not invent what it could not inspect.
30. As an auditor, I want one consolidated IA judgment per analysis of evidence, so that all item conclusions for the same evidence are coherent.
31. As an auditor, I want large evidence packages to support an intermediate summarization step, so that oversized evidence can still be judged consistently.
32. As an auditor, I want the prompt to require JSON output that follows a schema, so that downstream reporting is deterministic.
33. As an auditor, I want each conclusion to have one of `conforme`, `nao_conforme`, `inconclusivo` or `erro`, so that audit review can distinguish unsupported evidence from processing failures.
34. As an auditor, I want each conclusion to cite files, pages, excerpts or observed elements, so that a human reviewer can validate the basis of the pre-analysis.
35. As an auditor, I want each conclusion to describe lacunas, so that the auditado or auditor can understand what evidence was missing.
36. As an auditor, I want the model to be instructed not to use external knowledge to fill gaps, so that conclusions are based only on the submitted evidence and checklist.
37. As an auditor, I want every completed analysis to be appended to a checkpoint immediately, so that a crash does not lose previous IA work.
38. As an auditor, I want reruns to skip completed analyses with the same identity, so that the same evidence is not evaluated twice for the same provider and model.
39. As an auditor, I want errors to be retried by default, so that temporary API or file issues can be corrected and rerun.
40. As an auditor, I want an option to skip previous errors, so that I can generate a report without repeatedly hitting known failures.
41. As an auditor, I want changing the file content, checklist, provider, model or prompt version to force reprocessing, so that stale conclusions are not reused after meaningful input changes.
42. As an auditor, I want an auditable analysis log, so that every IA result can be traced to its inputs, checklist, model and prompt version.
43. As an auditor, I want a consolidated spreadsheet report, so that reviewers can filter conclusions by auditado, question, item, state and evidence.
44. As an auditor, I want the report to include an empty human review status, so that the IA output is treated as pre-analysis rather than final audit decision.
45. As a developer, I want the IA provider behind a stable internal interface, so that Gemini can be implemented first and OpenRouter can be added later.
46. As a developer, I want parsing, evidence resolution, item selection, normalization, checkpointing, provider calls and report generation separated behind simple interfaces, so that each part can be tested in isolation.
47. As a developer, I want the CLI to expose clear options for provider, model, checklist directory, output directory and prompt version, so that runs are reproducible.
48. As a developer, I want safe handling of untrusted files, so that survey evidence never executes embedded content.
49. As a developer, I want the pipeline to reuse the questionnaire model where practical, so that question texts, upload columns and item labels stay aligned with SurveyMD definitions.
50. As a reviewer, I want the PRD and design language to use the domain glossary terms, so that issues and implementation plans remain consistent.

## Implementation Decisions

- Build a single user-facing CLI for the evidence analysis pipeline. Internally it may be modular, but the operator should run one command.
- The CLI accepts a response spreadsheet, a raiz de evidencias, a SurveyMD questionnaire source, provider/model options, a checklist directory, an output directory, a prompt version and an option to skip prior errors.
- Process only respostas analisaveis, defined as rows with `submitdate` filled.
- Use `firstname` as the identificador do auditado and as the directory name under the raiz de evidencias.
- Detect colunas de evidencia by the presence of an `evi` segment in the response column code, excluding paired `[filecount]` metadata columns.
- Parse each evidence cell as a list of upload objects and require exactly one object. Empty cells produce no analysis; malformed cells or multiple objects produce an error record.
- Resolve the physical evidencia enviada using the upload object's `name` attribute. The `filename` attribute is internal LimeSurvey storage metadata and is not the lookup key.
- Decode URL-encoded names for lookup while preserving original metadata in the registro de analise.
- Do not search recursively outside the auditado directory in the initial implementation.
- Determine itens afirmados using question type and response semantics: adoption `adpar`/`admai`, adoption detail `ext[...] == Y`, array item `sim`, and item-specific evidence suffixes.
- Do not generate conclusions for weak, negative, non-applicable or empty adoption states.
- Store checklists as versioned files outside the questionnaire. Resolve item-specific checklists before base-question checklists.
- Do not call IA without a matching checklist de analise.
- Introduce a deep questionnaire-context module that converts SurveyMD metadata into lookup structures for base questions, evidence columns, item labels and response semantics.
- Introduce a deep response-inventory module that emits candidate analyses from the spreadsheet and questionnaire context.
- Introduce a deep evidence-resolution module that turns upload metadata and auditado directory rules into either a located file or an error.
- Introduce a deep item-selection module that maps one evidence column and one response row to the itens afirmados in scope.
- Introduce a deep evidence-normalization module that creates a pacote de evidencia for PDFs, DOCX, spreadsheets, text files, images and ZIPs.
- Introduce a deep checklist-catalog module that resolves checklists and exposes content plus stable hashes.
- Introduce a deep prompt/schema module that assembles provider-neutral model input and validates structured output.
- Introduce a provider adapter boundary with a simple `analisar(prompt, pacote, schema) -> JSON` shape. Gemini is the first implementation; OpenRouter is a later adapter.
- Introduce a checkpoint module that computes identidade da analise, loads prior records and appends completed or error records immediately after each analysis.
- The identidade da analise includes auditado, coluna de evidencia, nome original da evidencia, content hash, provider, model, checklist hash and prompt version.
- Completed records are skipped on rerun when the same identity is encountered.
- Error records are retried by default and skipped only when the operator explicitly requests it.
- Introduce a report module that converts analysis records into a relatorio de conformidade with one row per conclusao de conformidade.
- The checkpoint stores enough input metadata, hashes, prompt/checklist identity, provider/model identity, result and timestamps to support audit traceability.
- The report presents pre-analise de auditoria, not final audit decisions.
- The result schema uses controlled states: `conforme`, `nao_conforme`, `inconclusivo` and `erro`.
- Each conclusao de conformidade requires fundamentacao da conclusao: referenced files, pages or locations when available, observed excerpts or elements, gaps and justification.
- ZIP handling must validate path traversal, cap extracted size and cap internal file count.
- Evidence files are untrusted input. The pipeline must not execute embedded content from PDFs, DOCX, XLSX, ZIPs or other submitted files.
- Local checkpoint retention includes prompts, metadata and results by default; masking or redaction of sensitive data is a separate future requirement.

## Testing Decisions

- Tests should focus on external behavior of each module boundary, not private implementation details.
- The response-inventory tests should use small synthetic spreadsheets that include submitted and unsubmitted rows, empty evidence cells, malformed upload metadata and multiple-file upload objects.
- The column-detection tests should cover standard evidence columns, `[filecount]` metadata columns and item-specific evidence columns such as `q2804eviA`.
- The evidence-resolution tests should cover direct lookup by `name`, URL-decoded lookup, missing files and ignoring `filename` as the physical lookup key.
- The item-selection tests should cover adoption responses `adpar` and `admai`, ignored responses `naoad`, `adfor`, `admen`, `naoap`, adoption detail `ext[...] == Y`, array `sim/nao` items and item-specific evidence.
- The checklist-catalog tests should cover item-specific precedence, base-question fallback and no-checklist behavior.
- The evidence-normalization tests should cover at least text, DOCX, XLSX/CSV, PDF where dependencies allow, image placeholder behavior if OCR/multimodal support is abstracted, safe ZIP extraction and unsupported files.
- The checkpoint tests should prove that completed identities are skipped, errors are retried by default, errors can be skipped explicitly and changed file/checklist/model/prompt version changes the identity.
- The provider adapter tests should use a fake provider, not a real network call, to verify prompt assembly, schema validation and error handling.
- The report tests should verify one output row per conclusao de conformidade and preservation of auditado, question, item, state, justification, gaps and references.
- CLI tests should verify that a dry or fake-provider run can process a miniature fixture end to end and produce checkpoint plus report artifacts.
- Existing tests around evidence generation and LSS structure provide prior art for fixture-driven unit tests and should guide style.
- Manual validation should include a run against a small copy of the sample response spreadsheet and a tiny raiz de evidencias with one PDF/text evidence, one ZIP and one missing-file case.
- Network/API calls should not be part of the default automated test suite.

## Out of Scope

- A web UI for reviewing evidence and conclusions side by side.
- Final automated audit decisions.
- Recursive file search outside the auditado directory.
- Generic IA analysis without a checklist de analise.
- Use of external knowledge to fill gaps in submitted evidence.
- Building the OpenRouter adapter in the first implementation if Gemini is implemented first.
- Redaction or masking of sensitive data in local checkpoints.
- Downloading files from LimeSurvey or any remote service.
- Changing the questionnaire authoring format.
- Generating or maintaining the full set of production checklists for every question, unless separately requested.
- Replacing auditor human review.

## Further Notes

- This PRD was synthesized from the consolidated design document `docs/superpowers/specs/2026-05-17-evidence-analysis-pipeline-design.md` and the project glossary in `CONTEXT.md`.
- The local issue tracker status for this PRD is `ready-for-agent`.
- The most important implementation risk is letting the CLI remain physically simple while keeping internals modular enough to test. The user-facing shape is a single command; the engineering shape should be a set of deep modules with stable boundaries.
- The second major risk is model overreach. The prompt, checklist catalog and schema validation should bias toward `nao_conforme`, `inconclusivo` or `erro` when the evidence does not directly support an item afirmado.
