import json
import subprocess
import sys
import types
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from avaliacao_evidencias.providers_ai_service import (
    carregar_json_modelo,
    executar_com_retry_transiente,
    executar_provider,
    parse_retry_after,
)


class ProvidersAiServiceTests(unittest.TestCase):
    def test_importar_provider_nao_carrega_pipeline(self):
        script = (
            "import sys; "
            "import avaliacao_evidencias.providers_ai_service; "
            "print('avaliacao_evidencias.pipeline' in sys.modules)"
        )

        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.stdout.strip(), "False")

    def test_modulo_nao_depende_do_pipeline(self):
        import avaliacao_evidencias.providers_ai_service as providers

        self.assertNotIn("avaliacao_evidencias.pipeline", providers.__dict__.get("__file__", ""))
        self.assertNotIn("pipeline", providers.__dict__)

    def test_carrega_json_modelo_com_json_repair(self):
        resultado = carregar_json_modelo('{status: "completed", conclusoes: []}')

        self.assertEqual(resultado, {"status": "completed", "conclusoes": []})

    def test_openrouter_respeita_retry_after_em_429(self):
        calls = []
        sleeps = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps({"status": "completed", "conclusoes": []})
                            }
                        }
                    ]
                }).encode("utf-8")

        def fake_urlopen(request, timeout):
            calls.append(request)
            if len(calls) == 1:
                raise urllib.error.HTTPError(
                    request.full_url,
                    429,
                    "Too Many Requests",
                    {"Retry-After": "7"},
                    None,
                )
            return FakeResponse()

        with patch("avaliacao_evidencias.providers_ai_service.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("avaliacao_evidencias.providers_ai_service.time.sleep", side_effect=sleeps.append):
            result = executar_provider(
                provider="openrouter",
                model="modelo/teste",
                api_key="token",
                prompt="Prompt especifico",
                auditado="SEFAZ",
                questao_base="q1",
                coluna_evidencia="q1evi",
                itens_afirmados=[],
                pacote={"documentos": []},
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [7.0])

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
             patch("avaliacao_evidencias.providers_ai_service.time.sleep", side_effect=sleeps.append):
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

    def test_parse_retry_after_segundos(self):
        self.assertEqual(parse_retry_after("10"), 10.0)

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


if __name__ == "__main__":
    unittest.main()
