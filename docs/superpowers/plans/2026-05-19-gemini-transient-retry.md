# Gemini Transient Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Gemini transient overload errors, especially HTTP/API 503 `UNAVAILABLE`, wait and retry before recording an error and moving to the next evidence/consolidation item.

**Architecture:** Extend the provider retry layer in `avaliacao_evidencias/pipeline.py` so retry policy is shared by evidence analysis and consolidation, because both call `executar_provider()`. Keep checkpoint semantics unchanged: a provider result is written only after all retry attempts for that item are exhausted, and the main loop then continues to the next item.

**Tech Stack:** Python `unittest`, `google-genai`, existing `RequestsPerMinuteLimiter`, existing JSONL checkpoint flow.

---

## Current Finding

The file `.saida_analise/consolidado_gemini_3_1_flash_lite/consolidated.jsonl` has 11 records:

- 10 records with `status = completed`.
- 1 record with `status = error`.
- The failed record is `FUNARJ / q0103 / q0103evi / competencias%20atribuicoes.zip`.
- Error text: Gemini returned `503 UNAVAILABLE` with message that the model was experiencing high demand.
- The consolidation run was expected to process 21 groups, so the file is partial.

The current retry helper in `avaliacao_evidencias/pipeline.py` handles only HTTP 429. Gemini 503 from `google-genai` is caught in `executar_julgamento_gemini_genai()` and immediately converted into a JSON error result, so no retry is attempted.

## Files

- Modify: `avaliacao_evidencias/pipeline.py`
- Modify: `tests/test_avaliacao_evidencias.py`
- Modify: `avaliacao_evidencias/README.md`

## Policy

Treat these provider failures as transient and retryable:

- HTTP/API status `429`, `500`, `502`, `503`, `504`.
- Gemini `google.genai.errors.ServerError` when `exc.code` is one of `500`, `502`, `503`, `504`.
- Generic exceptions that expose `code`, `status`, `status_code`, or `response.status_code` in that set.

Retry timing:

- If `Retry-After` exists, respect it.
- Otherwise use exponential backoff with jitter-free deterministic defaults for testability: `30s`, `60s`, `120s`.
- Default maximum retries: `3`.
- After all attempts fail, return the same structured provider error as today and continue processing the remaining items.

## Task 1: Expand Transient Retry Helper

**Files:**
- Modify: `avaliacao_evidencias/pipeline.py`
- Test: `tests/test_avaliacao_evidencias.py`

- [ ] **Step 1: Write failing tests for retryable status classification**

Add tests near `RequestsPerMinuteLimiterTests`:

```python
def test_retry_after_usa_header_para_503(self):
    from google.genai import errors

    sleeps = []
    calls = []

    def unstable():
        calls.append(1)
        if len(calls) == 1:
            raise errors.ServerError(
                503,
                {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}},
                response=types.SimpleNamespace(headers={"Retry-After": "9"}),
            )
        return "ok"

    result = executar_com_retry_transiente(unstable, sleeper=sleeps.append)

    self.assertEqual(result, "ok")
    self.assertEqual(sleeps, [9.0])
    self.assertEqual(len(calls), 2)
```

Also import the helper explicitly:

```python
from avaliacao_evidencias.pipeline import executar_com_retry_transiente
```

- [ ] **Step 2: Run test and verify it fails**

Run:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias.RequestsPerMinuteLimiterTests.test_retry_after_usa_header_para_503
```

Expected: import error or name error for `executar_com_retry_transiente`.

- [ ] **Step 3: Replace the 429-only helper with a generic transient helper**

In `avaliacao_evidencias/pipeline.py`, replace `_executar_com_retry_429()` with:

```python
RETRYABLE_PROVIDER_STATUSES = {429, 500, 502, 503, 504}
DEFAULT_TRANSIENT_RETRY_DELAYS = (30.0, 60.0, 120.0)


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
```

Keep `_retry_after_from_exception()` but remove the `status != 429` guard so it can read `Retry-After` for 503 too:

```python
def _retry_after_from_exception(exc: BaseException) -> float | None:
    response = getattr(exc, "response", None)
    retry_after = _header_retry_after(getattr(exc, "headers", None))
    if retry_after is None and response is not None:
        retry_after = _header_retry_after(getattr(response, "headers", None))
    return parse_retry_after(retry_after)
```

- [ ] **Step 4: Update call sites**

In `executar_julgamento_openrouter()`, replace:

```python
payload = _executar_com_retry_429(call_openrouter)
```

with:

```python
payload = executar_com_retry_transiente(call_openrouter)
```

In `executar_julgamento_gemini_genai()`, replace both upload and generation calls:

```python
uploaded.append(executar_com_retry_transiente(lambda arquivo=arquivo: client.files.upload(file=arquivo)))
response = executar_com_retry_transiente(
    lambda: client.models.generate_content(
        model=model,
        contents=contents,
        config={"response_mime_type": "application/json"},
    )
)
```

In legacy `executar_julgamento_gemini()`, replace:

```python
payload = _executar_com_retry_429(call_gemini)
```

with:

```python
payload = executar_com_retry_transiente(call_gemini)
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias.RequestsPerMinuteLimiterTests
```

Expected: all tests in the class pass.

## Task 2: Prove Gemini 503 Retries Before Error

**Files:**
- Modify: `tests/test_avaliacao_evidencias.py`
- Modify: `avaliacao_evidencias/pipeline.py` only if the test exposes a gap.

- [ ] **Step 1: Add provider-level test for successful retry**

Add to `ProviderAbstractionTests`:

```python
def test_gemini_retries_503_e_depois_conclui(self):
    from google.genai import errors

    sleeps = []
    calls = []

    class FakeFiles:
        def upload(self, file):
            return {"uri": f"uploaded://{Path(file).name}"}

    class FakeModels:
        def generate_content(self, model, contents, config):
            calls.append(model)
            if len(calls) == 1:
                raise errors.ServerError(
                    503,
                    {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}},
                    response=types.SimpleNamespace(headers={}),
                )
            return types.SimpleNamespace(text=json.dumps({"status": "completed", "conclusoes": []}))

    class FakeClient:
        def __init__(self, api_key):
            self.files = FakeFiles()
            self.models = FakeModels()

    fake_genai = types.SimpleNamespace(Client=FakeClient)
    fake_google = types.SimpleNamespace(genai=fake_genai)

    with patch.dict(sys.modules, {"google": fake_google, "google.genai": fake_genai}), \
         patch("avaliacao_evidencias.pipeline.time.sleep", side_effect=sleeps.append):
        result = executar_provider(
            provider="gemini",
            model="gemini-3.1-flash-lite",
            api_key="token",
            prompt="Prompt especifico",
            auditado="FUNARJ",
            questao_base="q0103",
            coluna_evidencia="q0103evi",
            itens_afirmados=[],
            pacote={"arquivos_upload": [], "documentos": []},
        )

    self.assertEqual(result, {"status": "completed", "conclusoes": []})
    self.assertEqual(len(calls), 2)
    self.assertEqual(sleeps, [30.0])
```

- [ ] **Step 2: Add provider-level test for exhausted retries**

Add to `ProviderAbstractionTests`:

```python
def test_gemini_registra_erro_apos_retries_esgotados(self):
    from google.genai import errors

    sleeps = []
    calls = []

    class FakeFiles:
        def upload(self, file):
            return {"uri": f"uploaded://{Path(file).name}"}

    class FakeModels:
        def generate_content(self, model, contents, config):
            calls.append(model)
            raise errors.ServerError(
                503,
                {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}},
                response=types.SimpleNamespace(headers={}),
            )

    class FakeClient:
        def __init__(self, api_key):
            self.files = FakeFiles()
            self.models = FakeModels()

    fake_genai = types.SimpleNamespace(Client=FakeClient)
    fake_google = types.SimpleNamespace(genai=fake_genai)

    with patch.dict(sys.modules, {"google": fake_google, "google.genai": fake_genai}), \
         patch("avaliacao_evidencias.pipeline.time.sleep", side_effect=sleeps.append):
        result = executar_provider(
            provider="gemini",
            model="gemini-3.1-flash-lite",
            api_key="token",
            prompt="Prompt especifico",
            auditado="FUNARJ",
            questao_base="q0103",
            coluna_evidencia="q0103evi",
            itens_afirmados=[],
            pacote={"arquivos_upload": [], "documentos": []},
        )

    self.assertEqual(result["status"], "error")
    self.assertIn("503", result["error"])
    self.assertEqual(len(calls), 4)
    self.assertEqual(sleeps, [30.0, 60.0, 120.0])
```

- [ ] **Step 3: Run provider tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias.ProviderAbstractionTests
```

Expected: all provider abstraction tests pass.

## Task 3: Prove Consolidation Continues After Exhausted Retry

**Files:**
- Modify: `tests/test_consolidacao_evidencias.py`
- Modify: `avaliacao_evidencias/consolidacao.py` only if the test exposes a gap.

- [ ] **Step 1: Add consolidation test**

Add to `ConsolidacaoEvidenciasTests`:

```python
def test_cli_consolidacao_continua_apos_erro_transiente_esgotado(self):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        analyses = root / "analyses.jsonl"
        out_dir = root / "out"
        analyses.write_text(
            "\n".join(
                [
                    json.dumps(_registro(identity="a", provider="gemini", model="modelo-a", questao="q0101"), ensure_ascii=False),
                    json.dumps(_registro(identity="b", provider="gemini", model="modelo-a", questao="q0102"), ensure_ascii=False),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        calls = []

        def fake_provider(**kwargs):
            calls.append(kwargs["questao_base"])
            if kwargs["questao_base"] == "q0101":
                return {"status": "error", "error": "erro ao chamar Gemini: 503 UNAVAILABLE"}
            return {"status": "completed", "conclusoes": []}

        with patch("avaliacao_evidencias.consolidacao.executar_provider", side_effect=fake_provider):
            exit_code = main([
                str(analyses),
                "--out-dir",
                str(out_dir),
                "--judge-provider",
                "gemini",
                "--judge-model",
                "gemini-3.1-flash-lite",
                "--quiet",
            ])

        registros = [json.loads(line) for line in (out_dir / "consolidated.jsonl").read_text(encoding="utf-8").splitlines()]

    self.assertEqual(exit_code, 0)
    self.assertEqual(calls, ["q0101", "q0102"])
    self.assertEqual([registro["status"] for registro in registros], ["error", "completed"])
```

- [ ] **Step 2: Run consolidation tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_consolidacao_evidencias
```

Expected: all consolidation tests pass. The current loop should already continue after provider error, so this test should pass after provider retry behavior is corrected.

## Task 4: Document Runtime Behavior

**Files:**
- Modify: `avaliacao_evidencias/README.md`

- [ ] **Step 1: Update retry documentation**

In the “Controlar requests por minuto” section, replace the retry paragraph with:

```markdown
Quando o provider retorna erro transiente (`429`, `500`, `502`, `503` ou `504`), o pipeline tenta novamente antes de gravar erro no checkpoint. Se houver header `Retry-After`, esse tempo e respeitado; sem o header, sao usados intervalos de `30s`, `60s` e `120s`. Se todas as tentativas falharem, o item recebe `status = error` e o processamento segue para o proximo item.
```

- [ ] **Step 2: Mention consolidation**

Add under “Consolidar opinioes de modelos”:

```markdown
A consolidacao usa a mesma camada de provider do processamento principal, portanto tambem aplica retries para erros transientes antes de registrar erro em `consolidated.jsonl`.
```

## Task 5: Verification

**Files:**
- No code change.

- [ ] **Step 1: Run focused suites**

Run:

```bash
.venv/bin/python -m unittest tests.test_avaliacao_evidencias tests.test_consolidacao_evidencias
```

Expected: both suites pass.

- [ ] **Step 2: Run style check**

Run:

```bash
git diff --check -- avaliacao_evidencias/pipeline.py avaliacao_evidencias/consolidacao.py tests/test_avaliacao_evidencias.py tests/test_consolidacao_evidencias.py avaliacao_evidencias/README.md
```

Expected: no output.

- [ ] **Step 3: Manual resume command**

After implementation, rerun the interrupted consolidation with `--skip-errors` omitted, so the existing 503 error is retried:

```bash
GEMINI_API_KEY='...' .venv/bin/python -m avaliacao_evidencias.consolidacao \
  .saida_analise/analyses.jsonl \
  --evidencias-root evidencias_parcial \
  --judge-provider gemini \
  --judge-model gemini-3.1-flash-lite \
  --out-dir .saida_analise/consolidado_gemini_3_1_flash_lite \
  --rpm 12
```

Expected:

- Completed records already in `consolidated.jsonl` are skipped by checkpoint.
- The existing error record is retried because `--skip-errors` is not set.
- New transient 503 failures wait and retry before being written as errors.
- Processing continues until all 21 groups are either completed or have exhausted retries.

## Self-Review

- Spec coverage: Handles Gemini 503 with wait/retry, configurable attempt count through helper defaults, records error only after all retries, and continues the consolidation loop.
- Placeholder scan: No placeholder implementation steps.
- Type consistency: Uses existing `executar_provider()` path shared by pipeline and consolidation; keeps JSONL checkpoint structure unchanged.
