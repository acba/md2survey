# Survey Evidence Analysis

This context defines the language for analyzing evidence files submitted with SurveyMD/LimeSurvey questionnaire responses.

## Language

**Auditado**:
The organization or respondent whose submitted questionnaire response is being analyzed.
_Avoid_: órgão, entidade, respondente when the analysis refers to the accountable audited party.

**Identificador do auditado**:
The `firstname` value in the response spreadsheet, used as the canonical name of the **Auditado** and its **Diretório do auditado**.
_Avoid_: token, e-mail, nome do respondente.

**Resposta submetida**:
A completed questionnaire record for one **Auditado**.
_Avoid_: linha, registro, submissão when discussing the domain concept.

**Resposta analisável**:
A **Resposta submetida** that has a filled `submitdate` and is eligible for evidence analysis.
_Avoid_: qualquer linha da planilha.

**Questão base**:
The questionnaire question that contains the assertion being evaluated.
_Avoid_: pergunta principal when the question may be an array or item-specific question.

**Coluna de evidência**:
A questionnaire response column that records an uploaded evidence file for a **Questão base** or for a specific item of that question.
_Avoid_: coluna terminada em evi.

**Regra de coluna de evidência**:
A spreadsheet column is a **Coluna de evidência** when its question code contains an `evi` segment and it is not the paired `[filecount]` metadata column.
_Avoid_: suffix-only detection.

**Raiz de evidências**:
The top-level filesystem directory that contains one subdirectory per **Auditado** with that auditado's submitted evidence files.
_Avoid_: diretório de uploads when the files have already been organized by auditado.

**Diretório do auditado**:
The subdirectory inside the **Raiz de evidências** that contains the evidence files for one **Auditado**.
_Avoid_: pasta da resposta.

**Evidência enviada**:
The single file uploaded by the **Auditado** in a **Coluna de evidência**, including a ZIP file when that ZIP contains multiple internal documents.
_Avoid_: anexo when the analysis must reason about audit support.

**Pacote de evidência**:
The normalized representation of an **Evidência enviada**, including extracted text, document inventory, metadata, and unsupported-file notes.
_Avoid_: arquivo processado.

**Evidência interna**:
A file contained inside a ZIP **Evidência enviada** after safe extraction.
_Avoid_: anexo separado when it came from the same uploaded ZIP.

**Nome original da evidência**:
The `name` attribute stored inside a spreadsheet upload object and used to locate the physical **Evidência enviada** in the **Diretório do auditado**.
_Avoid_: filename when referring to the internal LimeSurvey storage id.

**Item afirmado**:
An item or practice that the **Auditado** claimed to adopt in the **Resposta submetida**.
_Avoid_: item marcado when the statement may come from a scale answer rather than only a checkbox.

**Adoção afirmada**:
An adoption-scale response that claims the practice is adopted enough to require evidentiary support.
_Avoid_: qualquer resposta de adoção.

**Análise de evidência**:
The evaluation of one **Evidência enviada** against the **Item afirmado** values it is expected to support.
_Avoid_: análise da pergunta when more than one evidence column can exist for the same question.

**Prompt de análise**:
A versioned, question-specific instruction that defines how an **Evidência enviada** must be evaluated for a **Questão base** or a specific item.
_Avoid_: prompt genérico when the evaluation criteria are specific to one question.

**Postura de julgamento**:
The evidentiary strictness encoded in a **Prompt de análise**, such as conservative or permissive evaluation.
_Avoid_: flag de execução when the strictness changes audit criteria.

**Conclusão de conformidade**:
The item-level result stating whether an **Item afirmado** is supported by the **Evidência enviada**.
_Avoid_: nota, escore.

**Estado de conformidade**:
The controlled result value for a **Conclusão de conformidade**: `conforme`, `nao_conforme`, `inconclusivo`, or `erro`.
_Avoid_: aprovado, reprovado.

**Fundamentação da conclusão**:
The evidence references, observed excerpts or elements, gaps, and audit rationale that justify one **Conclusão de conformidade**.
_Avoid_: comentário livre.

**Registro de análise**:
The auditable record of one **Análise de evidência**, including inputs, evidence identity, checklist identity, model identity, result, and errors.
_Avoid_: log when it is used as audit trace.

**Identidade da análise**:
The versioned identity that determines whether an **Análise de evidência** has already been performed and can be skipped on resume.
_Avoid_: apenas nome do arquivo.

**Relatório de conformidade**:
The auditor-facing consolidation of **Conclusões de conformidade** for review and follow-up.
_Avoid_: planilha final.

**Pré-análise de auditoria**:
The model-assisted assessment that suggests **Conclusões de conformidade** for human auditor review.
_Avoid_: decisão final.

**Julgamento consolidado**:
The model-assisted decision step that evaluates a complete **Pacote de evidência** against all **Itens afirmados** in scope for one **Análise de evidência**.
_Avoid_: uma chamada por item.

**Provedor de IA**:
The configured AI service that performs a **Julgamento consolidado** using a specific model and API credential.
_Avoid_: modelo when referring to the service integration rather than the model identifier.

## Relationships

- One **Resposta submetida** belongs to exactly one **Auditado**.
- Only a **Resposta analisável** is eligible to produce **Análises de evidência**.
- One **Identificador do auditado** maps one **Resposta submetida** to one **Diretório do auditado**.
- One **Questão base** may have one or more **Colunas de evidência**.
- One **Coluna de evidência** records at most one **Evidência enviada** per **Resposta submetida**.
- One **Raiz de evidências** contains one **Diretório do auditado** per **Auditado**.
- One **Diretório do auditado** contains the physical files referenced by the **Nome original da evidência** in that auditado's **Colunas de evidência**.
- One **Evidência enviada** produces one **Pacote de evidência** before model analysis.
- One ZIP **Evidência enviada** may contain many **Evidências internas**.
- One **Evidência enviada** can be analyzed against one or more **Itens afirmados**.
- One **Prompt de análise** applies to one **Questão base** or one specific item of that question.
- One **Prompt de análise** has one **Postura de julgamento**.
- One **Análise de evidência** normally has one **Julgamento consolidado**.
- One **Julgamento consolidado** is performed through one **Provedor de IA**.
- One **Análise de evidência** produces one **Conclusão de conformidade** for each **Item afirmado** in scope.
- One **Conclusão de conformidade** must include one **Fundamentação da conclusão**.
- One **Análise de evidência** produces one **Registro de análise**.
- One **Relatório de conformidade** consolidates many **Conclusões de conformidade**.
- One **Relatório de conformidade** presents **Pré-análises de auditoria** rather than final audit decisions.

## Example Dialogue

> **Dev:** "For q1001evi, should we analyze the file once for the whole question?"
> **Domain expert:** "Yes, but the result must still produce a conclusion for each item the auditado affirmed that the evidence is supposed to support."

## Flagged Ambiguities

- "Colunas terminadas em evi" excludes evidence columns such as `q2804eviA`; resolved term: **Coluna de evidência**.
- `filename` in the upload object is the internal LimeSurvey storage id; file lookup in the organized evidence directory uses **Nome original da evidência** from `name`.
- **Item afirmado** excludes weak or negative adoption states; only adoption claims that require evidence and `sim` array items are analyzed.
- "Mesma evidência" is not identified only by file name; resolved term: **Identidade da análise**.
- A missing **Prompt de análise** blocks only that **Análise de evidência**; the pipeline must not fall back to generic judgment.
- A different **Postura de julgamento** requires a different **Prompt de análise** so the **Identidade da análise** changes.
