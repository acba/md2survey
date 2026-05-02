import tempfile
import unittest
from pathlib import Path

import md2docx
import md2lss


FRONTMATTER_MD = """---
title: Multiline Metadata
sid: 800
expires: "2026-06-01 23:59:59"
welcome: |
  <p>Primeira linha</p>
  <p>Segunda linha</p>
endtext: |
  <p>Fim</p>
---

# Survey

## Grupo: g1 | Grupo 1

### q1 [short]

Pergunta.
"""


class FrontmatterTests(unittest.TestCase):
    def write_md(self, text: str = FRONTMATTER_MD) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "survey.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_lss_frontmatter_supports_literal_blocks_and_expires(self):
        survey = md2lss.parse_markdown(self.write_md())
        self.assertIn("<p>Primeira linha</p>", survey.meta["welcome"])
        self.assertIn("<p>Segunda linha</p>", survey.meta["welcome"])
        self.assertEqual(survey.meta["endtext"], "<p>Fim</p>")

        xml = md2lss.build_lss(survey, sid=800)

        self.assertIn("<expires><![CDATA[2026-06-01 23:59:59.000]]></expires>", xml)
        self.assertIn("<surveyls_welcometext><![CDATA[<p>Primeira linha</p>", xml)
        self.assertIn("<p>Segunda linha</p>", xml)
        self.assertNotIn("<p>|</p>", xml)

    def test_docx_frontmatter_supports_literal_blocks(self):
        survey = md2docx.parse_markdown(self.write_md())

        self.assertIn("<p>Primeira linha</p>", survey.meta["welcome"])
        self.assertIn("<p>Segunda linha</p>", survey.meta["welcome"])
        self.assertEqual(survey.meta["endtext"], "<p>Fim</p>")


if __name__ == "__main__":
    unittest.main()
