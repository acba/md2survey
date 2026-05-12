import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import md2docx
import md2lss


class AdoptionEvidenceTests(unittest.TestCase):
    def test_lss_rejects_obsolete_adoption_evidence_attribute(self):
        text = """---
sid: 123456
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
mandatory: true
evidence: upload

Texto da adoption.

### q1extDevi [upload]
mandatory: false
visible_if: q1ext.D == Y
allowed_filetypes: doc, pdf, docx, zip
min_files: 1
max_files: 3

Anexe evidencia documental.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "evidence.*obsoleto|evidence.*obsolete"):
                md2lss.parse_markdown(path)

    def test_docx_rejects_obsolete_adoption_evidence_attribute(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
evidence: upload

Texto da adoption.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "evidence.*obsoleto|evidence.*obsolete"):
                md2docx.parse_markdown(path)

    def test_lss_adoption_evidence_text_creates_upload_question(self):
        text = """---
sid: 123456
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
mandatory: true
question:**Texto da adoption.**
explain: Explicacao curta.
evidence_text: Anexe evidencia documental.

detail_options:
- A | Detalhe A
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertIn("q1evi", questions)
        self.assertEqual(questions["q1evi"].type, "upload")
        self.assertTrue(questions["q1evi"].mandatory)
        self.assertEqual(questions["q1evi"].visible_if, "q1 in [adpar, admai]")
        self.assertEqual(questions["q1evi"].attrs["allowed_filetypes"], "pdf, docx, zip")
        self.assertEqual(questions["q1evi"].attrs["min_files"], "1")
        self.assertEqual(questions["q1evi"].attrs["max_files"], "1")

        root = ET.fromstring(md2lss.build_lss(survey, sid=123456))
        question_rows = {
            row.findtext("title"): row
            for row in root.find("questions/rows")
        }
        self.assertEqual(question_rows["q1evi"].findtext("type"), "|")
        self.assertEqual(question_rows["q1evi"].findtext("mandatory"), "Y")
        self.assertEqual(questions["q1evi"].text(), "Anexe evidencia documental.")

        root = ET.fromstring(md2lss.build_lss(survey, sid=123456))
        question_rows = {
            row.findtext("title"): row
            for row in root.find("questions/rows")
        }
        self.assertIn("Explicacao curta.", question_rows["q1"].findtext("question"))
        self.assertIn("question-help-container text-info col-12", question_rows["q1"].findtext("question"))
        self.assertEqual(question_rows["q1evi"].findtext("type"), "|")
        self.assertEqual(question_rows["q1evi"].findtext("mandatory"), "Y")

    def test_lss_adoption_evidence_text_inherits_target(self):
        text = """---
target: municipal, estadual
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
target: municipal
evidence_text: Anexe evidencia documental.

Texto da adoption.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        municipal = md2lss.filter_survey_by_target(survey, "municipal")
        estadual = md2lss.filter_survey_by_target(survey, "estadual")
        municipal_codes = [q.code for group in municipal.groups for q in group.questions]
        estadual_codes = [q.code for group in estadual.groups for q in group.questions]

        self.assertIn("q1evi", municipal_codes)
        self.assertNotIn("q1evi", estadual_codes)

    def test_lss_single_evidence_text_creates_upload_with_default_condition(self):
        text = """---
sid: 123456
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [single]
question: **Escolha uma opção.**
mandatory: true
evidence_text: Anexe evidencia documental.

options:
- sim | Sim
- nao | Não
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertIn("q1evi", questions)
        self.assertEqual(questions["q1evi"].type, "upload")
        self.assertTrue(questions["q1evi"].mandatory)
        self.assertEqual(questions["q1evi"].visible_if, "q1 in [sim, nao]")
        self.assertEqual(questions["q1evi"].attrs["allowed_filetypes"], "pdf, docx, zip")
        self.assertEqual(questions["q1evi"].attrs["min_files"], "1")
        self.assertEqual(questions["q1evi"].attrs["max_files"], "1")

    def test_lss_multi_evidence_text_creates_upload_with_any_checked_condition(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [multi]
question: **Marque as opções.**
evidence_text: Anexe evidencia documental.

subquestions:
- A | Opção A
- B | Opção B
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertEqual(questions["q1evi"].visible_if, "q1.A == Y or q1.B == Y")

    def test_lss_common_evidence_if_overrides_default_condition(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [single]
question: **Escolha uma opção.**
evidence_text: Anexe evidencia documental.
evidence_if: q1 == sim

options:
- sim | Sim
- nao | Não
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertEqual(questions["q1evi"].visible_if, "q1 == sim")

    def test_lss_short_evidence_text_without_evidence_if_is_always_visible(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [short]
question: **Informe o valor.**
evidence_text: Anexe evidencia documental.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertEqual(questions["q1evi"].visible_if, "1")

    def test_docx_adoption_renders_explain_and_evidence_text(self):
        q = md2docx.Question(
            code="q1",
            type="adoption",
            text_lines=["Texto da adoption."],
            help="Ajuda da questao.",
            attrs={"explain": "Explicacao curta.", "evidence_text": "Anexe evidencia documental."},
        )
        survey = md2docx.Survey()
        paragraphs = []
        evidence_blocks = []

        with patch.object(md2docx, "add_subgroup_title"), \
            patch.object(md2docx, "add_question_title"), \
            patch.object(md2docx, "add_option_table", return_value=object()), \
            patch.object(md2docx, "add_option_row"), \
            patch.object(md2docx, "add_explanation_row"), \
            patch.object(md2docx, "add_help", side_effect=lambda _doc, text: paragraphs.append(("help", text, {}))), \
            patch.object(md2docx, "add_text_paragraph", side_effect=lambda _doc, text, **kwargs: paragraphs.append(("text", text, kwargs))), \
            patch.object(md2docx, "add_adoption_evidence_text", side_effect=lambda _doc, text: evidence_blocks.append(text)), \
            patch.object(md2docx, "add_blank"):
            md2docx.render_adoption(object(), survey, q)

        self.assertIn(("help", "Ajuda da questao.", {}), paragraphs)
        self.assertIn(("text", "Explicacao curta.", {"size": 9, "color": "5B9BD5", "align": md2docx.WD_ALIGN_PARAGRAPH.JUSTIFY, "left_indent": 10.16, "name": "Calibri", "space_after": 6}), paragraphs)
        self.assertEqual(evidence_blocks, ["Anexe evidencia documental."])

    def test_docx_common_question_renders_evidence_text(self):
        q = md2docx.Question(
            code="q1",
            type="short",
            text_lines=["Texto da pergunta."],
            attrs={"evidence_text": "Anexe evidencia documental."},
        )
        survey = md2docx.Survey()
        evidence_blocks = []

        with patch.object(md2docx, "start_question_page"), \
            patch.object(md2docx, "add_subgroup_title"), \
            patch.object(md2docx, "add_question_title"), \
            patch.object(md2docx, "add_adoption_explain"), \
            patch.object(md2docx, "add_answer_line"), \
            patch.object(md2docx, "add_help"), \
            patch.object(md2docx, "add_adoption_evidence_text", side_effect=lambda _doc, text: evidence_blocks.append(text)), \
            patch.object(md2docx, "add_blank"):
            md2docx.render_question(object(), survey, q)

        self.assertEqual(evidence_blocks, ["Anexe evidencia documental."])

    def test_docx_parser_ignores_repeat_group_description_directive(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
question: **Texto da adoption.**
repeat_group_description: true
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2docx.parse_markdown(path)

        question = survey.groups[0].questions[0]
        self.assertEqual(question.text_lines, ["**Texto da adoption.**"])
        self.assertNotIn("repeat_group_description", question.attrs)

    def test_docx_evidence_text_uses_discreet_callout(self):
        doc = md2docx.Document()

        md2docx.add_adoption_evidence_text(doc, "Anexe evidencia documental.")

        self.assertEqual(len(doc.tables), 1)
        table = doc.tables[0]
        self.assertEqual(table.cell(0, 0).text, "⇪")
        self.assertIn("Evidência documental", table.cell(0, 1).text)
        self.assertIn("Anexe evidencia documental.", table.cell(0, 1).text)

        cell_xml = table.cell(0, 1)._tc.xml
        self.assertIn('w:fill="EAF4FF"', cell_xml)
        self.assertIn('w:color="5B9BD5"', cell_xml)

        body_paragraph = table.cell(0, 1).paragraphs[1]
        self.assertEqual(body_paragraph.alignment, md2docx.WD_ALIGN_PARAGRAPH.JUSTIFY)
        body_run = body_paragraph.runs[0]
        self.assertEqual(body_run.font.name, "Calibri")
        self.assertEqual(body_run.font.size, md2docx.Pt(9))

    def test_lss_adoption_detail_defaults_to_enabled_and_not_mandatory(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]

Texto da adoption.

detail_options:
- A | Detalhe A
- B | Detalhe B
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        questions = {q.code: q for group in survey.groups for q in group.questions}
        self.assertIn("q1ext", questions)
        self.assertFalse(questions["q1ext"].mandatory)

    def test_lss_adoption_detail_false_disables_detail_question(self):
        text = """# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
detail: false

Texto da adoption.

detail_options:
- A | Detalhe A
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "survey.md"
            path.write_text(text, encoding="utf-8")

            survey = md2lss.parse_markdown(path)

        codes = [q.code for group in survey.groups for q in group.questions]
        self.assertNotIn("q1ext", codes)

    def test_docx_adoption_detail_defaults_to_enabled(self):
        q = md2docx.Question(
            code="q1",
            type="adoption",
            text_lines=["Texto da adoption."],
            detail_options=[md2docx.Option(code="A", text="Detalhe A")],
        )
        survey = md2docx.Survey()
        option_rows = []

        with patch.object(md2docx, "add_subgroup_title"), \
            patch.object(md2docx, "add_question_title"), \
            patch.object(md2docx, "add_option_table", return_value=object()), \
            patch.object(md2docx, "add_option_row", side_effect=lambda _table, text, symbol="🔿": option_rows.append(text)), \
            patch.object(md2docx, "add_explanation_row"), \
            patch.object(md2docx, "add_text_paragraph", side_effect=lambda _doc, text, **_kwargs: option_rows.append(text.removeprefix("☐  "))), \
            patch.object(md2docx, "add_help"), \
            patch.object(md2docx, "add_blank"):
            md2docx.render_adoption(object(), survey, q)

        self.assertIn("Detalhe A", option_rows)

    def test_docx_adoption_detail_false_disables_detail_rows(self):
        q = md2docx.Question(
            code="q1",
            type="adoption",
            text_lines=["Texto da adoption."],
            detail_options=[md2docx.Option(code="A", text="Detalhe A")],
            attrs={"detail": "false"},
        )
        survey = md2docx.Survey()
        option_rows = []

        with patch.object(md2docx, "add_subgroup_title"), \
            patch.object(md2docx, "add_question_title"), \
            patch.object(md2docx, "add_option_table", return_value=object()), \
            patch.object(md2docx, "add_option_row", side_effect=lambda _table, text, symbol="🔿": option_rows.append(text)), \
            patch.object(md2docx, "add_explanation_row"), \
            patch.object(md2docx, "add_text_paragraph", side_effect=lambda _doc, text, **_kwargs: option_rows.append(text.removeprefix("☐  "))), \
            patch.object(md2docx, "add_help"), \
            patch.object(md2docx, "add_blank"):
            md2docx.render_adoption(object(), survey, q)

        self.assertNotIn("Detalhe A", option_rows)


if __name__ == "__main__":
    unittest.main()
