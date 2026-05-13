# Repository Guidelines

## Project Structure & Module Organization

This repository contains standalone Python CLI converters for SurveyMD workflows.
Keep source files at the repository root unless a module grows large enough to
justify a package.

- `md2docx.py`: converts SurveyMD Markdown to review/print DOCX.
- `md2lss.py`: converts SurveyMD Markdown to LimeSurvey `.lss`.
- `xlsx2md.py`: converts SurveyXLSX workbooks to SurveyMD Markdown.
- `md2docx_gpt.py` and `md2docx-deepseek-v2.py`: alternate DOCX converter variants.
- `modelo_teste.*`: sample input/output fixtures for manual validation.
- `exemplo/`: reference DOCX template assets.
- `requirements.txt`: runtime dependencies.

Avoid committing generated local artifacts unless they are intentional examples.
Do not commit `venv/`, caches, or temporary DOCX/XLSX outputs.

## Build, Test, and Development Commands

Create and activate a virtual environment before running tools:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run converters from the repository root:

```bash
python xlsx2md.py modelo_teste.xlsx modelo_teste.md
python md2lss.py modelo_teste.md modelo_teste.lss --sid 431594
python md2docx.py modelo_teste.md output.docx --template-docx exemplo/TSID03-ANEXO_QUESTIONARIO.docx
```

Use `python <script>.py --help` to verify the current CLI options before changing
arguments or defaults.

## Coding Style & Naming Conventions

Target Python 3 and follow the existing script style: 4-space indentation,
`argparse` for CLIs, `pathlib.Path` for paths, dataclasses for structured survey
models, and constants in `UPPER_SNAKE_CASE`. Keep functions focused on parsing,
transformation, or rendering rather than mixing responsibilities. Prefer clear
Portuguese domain terms already used in the files, but keep code identifiers
ASCII unless a file already requires accents.

## Testing Guidelines

There is no automated test suite yet. For changes, run at least one round-trip
manual check with `modelo_teste.xlsx`, `modelo_teste.md`, and generated `.lss` or
`.docx` output. When adding tests, place them under `tests/`, name files
`test_<module>.py`, and use `pytest` with fixture copies of sample inputs.

## Commit & Pull Request Guidelines

Git history is not available in this workspace, so use conventional, imperative
commit subjects such as `Add SurveyMD validation` or `Fix DOCX checkbox layout`.
Pull requests should include the affected converter, example command output or
manual validation steps, linked issue when applicable, and before/after files or
screenshots for DOCX formatting changes.

## Security & Configuration Tips

Treat survey files as untrusted input. Do not add network calls or execute
embedded content from Markdown, XLSX, DOCX, or LSS files. Keep dependencies
minimal and update `requirements.txt` whenever a new import is required.

## Browser Automation

Use `agent-browser` for web automation. Run `agent-browser --help` for all commands.

Core workflow:

1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes