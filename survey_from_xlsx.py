#!/usr/bin/env python3
"""Gera SurveyMD, DOCX e LSS a partir de uma planilha SurveyXLSX."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import md2docx
import md2lss
import xlsx2md


REQUIRED_HEADERS: Dict[str, List[str]] = {
    "survey": ["key", "value"],
    "groups": ["group_code", "group_name"],
    "questions": ["group_code", "code", "type", "text"],
}

OPTIONAL_HEADERS: Dict[str, List[str]] = {
    "subgroups": ["group_code", "subgroup_code", "subgroup_title"],
}


def validate_xlsx(input_path: Path) -> None:
    if input_path.suffix.lower() != ".xlsx":
        raise ValueError("O arquivo de entrada deve ter extensao .xlsx.")

    try:
        wb = xlsx2md.load_workbook(input_path, data_only=False)
    except Exception as exc:
        raise ValueError(f"Nao foi possivel abrir a planilha: {exc}") from exc

    missing_sheets = [sheet for sheet in REQUIRED_HEADERS if sheet not in wb.sheetnames]
    if missing_sheets:
        raise ValueError(f"Abas obrigatorias ausentes: {', '.join(missing_sheets)}.")

    for sheet, headers in REQUIRED_HEADERS.items():
        rows = xlsx2md.sheet_rows(wb, sheet)
        if not rows:
            raise ValueError(f"A aba '{sheet}' nao contem dados validos.")
        present = set(rows[0].keys())
        missing = [header for header in headers if header not in present]
        if missing:
            raise ValueError(f"A aba '{sheet}' nao contem as colunas: {', '.join(missing)}.")

    for sheet, headers in OPTIONAL_HEADERS.items():
        if sheet not in wb.sheetnames:
            continue
        rows = xlsx2md.sheet_rows(wb, sheet)
        if not rows:
            continue
        present = set(rows[0].keys())
        missing = [header for header in headers if header not in present]
        if missing:
            raise ValueError(f"A aba '{sheet}' nao contem as colunas: {', '.join(missing)}.")

    meta = xlsx2md.survey_meta(wb)
    orgs = xlsx2md.discover_organizations_from_rows(
        xlsx2md.sheet_rows(wb, "questions"),
        xlsx2md.sheet_rows(wb, "subquestions"),
        xlsx2md.sheet_rows(wb, "options"),
    )
    if orgs:
        missing_sids = [org for org in orgs if not sid_for_org(meta, org)]
        if missing_sids:
            keys = ", ".join(f"sid_{org}" for org in missing_sids)
            raise ValueError(f"A aba 'survey' deve informar SID por organizacao: {keys}.")
    elif not meta.get("sid"):
        raise ValueError("A aba 'survey' deve informar a chave 'sid'.")

    subgroups = xlsx2md.sheet_rows(wb, "subgroups")
    subgroup_keys = {(row.get("group_code", ""), row.get("subgroup_code", "")) for row in subgroups}
    for row in xlsx2md.sheet_rows(wb, "questions"):
        subgroup_code = row.get("subgroup_code", "")
        if subgroup_code and (row.get("group_code", ""), subgroup_code) not in subgroup_keys:
            raise ValueError(f"Questao {row.get('code', '')} referencia subgrupo inexistente: {subgroup_code}.")


def sid_for_org(meta: Dict[str, str], org: str) -> Optional[str]:
    wanted = f"sid_{org}".casefold()
    for key, value in meta.items():
        if key.casefold() == wanted and value:
            return value
    return None


def output_paths(input_path: Path, out_dir: Path | None, org: Optional[str] = None) -> Dict[str, Path]:
    target_dir = out_dir or input_path.parent
    base = f"{input_path.stem}_{org}" if org else input_path.stem
    return {
        "md": target_dir / f"{base}.md",
        "docx": target_dir / f"{base}.docx",
        "lss": target_dir / f"{base}.lss",
    }


def assert_can_write(paths: Iterable[Path], force: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Arquivos de saida ja existem: {names}. Use --force para sobrescrever.")


def build_all(
    input_xlsx: Path,
    template_docx: Path,
    out_dir: Path | None,
    force: bool,
    sid: int | None,
    first_gid: int,
    first_qid: int,
) -> Dict[str, Dict[str, Path]]:
    input_xlsx = input_xlsx.resolve()
    template_docx = template_docx.resolve()
    if not input_xlsx.exists():
        raise FileNotFoundError(f"Planilha nao encontrada: {input_xlsx}")
    if not template_docx.exists():
        raise FileNotFoundError(f"DOCX de referencia nao encontrado: {template_docx}")

    validate_xlsx(input_xlsx)
    target_dir = out_dir.resolve() if out_dir else None
    orgs = xlsx2md.discover_organizations(input_xlsx)
    variants: List[Optional[str]] = orgs or [None]
    paths_by_variant = {org or "default": output_paths(input_xlsx, target_dir, org) for org in variants}
    all_paths = [path for paths in paths_by_variant.values() for path in paths.values()]
    for paths in paths_by_variant.values():
        paths["md"].parent.mkdir(parents=True, exist_ok=True)
    assert_can_write(all_paths, force)

    for org in variants:
        variant_name = org or "default"
        paths = paths_by_variant[variant_name]
        md_text = xlsx2md.convert_xlsx_to_md(input_xlsx, org=org)

        with tempfile.TemporaryDirectory(prefix="survey_from_xlsx_") as temp_root:
            temp_dir = Path(temp_root)
            temp_md = temp_dir / paths["md"].name
            temp_docx = temp_dir / paths["docx"].name
            temp_md.write_text(md_text, encoding="utf-8")

            lss_survey = md2lss.parse_markdown(temp_md)
            resolved_sid = sid or int(lss_survey.meta.get("sid", "900001"))
            lss_text = md2lss.build_lss(lss_survey, sid=resolved_sid, first_gid=first_gid, first_qid=first_qid)

            docx_survey = md2docx.parse_markdown(temp_md)
            md2docx.build_docx(docx_survey, temp_docx, template_docx=template_docx)

            paths["md"].write_text(md_text, encoding="utf-8")
            paths["lss"].write_text(lss_text, encoding="utf-8")
            shutil.copyfile(temp_docx, paths["docx"])

    return paths_by_variant


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera .md, .docx e .lss a partir de uma planilha SurveyXLSX.")
    parser.add_argument("input_xlsx", type=Path, help="Planilha .xlsx de entrada")
    parser.add_argument("--template-docx", type=Path, required=True, help="DOCX de referencia usado como base visual")
    parser.add_argument("--out-dir", type=Path, default=None, help="Diretorio de saida; padrao: diretorio da planilha")
    parser.add_argument("--force", action="store_true", help="Sobrescreve arquivos de saida existentes")
    parser.add_argument("--sid", type=int, default=None, help="Survey ID; padrao: valor sid da planilha")
    parser.add_argument("--first-gid", type=int, default=1000, help="Primeiro GID gerado no LSS")
    parser.add_argument("--first-qid", type=int, default=10000, help="Primeiro QID gerado no LSS")
    args = parser.parse_args(argv)

    try:
        paths_by_variant = build_all(
            args.input_xlsx,
            args.template_docx,
            args.out_dir,
            args.force,
            args.sid,
            args.first_gid,
            args.first_qid,
        )
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    print("Arquivos gerados:")
    for variant, paths in paths_by_variant.items():
        label = "" if variant == "default" else f" [{variant}]"
        print(f"  MD{label}:   {paths['md']}")
        print(f"  DOCX{label}: {paths['docx']}")
        print(f"  LSS{label}:  {paths['lss']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
