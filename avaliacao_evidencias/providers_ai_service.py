from __future__ import annotations

import dataclasses
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Mapping


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
RETRYABLE_PROVIDER_STATUSES = {429, 500, 502, 503, 504}
DEFAULT_TRANSIENT_RETRY_DELAYS = (30.0, 60.0, 120.0)


def parse_retry_after(value: str | None, *, now: Callable[[], float] = time.time) -> float | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=dt.timezone.utc)
    return max(0.0, retry_at.timestamp() - now())


def _item_para_dict(item: Any) -> dict[str, Any]:
    if dataclasses.is_dataclass(item):
        return dataclasses.asdict(item)
    if isinstance(item, Mapping):
        return dict(item)
    if hasattr(item, "__dict__"):
        return dict(item.__dict__)
    raise TypeError(f"item afirmado nao serializavel: {type(item).__name__}")


def _valor_item(item: Any, campo: str) -> Any:
    if isinstance(item, Mapping):
        return item.get(campo)
    return getattr(item, campo)


def executar_julgamento_fake(
    *,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[Any],
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
                "item_codigo": _valor_item(item, "codigo"),
                "item_texto": _valor_item(item, "texto"),
                "afirmacao_auditado": _valor_item(item, "afirmacao"),
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


def _extrair_bloco_json(texto: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", texto, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return texto.strip()


def carregar_json_modelo(texto: str) -> dict[str, Any]:
    try:
        from json_repair import repair_json
    except ModuleNotFoundError as exc:
        raise ValueError("json-repair nao instalado para reparar respostas JSON") from exc

    bruto = _extrair_bloco_json(texto)
    reparado = repair_json(bruto)
    if not isinstance(reparado, str) or not reparado.strip():
        raise ValueError("resposta do modelo nao contem JSON reparavel")
    try:
        resultado = json.loads(reparado)
    except json.JSONDecodeError as exc:
        raise ValueError(f"resposta do modelo nao contem JSON reparavel: {exc.msg}") from exc
    if not isinstance(resultado, dict):
        raise ValueError("resposta do modelo precisa ser objeto JSON")
    return resultado


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
    itens_afirmados: list[Any],
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
    itens_afirmados: list[Any],
    pacote: dict[str, Any],
) -> str:
    payload = {
        "prompt_de_analise": prompt,
        "auditado": auditado,
        "questao_base": questao_base,
        "coluna_evidencia": coluna_evidencia,
        "itens_afirmados": [_item_para_dict(item) for item in itens_afirmados],
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


def _header_retry_after(headers: Any) -> str | None:
    if not headers:
        return None
    getter = getattr(headers, "get", None)
    if callable(getter):
        return getter("Retry-After") or getter("retry-after")
    if isinstance(headers, dict):
        return headers.get("Retry-After") or headers.get("retry-after")
    return None


def _status_from_exception(exc: BaseException) -> Any:
    status = getattr(exc, "code", None) or getattr(exc, "status", None) or getattr(exc, "status_code", None)
    response = getattr(exc, "response", None)
    if status is None and response is not None:
        status = getattr(response, "status_code", None) or getattr(response, "status", None)
    return status


def _retry_after_from_exception(exc: BaseException) -> float | None:
    response = getattr(exc, "response", None)
    retry_after = _header_retry_after(getattr(exc, "headers", None))
    if retry_after is None and response is not None:
        retry_after = _header_retry_after(getattr(response, "headers", None))
    return parse_retry_after(retry_after)


def _is_retryable_provider_error(exc: BaseException) -> bool:
    return _status_from_exception(exc) in RETRYABLE_PROVIDER_STATUSES


def executar_com_retry_transiente(
    func: Callable[[], Any],
    *,
    max_retries: int = 3,
    fallback_delays: tuple[float, ...] = DEFAULT_TRANSIENT_RETRY_DELAYS,
    sleeper: Callable[[float], None] | None = None,
) -> Any:
    sleep = sleeper or time.sleep
    tentativa = 0
    while True:
        try:
            return func()
        except Exception as exc:
            if not _is_retryable_provider_error(exc) or tentativa >= max_retries:
                raise
            retry_after = _retry_after_from_exception(exc)
            delay = retry_after if retry_after is not None else fallback_delays[min(tentativa, len(fallback_delays) - 1)]
            sleep(delay)
            tentativa += 1


def executar_julgamento_openrouter(
    *,
    api_key: str,
    model: str,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[Any],
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
    content = ""
    try:
        def call_openrouter() -> dict[str, Any]:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))

        payload = executar_com_retry_transiente(call_openrouter)
        content = payload["choices"][0]["message"]["content"]
        return validar_resultado_ia(carregar_json_modelo(content))
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
        result = {"status": "error", "error": f"erro ao chamar OpenRouter: {exc}"}
        if content:
            result["raw_response_excerpt"] = content[:2000]
        return result


def executar_julgamento_gemini_genai(
    *,
    api_key: str,
    model: str,
    prompt: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[Any],
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
            uploaded.append(executar_com_retry_transiente(lambda arquivo=arquivo: client.files.upload(file=arquivo)))
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
    raw_text = ""
    try:
        response = executar_com_retry_transiente(
            lambda: client.models.generate_content(
                model=model,
                contents=contents,
                config={"response_mime_type": "application/json"},
            )
        )
        raw_text = response.text
        return validar_resultado_ia(carregar_json_modelo(raw_text))
    except Exception as exc:
        result = {"status": "error", "error": f"erro ao chamar Gemini: {exc}"}
        if raw_text:
            result["raw_response_excerpt"] = raw_text[:2000]
        return result


def executar_julgamento_gemini(
    *,
    api_key: str,
    model: str,
    auditado: str,
    questao_base: str,
    coluna_evidencia: str,
    itens_afirmados: list[Any],
    checklist: str,
    pacote: dict[str, Any],
) -> dict[str, Any]:
    prompt = {
        "auditado": auditado,
        "questao_base": questao_base,
        "coluna_evidencia": coluna_evidencia,
        "itens_afirmados": [_item_para_dict(item) for item in itens_afirmados],
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
        def call_gemini() -> dict[str, Any]:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))

        payload = executar_com_retry_transiente(call_gemini)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "error", "error": f"erro ao chamar Gemini: {exc}"}
    text = ""
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        result = carregar_json_modelo(text)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        response = {"status": "error", "error": f"resposta Gemini invalida: {exc}", "raw": payload}
        if text:
            response["raw_response_excerpt"] = text[:2000]
        return response
    if result.get("status") not in {"completed", "error"}:
        result["status"] = "completed"
    return result
