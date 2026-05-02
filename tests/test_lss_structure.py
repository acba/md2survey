import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import md2lss


MULTI_MD = """---
title: Multi Test
sid: 900
---

# Multi Test

## Grupo: g1 | Grupo 1

### q1 [multi]
mandatory: true
min_answers: 1

Selecione as opções aplicáveis.

subquestions:
- A | Opção A
- B | Opção B
"""

PLAIN_MULTI_MD = """---
title: Plain Multi Test
sid: 901
---

# Plain Multi Test

## Grupo: g1 | Grupo 1

### q1 [multi]
mandatory: true

Selecione as opções aplicáveis.

subquestions:
- A | Opção A
- B | Opção B
"""

LONG_ADMIN_MD = """---
title: Long Admin Test
sid: 902
admin: Coordenadoria de Auditoria em Políticas de Tecnologia da Informação
---

# Long Admin Test

## Grupo: g1 | Grupo 1

### q1 [short]

Pergunta.
"""


class LssStructureTests(unittest.TestCase):
    def write_md(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "survey.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_multi_subquestions_use_limesurvey_text_type(self):
        survey = md2lss.parse_markdown(self.write_md(MULTI_MD))

        root = ET.fromstring(md2lss.build_lss(survey, sid=900))
        subquestion_types = [
            row.findtext("type")
            for row in root.find("subquestions/rows")
            if row.findtext("parent_qid") == "10000"
        ]

        self.assertEqual(subquestion_types, ["T", "T"])

    def test_plain_multi_subquestions_keep_limesurvey_multi_type(self):
        survey = md2lss.parse_markdown(self.write_md(PLAIN_MULTI_MD))

        root = ET.fromstring(md2lss.build_lss(survey, sid=901))
        subquestion_types = [
            row.findtext("type")
            for row in root.find("subquestions/rows")
            if row.findtext("parent_qid") == "10000"
        ]

        self.assertEqual(subquestion_types, ["M", "M"])

    def test_long_admin_fails_before_generating_unimportable_lss(self):
        survey = md2lss.parse_markdown(self.write_md(LONG_ADMIN_MD))

        with self.assertRaisesRegex(ValueError, "admin.*67.*50"):
            md2lss.build_lss(survey, sid=902)


if __name__ == "__main__":
    unittest.main()
