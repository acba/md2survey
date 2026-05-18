from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import datetime as dt
import os
import re
import tempfile
import unicodedata
import urllib.error
import urllib.request
import zipfile
from urllib.parse import unquote
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import md2lss
from openpyxl import Workbook, load_workbook


@dataclass(frozen=True)
class AnaliseCandidata:
    auditado: str
    coluna_evidencia: str
    nome_original_evidencia: str
    upload: dict[str, Any]
    resposta_id: Any = None
    evidence_index: int | None = None
    erro: str = ""


@dataclass(frozen=True)
class ResolucaoEvidencia:
    caminho: Path | None
    nome_decodificado: str
    erro: str = ""


@dataclass(frozen=True)
class ItemAfirmado:
    codigo: str
    texto: str
    afirmacao: str


@dataclass(frozen=True)
class QuestaoContexto:
    codigo: str
    tipo: str
    texto: str
    itens: dict[str, str]


@dataclass(frozen=True)
class ContextoQuestionario:
    questoes: dict[str, QuestaoContexto]


@dataclass(frozen=True)
class ChecklistResolvido:
    nome: str
    caminho: Path | None
    conteudo: str
    hash_conteudo: str
    erro: str = ""


@dataclass(frozen=True)
class PromptResolvido:
    nome: str
    caminho: Path | None
    conteudo: str
    hash_conteudo: str
    erro: str = ""


@dataclass(frozen=True)
class PacoteEvidencia:
    caminho: Path
    tipo: str
    documentos: list[dict[str, Any]]
    inventario: list[str]
    erro: str = ""


def coluna_evidencia(nome: str) -> bool:
    return "evi" in nome and not nome.endswith("[filecount]")


def _parse_upload(valor: Any) -> tuple[dict[str, Any] | None, str]:
    if valor in (None, ""):
        return None, ""
    if isinstance(valor, str):
        try:
            parsed = json.loads(valor)
        except json.JSONDecodeError as exc:
            return None, f"metadados de upload invalidos: {exc.msg}"
    else:
        parsed = valor
    if not isinstance(parsed, list):
        return None, "metadados de upload devem ser uma lista"
    if len(parsed) != 1:
        return None, "coluna de evidencia deve conter exatamente um arquivo"
    upload = parsed[0]
    if not isinstance(upload, dict):
        return None, "metadado de upload deve ser um objeto"
    name = upload.get("name")
    if not isinstance(name, str) or not name:
        return None, "metadado de upload sem atributo name"
    return upload, ""


def _rows_from_xlsx(caminho_xlsx: Path) -> Iterable[dict[str, Any]]:
    workbook = load_workbook(caminho_xlsx, read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    headers = [str(value) if value is not None else "" for value in next(rows)]
    for values in rows:
        yield dict(zip(headers, values))


def inventariar_analises(
    caminho_xlsx: str | Path,
    raiz_evidencias: str | Path,
    caminho_questionario: str | Path,
    *,
    include_unsubmitted: bool = False,
) -> list[AnaliseCandidata]:
    del raiz_evidencias, caminho_questionario
    linhas = list(_rows_from_xlsx(Path(caminho_xlsx)))
    if not linhas:
        return []
    colunas = list(linhas[0].keys())
    colunas_evidencia = [col for col in colunas if coluna_evidencia(col)]
    analises: list[AnaliseCandidata] = []
    for linha in linhas:
        if not include_unsubmitted and not linha.get("submitdate"):
            continue
        auditado = str(linha.get("firstname") or "").strip()
        for evidence_index, coluna in enumerate(colunas_evidencia, start=1):
            upload, erro = _parse_upload(linha.get(coluna))
            if upload is None and not erro:
                continue
            analises.append(
                AnaliseCandidata(
                    auditado=auditado,
                    coluna_evidencia=coluna,
                    nome_original_evidencia=upload.get("name", "") if upload else "",
                    upload=upload or {},
                    resposta_id=linha.get("id"),
                    evidence_index=evidence_index,
                    erro=erro,
                )
            )
    return analises


def resolver_evidencia(
    auditado: str,
    raiz_evidencias: str | Path,
    upload: dict[str, Any],
    *,
    resposta_id: Any = None,
    evidence_index: int | None = None,
) -> ResolucaoEvidencia:
    nome_original = upload.get("name")
    if not isinstance(nome_original, str) or not nome_original:
        return ResolucaoEvidencia(caminho=None, nome_decodificado="", erro="metadado de upload sem atributo name")
    nome_decodificado = unquote(nome_original)
    auditado_dir = Path(raiz_evidencias) / auditado
    caminho = auditado_dir / nome_decodificado
    if not caminho.is_file():
        exportado = _resolver_evidencia_exportada_limesurvey(
            auditado_dir,
            nome_decodificado,
            resposta_id=resposta_id,
            evidence_index=evidence_index,
        )
        if exportado:
            return ResolucaoEvidencia(caminho=exportado, nome_decodificado=nome_decodificado)
        return ResolucaoEvidencia(
            caminho=None,
            nome_decodificado=nome_decodificado,
            erro=f"arquivo de evidencia nao encontrado: {caminho}",
        )
    return ResolucaoEvidencia(caminho=caminho, nome_decodificado=nome_decodificado)


def _resolver_evidencia_exportada_limesurvey(
    auditado_dir: Path,
    nome_decodificado: str,
    *,
    resposta_id: Any = None,
    evidence_index: int | None = None,
) -> Path | None:
    if not auditado_dir.is_dir():
        return None
    candidatos = [path for path in auditado_dir.iterdir() if path.is_file()]
    if not candidatos:
        return None

    if resposta_id is not None and evidence_index is not None:
        prefixo = _prefixo_exportacao_limesurvey(resposta_id, evidence_index)
        if prefixo:
            candidatos_prefixo = [path for path in candidatos if path.name.startswith(prefixo)]
            match = _melhor_match_nome_exportado(nome_decodificado, candidatos_prefixo)
            if match:
                return match

    return _melhor_match_nome_exportado(nome_decodificado, candidatos)


def _prefixo_exportacao_limesurvey(resposta_id: Any, evidence_index: int) -> str:
    try:
        return f"{int(resposta_id):05d}_{int(evidence_index):02d}_"
    except (TypeError, ValueError):
        return ""


def _melhor_match_nome_exportado(nome_decodificado: str, candidatos: list[Path]) -> Path | None:
    nome_key, suffix = _nome_exportado_key(nome_decodificado)
    matches: list[tuple[float, str, Path]] = []
    for candidato in candidatos:
        candidato_sem_prefixo = _remover_prefixo_exportacao_limesurvey(candidato.name)
        candidato_key, candidato_suffix = _nome_exportado_key(candidato_sem_prefixo)
        if candidato_suffix != suffix:
            continue
        if candidato_key == nome_key:
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, nome_key, candidato_key).ratio()
        if score >= 0.92:
            matches.append((score, candidato.name, candidato))
    if not matches:
        return None
    matches.sort(key=lambda item: (-item[0], item[1]))
    return matches[0][2]


def _remover_prefixo_exportacao_limesurvey(nome: str) -> str:
    return re.sub(r"^\d+_\d+_", "", nome)


def _nome_exportado_key(nome: str) -> tuple[str, str]:
    path = Path(nome)
    stem = unicodedata.normalize("NFKD", path.stem.casefold())
    stem = "".join(char for char in stem if not unicodedata.combining(char))
    stem = re.sub(r"[^a-z0-9]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-")
    return stem, path.suffix.casefold()


def carregar_contexto_questionario(caminho_questionario: str | Path) -> ContextoQuestionario:
    survey = md2lss.parse_markdown(Path(caminho_questionario))
    questoes: dict[str, QuestaoContexto] = {}
    for group in survey.groups:
        for question in group.questions:
            if question.type == "upload":
                continue
            itens = {option.code: option.text for option in question.subquestions}
            questoes[question.code] = QuestaoContexto(
                codigo=question.code,
                tipo=question.type,
                texto=question.text(),
                itens=itens,
            )
    return ContextoQuestionario(questoes=questoes)


def _base_coluna_evidencia(coluna_evidencia: str) -> tuple[str, str | None]:
    marker = coluna_evidencia.find("evi")
    base = coluna_evidencia[:marker]
    suffix = coluna_evidencia[marker + 3 :]
    return base, suffix or None


def selecionar_itens_afirmados(
    contexto: ContextoQuestionario,
    coluna_evidencia: str,
    resposta: dict[str, Any],
) -> list[ItemAfirmado]:
    base, item_especifico = _base_coluna_evidencia(coluna_evidencia)
    questao = contexto.questoes.get(base)
    if not questao:
        return []

    if item_especifico:
        valor = resposta.get(f"{base}[{item_especifico}]")
        if valor == "sim":
            return [
                ItemAfirmado(
                    codigo=f"{base}[{item_especifico}]",
                    texto=questao.itens.get(item_especifico, item_especifico),
                    afirmacao="sim",
                )
            ]
        return []

    valor_base = resposta.get(base)
    if questao.tipo in {"single", "adoption"} and valor_base in {"adpar", "admai"}:
        itens = [ItemAfirmado(codigo=base, texto=questao.texto, afirmacao=str(valor_base))]
        prefixo_ext = f"{base}ext["
        detalhe = contexto.questoes.get(f"{base}ext")
        for chave, valor in resposta.items():
            if chave.startswith(prefixo_ext) and chave.endswith("]") and valor == "Y":
                codigo_item = chave[len(prefixo_ext) : -1]
                itens.append(
                    ItemAfirmado(
                        codigo=chave,
                        texto=(detalhe.itens if detalhe else {}).get(codigo_item, codigo_item),
                        afirmacao="Y",
                    )
                )
        return itens

    itens = []
    for codigo_item, texto in questao.itens.items():
        chave = f"{base}[{codigo_item}]"
        if resposta.get(chave) == "sim":
            itens.append(ItemAfirmado(codigo=chave, texto=texto, afirmacao="sim"))
    return itens


def resolver_checklist(checklists_dir: str | Path, coluna_evidencia: str) -> ChecklistResolvido:
    base, item_especifico = _base_coluna_evidencia(coluna_evidencia)
    raiz = Path(checklists_dir)
    candidatos = []
    if item_especifico:
        candidatos.append(raiz / f"{base}_{item_especifico}.md")
    candidatos.append(raiz / f"{base}.md")
    for caminho in candidatos:
        if caminho.is_file():
            conteudo = caminho.read_text(encoding="utf-8")
            digest = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
            return ChecklistResolvido(
                nome=caminho.name,
                caminho=caminho,
                conteudo=conteudo,
                hash_conteudo=digest,
            )
    return ChecklistResolvido(
        nome="",
        caminho=None,
        conteudo="",
        hash_conteudo="",
        erro=f"checklist de analise nao encontrado para {coluna_evidencia}",
    )


def resolver_prompt(prompts_dir: str | Path, coluna_evidencia: str) -> PromptResolvido:
    base, item_especifico = _base_coluna_evidencia(coluna_evidencia)
    raiz = Path(prompts_dir)
    candidatos = []
    if item_especifico:
        candidatos.append(raiz / f"{base}_{item_especifico}.md")
    candidatos.append(raiz / f"{base}.md")
    for caminho in candidatos:
        if caminho.is_file():
            conteudo = caminho.read_text(encoding="utf-8")
            digest = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
            return PromptResolvido(
                nome=caminho.name,
                caminho=caminho,
                conteudo=conteudo,
                hash_conteudo=digest,
            )
    return PromptResolvido(
        nome="",
        caminho=None,
        conteudo="",
        hash_conteudo="",
        erro=f"prompt de analise nao encontrado para {coluna_evidencia}",
    )


def hash_arquivo(caminho: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(caminho).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zip_member_safe(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts


def normalizar_evidencia(caminho: str | Path) -> PacoteEvidencia:
    path = Path(caminho)
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        try:
            texto = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            texto = path.read_text(encoding="latin-1")
        return PacoteEvidencia(
            caminho=path,
            tipo=suffix.lstrip("."),
            documentos=[{"nome": path.name, "texto": texto}],
            inventario=[path.name],
        )
    if suffix == ".zip":
        documentos: list[dict[str, Any]] = []
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                for name in names:
                    if not _zip_member_safe(name):
                        return PacoteEvidencia(
                            caminho=path,
                            tipo="zip",
                            documentos=[],
                            inventario=names,
                            erro=f"zip contem path traversal: {name}",
                        )
                for name in names:
                    if name.endswith("/"):
                        continue
                    if Path(name).suffix.lower() in {".txt", ".md", ".csv"}:
                        data = archive.read(name)
                        try:
                            texto = data.decode("utf-8")
                        except UnicodeDecodeError:
                            texto = data.decode("latin-1")
                        documentos.append({"nome": name, "texto": texto})
                    else:
                        documentos.append({"nome": name, "nao_suportado": True})
                return PacoteEvidencia(caminho=path, tipo="zip", documentos=documentos, inventario=names)
        except zipfile.BadZipFile:
            return PacoteEvidencia(caminho=path, tipo="zip", documentos=[], inventario=[], erro="zip invalido")
    if suffix == ".xlsx":
        workbook = load_workbook(path, read_only=True, data_only=True)
        documentos = []
        for sheet in workbook.worksheets:
            linhas = []
            for row in sheet.iter_rows(values_only=True):
                valores = ["" if value is None else str(value) for value in row]
                if any(valores):
                    linhas.append("\t".join(valores))
            documentos.append({"nome": sheet.title, "texto": "\n".join(linhas)})
        return PacoteEvidencia(
            caminho=path,
            tipo="xlsx",
            documentos=documentos,
            inventario=[sheet.title for sheet in workbook.worksheets],
        )
    if suffix == ".docx":
        try:
            from docx import Document
        except ModuleNotFoundError:
            return PacoteEvidencia(
                caminho=path,
                tipo="docx",
                documentos=[],
                inventario=[path.name],
                erro="python-docx nao instalado para normalizar DOCX",
            )
        document = Document(path)
        partes = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        for table in document.tables:
            for row in table.rows:
                partes.append("\t".join(cell.text for cell in row.cells))
        return PacoteEvidencia(
            caminho=path,
            tipo="docx",
            documentos=[{"nome": path.name, "texto": "\n".join(partes)}],
            inventario=[path.name],
        )
    return PacoteEvidencia(
        caminho=path,
        tipo=suffix.lstrip(".") or "desconhecido",
        documentos=[],
        inventario=[path.name],
        erro=f"tipo de evidencia nao suportado: {suffix or path.name}",
    )


EXTENSOES_UPLOAD_COMPATIVEIS = {".pdf", ".txt", ".md", ".csv", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"}


def arquivos_compativeis_upload(caminho: str | Path, destino_zip: str | Path | None = None) -> list[str]:
    path = Path(caminho)
    if path.suffix.lower() in EXTENSOES_UPLOAD_COMPATIVEIS and path.is_file():
        return [str(path)]
    if path.suffix.lower() == ".zip" and destino_zip is not None:
        destino = Path(destino_zip)
        arquivos = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith("/") or not _zip_member_safe(name):
                    continue
                member = Path(name)
                if member.suffix.lower() not in EXTENSOES_UPLOAD_COMPATIVEIS:
                    continue
                target = destino / member
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
                arquivos.append(str(target))
        return arquivos
    return []


def calcular_identidade_analise(
    *,
    auditado: str,
    coluna_evidencia: str,
    nome_original_evidencia: str,
    hash_conteudo: str,
    provider: str,
    model: str,
    prompt_hash: str = "",
    checklist_hash: str = "",
    prompt_version: str,
) -> str:
    artifact_hash = prompt_hash or checklist_hash
    payload = {
        "auditado": auditado,
        "coluna_evidencia": coluna_evidencia,
        "nome_original_evidencia": nome_original_evidencia,
        "hash_conteudo": hash_conteudo,
        "provider": provider,
        "model": model,
        "prompt_hash": artifact_hash,
        "prompt_version": prompt_version,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def gravar_registro_analise(checkpoint: str | Path, registro: dict[str, Any]) -> None:
    path = Path(checkpoint)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(registro, ensure_ascii=False, sort_keys=True, default=str))
        file.write("\n")


def carregar_registros_analise(checkpoint: str | Path) -> dict[str, dict[str, Any]]:
    path = Path(checkpoint)
    if not path.is_file():
        return {}
    registros: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        registro = json.loads(line)
        identity = registro.get("identity")
        if isinstance(identity, str):
            registros[identity] = registro
    return registros


def deve_processar_identidade(
    registros: dict[str, dict[str, Any]],
    identity: str,
    *,
    skip_errors: bool = False,
) -> bool:
    registro = registros.get(identity)
    if not registro:
        return True
    status = registro.get("status")
    if status == "completed":
        return False
    if status == "error" and skip_errors:
        return False
    return True


def executar_julgamento_fake(
    *,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    checklist: str,
    pacote: dict[str, Any],
) -> dict[str, Any]:
    del auditado, questao_base, checklist
    documentos = pacote.get("documentos", []) if isinstance(pacote, dict) else []
    referencias = [
        documento.get("nome")
        for documento in documentos
        if isinstance(documento, dict) and documento.get("nome")
    ]
    conclusoes = []
    for item in itens_afirmados:
        conclusoes.append(
            {
                "item_codigo": item.codigo,
                "item_texto": item.texto,
                "afirmacao_auditado": item.afirmacao,
                "estado": "inconclusivo",
                "justificativa": "Provider fake nao emite conclusao substantiva.",
                "lacunas": ["Analise real de IA nao executada."],
                "arquivos_referenciados": referencias,
                "trechos_ou_elementos": [],
                "paginas_ou_localizacao": [],
                "coluna_evidencia": coluna_evidencia,
            }
        )
    return {"status": "completed", "conclusoes": conclusoes}


ESTADOS_CONFORMIDADE = {"conforme", "nao_conforme", "inconclusivo", "erro"}
CONCLUSAO_CAMPOS_OBRIGATORIOS = {
    "item_codigo",
    "item_texto",
    "afirmacao_auditado",
    "estado",
    "justificativa",
    "lacunas",
    "arquivos_referenciados",
    "trechos_ou_elementos",
    "paginas_ou_localizacao",
}


def validar_resultado_ia(resultado: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(resultado, dict):
        raise ValueError("resultado de IA deve ser objeto JSON")
    status = resultado.get("status", "completed")
    if status not in {"completed", "error"}:
        raise ValueError(f"status invalido: {status}")
    if status == "error":
        if not resultado.get("error"):
            raise ValueError("resultado error precisa de campo error")
        return resultado
    conclusoes = resultado.get("conclusoes")
    if not isinstance(conclusoes, list):
        raise ValueError("resultado completed precisa de lista conclusoes")
    for idx, conclusao in enumerate(conclusoes):
        if not isinstance(conclusao, dict):
            raise ValueError(f"conclusao {idx} deve ser objeto")
        faltantes = CONCLUSAO_CAMPOS_OBRIGATORIOS.difference(conclusao)
        if faltantes:
            raise ValueError(f"conclusao {idx} sem campos: {', '.join(sorted(faltantes))}")
        if conclusao["estado"] not in ESTADOS_CONFORMIDADE:
            raise ValueError(f"estado invalido: {conclusao['estado']}")
        for campo in ["lacunas", "arquivos_referenciados", "trechos_ou_elementos", "paginas_ou_localizacao"]:
            if not isinstance(conclusao[campo], list):
                raise ValueError(f"campo {campo} deve ser lista")
    resultado["status"] = status
    return resultado


def executar_provider(
    *,
    provider: str,
    model: str,
    api_key: str,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    pacote: dict[str, Any],
) -> dict[str, Any]:
    if provider == "fake":
        return validar_resultado_ia(
            executar_julgamento_fake(
                auditado=auditado,
                questao_base=questao_base,
                coluna_evidencia=coluna_evidencia,
                itens_afirmados=itens_afirmados,
                checklist=prompt,
                pacote=pacote,
            )
        )
    if provider == "openrouter" and not api_key:
        return {"status": "error", "error": "OPENROUTER_API_KEY nao configurada para provider openrouter"}
    if provider == "gemini" and not api_key:
        return {"status": "error", "error": "GEMINI_API_KEY nao configurada para provider gemini"}
    if provider == "openrouter":
        return executar_julgamento_openrouter(
            api_key=api_key,
            model=model,
            prompt=prompt,
            auditado=auditado,
            questao_base=questao_base,
            coluna_evidencia=coluna_evidencia,
            itens_afirmados=itens_afirmados,
            pacote=pacote,
        )
    if provider == "gemini":
        return executar_julgamento_gemini_genai(
            api_key=api_key,
            model=model,
            prompt=prompt,
            auditado=auditado,
            questao_base=questao_base,
            coluna_evidencia=coluna_evidencia,
            itens_afirmados=itens_afirmados,
            pacote=pacote,
        )
    return {"status": "error", "error": f"provider nao suportado: {provider}/{model}"}


def _conteudo_provider_textual(
    *,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    pacote: dict[str, Any],
) -> str:
    payload = {
        "prompt_de_analise": prompt,
        "auditado": auditado,
        "questao_base": questao_base,
        "coluna_evidencia": coluna_evidencia,
        "itens_afirmados": [item.__dict__ for item in itens_afirmados],
        "pacote_evidencia": pacote,
        "saida_obrigatoria": {
            "status": "completed",
            "conclusoes": [
                {
                    "item_codigo": "...",
                    "item_texto": "...",
                    "afirmacao_auditado": "...",
                    "estado": "conforme|nao_conforme|inconclusivo|erro",
                    "justificativa": "...",
                    "lacunas": [],
                    "arquivos_referenciados": [],
                    "trechos_ou_elementos": [],
                    "paginas_ou_localizacao": [],
                }
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _json_schema_response_format() -> dict[str, Any]:
    properties = {
        "item_codigo": {"type": "string"},
        "item_texto": {"type": "string"},
        "afirmacao_auditado": {"type": "string"},
        "estado": {"type": "string", "enum": sorted(ESTADOS_CONFORMIDADE)},
        "justificativa": {"type": "string"},
        "lacunas": {"type": "array", "items": {"type": "string"}},
        "arquivos_referenciados": {"type": "array", "items": {"type": "string"}},
        "trechos_ou_elementos": {"type": "array", "items": {"type": "string"}},
        "paginas_ou_localizacao": {"type": "array", "items": {"type": "string"}},
    }
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "resultado_avaliacao_evidencia",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "status": {"type": "string", "enum": ["completed", "error"]},
                    "conclusoes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": properties,
                            "required": sorted(CONCLUSAO_CAMPOS_OBRIGATORIOS),
                        },
                    },
                    "error": {"type": "string"},
                },
                "required": ["status"],
            },
        },
    }


def executar_julgamento_openrouter(
    *,
    api_key: str,
    model: str,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    pacote: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": _conteudo_provider_textual(
                    prompt=prompt,
                    auditado=auditado,
                    questao_base=questao_base,
                    coluna_evidencia=coluna_evidencia,
                    itens_afirmados=itens_afirmados,
                    pacote=pacote,
                ),
            }
        ],
        "response_format": _json_schema_response_format(),
    }
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        return validar_resultado_ia(json.loads(content))
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "error", "error": f"erro ao chamar OpenRouter: {exc}"}


def executar_julgamento_gemini_genai(
    *,
    api_key: str,
    model: str,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    pacote: dict[str, Any],
) -> dict[str, Any]:
    try:
        from google import genai
    except Exception as exc:
        return {"status": "error", "error": f"google-genai nao disponivel: {exc}"}
    client = genai.Client(api_key=api_key)
    uploaded = []
    for arquivo in pacote.get("arquivos_upload", []):
        try:
            uploaded.append(client.files.upload(file=arquivo))
        except Exception as exc:
            return {"status": "error", "error": f"erro ao fazer upload Gemini de {arquivo}: {exc}"}
    contents = [
        _conteudo_provider_textual(
            prompt=prompt,
            auditado=auditado,
            questao_base=questao_base,
            coluna_evidencia=coluna_evidencia,
            itens_afirmados=itens_afirmados,
            pacote={k: v for k, v in pacote.items() if k != "arquivos_upload"},
        )
    ]
    contents.extend(uploaded)
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config={"response_mime_type": "application/json"},
        )
        return validar_resultado_ia(json.loads(response.text))
    except (TypeError, json.JSONDecodeError, ValueError, Exception) as exc:
        return {"status": "error", "error": f"erro ao chamar Gemini: {exc}"}


def executar_julgamento_gemini(
    *,
    api_key: str,
    model: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[ItemAfirmado],
    checklist: str,
    pacote: dict[str, Any],
) -> dict[str, Any]:
    prompt = {
        "auditado": auditado,
        "questao_base": questao_base,
        "coluna_evidencia": coluna_evidencia,
        "itens_afirmados": [item.__dict__ for item in itens_afirmados],
        "checklist": checklist,
        "pacote_evidencia": pacote,
        "instrucoes": [
            "Avalie somente os criterios do checklist.",
            "Nao use conhecimento externo para suprir lacunas.",
            "Retorne somente JSON com status e conclusoes.",
            "Use estados: conforme, nao_conforme, inconclusivo, erro.",
        ],
    }
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": json.dumps(prompt, ensure_ascii=False),
                    }
                ]
            }
        ],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "error", "error": f"erro ao chamar Gemini: {exc}"}
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        return {"status": "error", "error": f"resposta Gemini invalida: {exc}", "raw": payload}
    if result.get("status") not in {"completed", "error"}:
        result["status"] = "completed"
    return result


def _join_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def gerar_relatorio_conformidade(checkpoint: str | Path, destino: str | Path) -> None:
    registros = carregar_registros_analise(checkpoint)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Conformidade"
    headers = [
        "auditado",
        "questao",
        "item",
        "afirmacao_auditado",
        "estado",
        "justificativa",
        "lacunas",
        "referencias",
        "evidencia",
        "provider",
        "model",
        "data_analise",
        "status_revisao_humana",
    ]
    sheet.append(headers)
    for registro in registros.values():
        result = registro.get("result") if isinstance(registro.get("result"), dict) else {}
        conclusoes = result.get("conclusoes") if isinstance(result, dict) else None
        if not conclusoes and registro.get("status") == "error":
            conclusoes = [
                {
                    "item_codigo": "",
                    "afirmacao_auditado": "",
                    "estado": "erro",
                    "justificativa": registro.get("error", "Erro de analise"),
                    "lacunas": [],
                    "arquivos_referenciados": [],
                }
            ]
        for conclusao in conclusoes or []:
            sheet.append(
                [
                    registro.get("auditado", ""),
                    registro.get("questao", ""),
                    conclusao.get("item_codigo", ""),
                    conclusao.get("afirmacao_auditado", ""),
                    conclusao.get("estado", ""),
                    conclusao.get("justificativa", ""),
                    _join_value(conclusao.get("lacunas")),
                    _join_value(conclusao.get("arquivos_referenciados")),
                    registro.get("evidencia", ""),
                    registro.get("provider", ""),
                    registro.get("model", ""),
                    registro.get("finished_at", ""),
                    None,
                ]
            )
    destino_path = Path(destino)
    destino_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(destino_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-analisa evidencias enviadas por auditados.")
    parser.add_argument("respostas")
    parser.add_argument("evidencias")
    parser.add_argument("--questionario", required=True)
    parser.add_argument("--provider", default="fake")
    parser.add_argument("--model", default="fake")
    parser.add_argument("--prompts-dir", default=None, help="Diretorio com Prompts de analise por questao.")
    parser.add_argument("--checklists-dir", default=None, help="Alias legado para --prompts-dir.")
    parser.add_argument("--out-dir", default=".saida_analise")
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--skip-errors", action="store_true")
    parser.add_argument(
        "--include-unsubmitted",
        action="store_true",
        help="Inclui respostas sem submitdate. Por padrao, somente respostas submetidas sao analisadas.",
    )
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args(argv)
    prompts_dir = args.prompts_dir or args.checklists_dir or "checklists"
    analises = inventariar_analises(
        args.respostas,
        args.evidencias,
        args.questionario,
        include_unsubmitted=args.include_unsubmitted,
    )
    if args.list_only:
        for analise in analises:
            print(json.dumps(analise.__dict__, ensure_ascii=False, default=str))
        return 0
    contexto = carregar_contexto_questionario(args.questionario)
    out_dir = Path(args.out_dir)
    checkpoint = out_dir / "analyses.jsonl"
    registros = carregar_registros_analise(checkpoint)
    for analise in analises:
        questao_base, _ = _base_coluna_evidencia(analise.coluna_evidencia)
        if analise.erro:
            identity = hashlib.sha256(
                json.dumps(analise.__dict__, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()
            if deve_processar_identidade(registros, identity, skip_errors=args.skip_errors):
                gravar_registro_analise(
                    checkpoint,
                    {
                        "identity": identity,
                        "status": "error",
                        "auditado": analise.auditado,
                        "questao": questao_base,
                        "coluna_evidencia": analise.coluna_evidencia,
                        "evidencia": analise.nome_original_evidencia,
                        "provider": args.provider,
                        "model": args.model,
                        "error": analise.erro,
                        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    },
                )
            continue
        resolucao = resolver_evidencia(
            analise.auditado,
            args.evidencias,
            analise.upload,
            resposta_id=analise.resposta_id,
            evidence_index=analise.evidence_index,
        )
        prompt = resolver_prompt(prompts_dir, analise.coluna_evidencia)
        if resolucao.erro:
            hash_conteudo = ""
        else:
            hash_conteudo = hash_arquivo(resolucao.caminho)
        identity = calcular_identidade_analise(
            auditado=analise.auditado,
            coluna_evidencia=analise.coluna_evidencia,
            nome_original_evidencia=analise.nome_original_evidencia,
            hash_conteudo=hash_conteudo,
            provider=args.provider,
            model=args.model,
            prompt_hash=prompt.hash_conteudo,
            prompt_version=args.prompt_version,
        )
        if not deve_processar_identidade(registros, identity, skip_errors=args.skip_errors):
            continue
        erro = resolucao.erro or prompt.erro
        if erro:
            gravar_registro_analise(
                checkpoint,
                {
                    "identity": identity,
                    "status": "error",
                    "auditado": analise.auditado,
                    "questao": questao_base,
                    "coluna_evidencia": analise.coluna_evidencia,
                    "evidencia": analise.nome_original_evidencia,
                    "provider": args.provider,
                    "model": args.model,
                    "error": erro,
                    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                },
            )
            continue
        itens = selecionar_itens_afirmados(contexto, analise.coluna_evidencia, _linha_por_id(args.respostas, analise.resposta_id))
        pacote = normalizar_evidencia(resolucao.caminho)
        env_key = {"gemini": "GEMINI_API_KEY", "openrouter": "OPENROUTER_API_KEY"}.get(args.provider, "")
        api_key = os.environ.get(env_key, "") if env_key else ""
        with tempfile.TemporaryDirectory() as upload_tmp:
            result = executar_provider(
                provider=args.provider,
                model=args.model,
                api_key=api_key,
                prompt=prompt.conteudo,
                auditado=analise.auditado,
                questao_base=questao_base,
                coluna_evidencia=analise.coluna_evidencia,
                itens_afirmados=itens,
                pacote={
                    "documentos": pacote.documentos,
                    "inventario": pacote.inventario,
                    "erro": pacote.erro,
                    "arquivos_upload": arquivos_compativeis_upload(resolucao.caminho, upload_tmp),
                },
            )
        gravar_registro_analise(
            checkpoint,
            {
                "identity": identity,
                "status": result["status"],
                "auditado": analise.auditado,
                "questao": questao_base,
                "coluna_evidencia": analise.coluna_evidencia,
                "evidencia": analise.nome_original_evidencia,
                "provider": args.provider,
                "model": args.model,
                "result": result,
                "error": result.get("error", ""),
                "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        )
        registros[identity] = {"identity": identity, "status": result["status"]}
    gerar_relatorio_conformidade(checkpoint, out_dir / "relatorio_conformidade.xlsx")
    return 0


def _linha_por_id(caminho_xlsx: str | Path, resposta_id: Any) -> dict[str, Any]:
    for linha in _rows_from_xlsx(Path(caminho_xlsx)):
        if linha.get("id") == resposta_id:
            return linha
    return {}
