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

ARRAY_NUMBERS_MD = """---
title: Array Numbers Test
sid: 903
---

# Array Numbers Test

## Grupo: g1 | Grupo 1

### q1 [array_numbers]
question: **Informe o quantitativo de profissionais por área e vínculo.**
mandatory: true

subquestions:
- TI | Tecnologia da Informação
- SI | Segurança da Informação

options:
- efetivos | Servidores efetivos
- comissionados | Servidores comissionados
- terceirizados | Terceirizados
"""

REPEAT_GROUP_CHAIN_MD = """---
title: Repeat Group Chain Test
sid: 904
---

# Repeat Group Chain Test

## Grupo: g1 | Grupo 1
> Descricao do grupo.

### q1 [short]
repeat_group_description: true
question: Pergunta 1.

### q2 [short]
question: Pergunta 2.

### q3 [short]
repeat_group_description: true
question: Pergunta 3.

### q4 [short]
question: Pergunta 4.
"""

ARRAY_CONDITION_MD = """---
title: Array Condition Test
sid: 905
---

# Array Condition Test

## Escala: sim_nao
type: single
- sim | Sim
- nao | Nao

## Grupo: g1 | Grupo 1

### q1 [array]
mandatory: true
scale: sim_nao

Praticas adotadas.

subquestions:
- A | Pratica A
- B | Pratica B

### q1eviA [upload]
visible_if: q1.A == sim

Envie evidencia da pratica A.
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

    def test_array_numbers_uses_limesurvey_numeric_array_shape(self):
        survey = md2lss.parse_markdown(self.write_md(ARRAY_NUMBERS_MD))

        root = ET.fromstring(md2lss.build_lss(survey, sid=903))
        question = next(row for row in root.find("questions/rows") if row.findtext("title") == "q1")
        self.assertEqual(question.findtext("type"), ":")

        answers = [
            row
            for row in root.find("answers/rows")
            if row.findtext("qid") == question.findtext("qid")
        ]
        self.assertEqual(answers, [])

        subquestions = [
            row
            for row in root.find("subquestions/rows")
            if row.findtext("parent_qid") == question.findtext("qid")
        ]
        self.assertEqual([row.findtext("title") for row in subquestions], ["TI", "SI", "efetivos", "comissionados", "terceirizados"])
        self.assertEqual([row.findtext("scale_id") for row in subquestions], ["0", "0", "1", "1", "1"])
        self.assertEqual([row.findtext("type") for row in subquestions], ["T", "T", "T", "T", "T"])

        attributes = {
            row.findtext("attribute"): row.findtext("value")
            for row in root.find("question_attributes/rows")
            if row.findtext("qid") == question.findtext("qid")
        }
        self.assertEqual(attributes["input_boxes"], "1")
        self.assertEqual(attributes["multiflexible_min"], "0")
        self.assertEqual(attributes["multiflexible_max"], "1000")
        self.assertEqual(attributes["multiflexible_step"], "-1")

    def test_repeat_group_description_keeps_following_plain_questions_in_same_group(self):
        survey = md2lss.parse_markdown(self.write_md(REPEAT_GROUP_CHAIN_MD))

        groups = {group.code: [q.code for q in group.questions] for group in survey.groups}

        self.assertEqual(groups["g1_q1"], ["q1", "q2"])
        self.assertEqual(groups["g1_q3"], ["q3", "q4"])
        self.assertNotIn("g1", groups)
        self.assertNotIn("g1_parte2", groups)

    def test_lss_hides_total_question_count_by_default(self):
        survey = md2lss.parse_markdown(self.write_md(PLAIN_MULTI_MD))

        root = ET.fromstring(md2lss.build_lss(survey, sid=901))
        survey_row = next(iter(root.find("surveys/rows")))

        self.assertEqual(survey_row.findtext("showxquestions"), "N")

    def test_array_subquestion_condition_does_not_prefix_cfieldname_with_plus(self):
        survey = md2lss.parse_markdown(self.write_md(ARRAY_CONDITION_MD))

        root = ET.fromstring(md2lss.build_lss(survey, sid=905))
        evidence = next(row for row in root.find("questions/rows") if row.findtext("title") == "q1eviA")
        condition = next(row for row in root.find("conditions/rows") if row.findtext("qid") == evidence.findtext("qid"))

        self.assertEqual(evidence.findtext("relevance"), '((905X1000X10000A.NAOK == "sim"))')
        self.assertEqual(condition.findtext("cfieldname"), "905X1000X10000A")


if __name__ == "__main__":
    unittest.main()
