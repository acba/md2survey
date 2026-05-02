import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import md2docx
import md2lss


TARGET_MD = """---
title: Target Test
sid: 700
target: municipal, estadual
---

# Target Test

## Grupo: g1 | Grupo comum

### qcommon [single]
mandatory: true

Pergunta comum.

options:
- sim | Sim
- nao | Não

### qmun [short]
target: municipal

Pergunta municipal.

### qest [short]
target: estadual

Pergunta estadual.

## Grupo: g2 | Grupo municipal

### qmunonly [short]
target: municipal

Somente municipal.
"""


class TargetTests(unittest.TestCase):
    def write_md(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "survey.md"
        path.write_text(text, encoding="utf-8")
        return path

    def codes_by_group(self, survey):
        return {group.code: [q.code for q in group.questions] for group in survey.groups}

    def test_lss_filters_questions_by_target_and_omits_empty_groups(self):
        survey = md2lss.parse_markdown(self.write_md(TARGET_MD))

        municipal = md2lss.filter_survey_by_target(survey, "municipal")
        estadual = md2lss.filter_survey_by_target(survey, "estadual")

        self.assertEqual(self.codes_by_group(municipal), {"g1": ["qcommon", "qmun"], "g2": ["qmunonly"]})
        self.assertEqual(self.codes_by_group(estadual), {"g1": ["qcommon", "qest"]})

    def test_docx_filters_questions_by_target_and_omits_empty_groups(self):
        survey = md2docx.parse_markdown(self.write_md(TARGET_MD))

        municipal = md2docx.filter_survey_by_target(survey, "municipal")
        estadual = md2docx.filter_survey_by_target(survey, "estadual")

        self.assertEqual(self.codes_by_group(municipal), {"g1": ["qcommon", "qmun"], "g2": ["qmunonly"]})
        self.assertEqual(self.codes_by_group(estadual), {"g1": ["qcommon", "qest"]})

    def test_unknown_question_target_fails(self):
        text = TARGET_MD.replace("target: municipal\n\nPergunta municipal.", "target: federal\n\nPergunta municipal.")

        with self.assertRaisesRegex(ValueError, "target.*federal"):
            md2lss.parse_markdown(self.write_md(text))

        with self.assertRaisesRegex(ValueError, "target.*federal"):
            md2docx.parse_markdown(self.write_md(text))

    def test_question_target_without_header_target_fails(self):
        text = TARGET_MD.replace("target: municipal, estadual\n", "")

        with self.assertRaisesRegex(ValueError, "target.*cabeçalho|target.*cabecalho"):
            md2lss.parse_markdown(self.write_md(text))

        with self.assertRaisesRegex(ValueError, "target.*cabeçalho|target.*cabecalho"):
            md2docx.parse_markdown(self.write_md(text))

    def test_filtered_dependency_fails(self):
        text = TARGET_MD + """
### qbroken [short]
target: estadual
visible_if: qmun == abc

Dependencia quebrada.
"""
        survey = md2lss.parse_markdown(self.write_md(text))

        with self.assertRaisesRegex(ValueError, "qbroken.*qmun|qmun.*qbroken"):
            md2lss.filter_survey_by_target(survey, "estadual")

    def test_visible_if_values_are_not_treated_as_question_dependencies(self):
        text = """---
target: municipal, estadual
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [single]
options:
- adpar | Adota parcialmente
- admai | Adota em maior parte

Pergunta principal.

### q2 [short]
target: municipal
visible_if: q1 in [adpar, admai]

Pergunta dependente.
"""
        survey = md2lss.parse_markdown(self.write_md(text))

        municipal = md2lss.filter_survey_by_target(survey, "municipal")

        self.assertEqual(self.codes_by_group(municipal), {"g1": ["q1", "q2"]})

    def test_lss_adoption_expansion_inherits_question_target(self):
        text = """---
target: municipal, estadual
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [adoption]
target: municipal

Pergunta adoption.

detail_options:
- A | Detalhe A
"""
        survey = md2lss.parse_markdown(self.write_md(text))

        municipal = md2lss.filter_survey_by_target(survey, "municipal")
        estadual = md2lss.filter_survey_by_target(survey, "estadual")

        self.assertIn("q1ext", self.codes_by_group(municipal)["g1"])
        self.assertEqual(self.codes_by_group(estadual), {})

    def test_lss_cli_generates_suffixed_outputs_with_incremental_sid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_md = root / "survey.md"
            output_lss = root / "saida.lss"
            input_md.write_text(TARGET_MD, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "md2lss.py", str(input_md), str(output_lss)],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            municipal = root / "saida_municipal.lss"
            estadual = root / "saida_estadual.lss"
            self.assertTrue(municipal.exists())
            self.assertTrue(estadual.exists())
            self.assertIn("<sid><![CDATA[700]]></sid>", municipal.read_text(encoding="utf-8"))
            self.assertIn("<sid><![CDATA[701]]></sid>", estadual.read_text(encoding="utf-8"))
            self.assertFalse(output_lss.exists())

    def test_docx_cli_generates_suffixed_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_md = root / "survey.md"
            output_docx = root / "saida.docx"
            input_md.write_text(TARGET_MD, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "md2docx.py", str(input_md), str(output_docx)],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "saida_municipal.docx").exists())
            self.assertTrue((root / "saida_estadual.docx").exists())
            self.assertFalse(output_docx.exists())


if __name__ == "__main__":
    unittest.main()
