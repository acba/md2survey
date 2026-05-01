import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import md2docx
import md2lss


class AdoptionEvidenceTests(unittest.TestCase):
    def test_adoption_does_not_create_implicit_evidence_question(self):
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

            survey = md2lss.parse_markdown(path)

        codes = [q.code for group in survey.groups for q in group.questions]
        self.assertNotIn("q1evi", codes)
        self.assertIn("q1extDevi", codes)

    def test_docx_adoption_ignores_evidence_attribute(self):
        q = md2docx.Question(
            code="q1",
            type="adoption",
            text_lines=["Texto da adoption."],
            attrs={"evidence": "upload"},
        )
        survey = md2docx.Survey()
        explanation_rows = []

        with patch.object(md2docx, "add_subgroup_title"), \
            patch.object(md2docx, "add_question_title"), \
            patch.object(md2docx, "add_option_table", return_value=object()), \
            patch.object(md2docx, "add_option_row"), \
            patch.object(md2docx, "add_explanation_row", side_effect=lambda _table, text: explanation_rows.append(text)), \
            patch.object(md2docx, "add_help"), \
            patch.object(md2docx, "add_blank"):
            md2docx.render_adoption(object(), survey, q)

        self.assertNotIn("Indique quais as evidências dessa adoção:", explanation_rows)

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
