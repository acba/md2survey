import json
import tempfile
import unittest
from pathlib import Path

from avaliacao_evidencias.consolidacao import (
    agrupar_opinioes_por_evidencia,
    calcular_identidade_parecer,
    carregar_registros_processamento,
    gerar_relatorio_pareceres,
    itens_afirmados_do_grupo,
    localizar_evidencia,
    referencias_arquivos_do_grupo,
    registros_pareceres_mais_recentes,
    main,
)


def _registro(
    *,
    identity: str,
    provider: str,
    model: str,
    auditado: str = "SEFAZ",
    questao: str = "q0101",
    coluna_evidencia: str = "q0101evi",
    evidencia: str = "Plano%20TI.pdf",
    estado: str = "conforme",
) -> dict:
    return {
        "identity": identity,
        "status": "completed",
        "auditado": auditado,
        "questao": questao,
        "coluna_evidencia": coluna_evidencia,
        "evidencia": evidencia,
        "provider": provider,
        "model": model,
        "finished_at": "2026-05-18T12:00:00+00:00",
        "result": {
            "status": "completed",
            "conclusoes": [
                {
                    "item_codigo": "q0101[A]",
                    "item_texto": "Area de TI centralizada.",
                    "afirmacao_auditado": "A",
                    "estado": estado,
                    "justificativa": f"Opiniao {provider}/{model}.",
                    "lacunas": [],
                    "arquivos_referenciados": ["Plano TI.pdf"],
                    "trechos_ou_elementos": ["Assessoria de TI"],
                    "paginas_ou_localizacao": ["p. 1"],
                }
            ],
        },
    }


class ConsolidacaoEvidenciasTests(unittest.TestCase):
    def test_agrupa_opinioes_por_evidencia_e_preserva_itens(self):
        registros = [
            _registro(identity="a", provider="gemini", model="modelo-a"),
            _registro(identity="b", provider="openrouter", model="modelo-b", estado="inconclusivo"),
            _registro(
                identity="c",
                provider="gemini",
                model="modelo-a",
                coluna_evidencia="q0102evi",
                evidencia="Outro.pdf",
            ),
            {**_registro(identity="erro", provider="gemini", model="modelo-a"), "status": "error"},
        ]

        grupos = agrupar_opinioes_por_evidencia(registros)

        self.assertEqual(len(grupos), 2)
        primeiro = grupos[0]
        self.assertEqual(primeiro.chave.auditado, "SEFAZ")
        self.assertEqual(primeiro.chave.coluna_evidencia, "q0101evi")
        self.assertEqual(len(primeiro.opinioes), 2)
        self.assertEqual([item.codigo for item in itens_afirmados_do_grupo(primeiro)], ["q0101[A]"])

    def test_carrega_multiplos_jsonl_usando_ultima_execucao_por_identidade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primeiro = root / "a.jsonl"
            segundo = root / "b.jsonl"
            primeiro.write_text(
                json.dumps(_registro(identity="same", provider="gemini", model="antigo"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            segundo.write_text(
                json.dumps(_registro(identity="same", provider="gemini", model="novo"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            registros = carregar_registros_processamento([primeiro, segundo])

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["model"], "novo")

    def test_identidade_do_parecer_muda_com_modelo_juiz(self):
        grupo = agrupar_opinioes_por_evidencia([_registro(identity="a", provider="gemini", model="modelo-a")])[0]

        primeira = calcular_identidade_parecer(
            grupo=grupo,
            judge_provider="gemini",
            judge_model="modelo-juiz-a",
            prompt_hash="prompt",
            prompt_version="v1",
        )
        segunda = calcular_identidade_parecer(
            grupo=grupo,
            judge_provider="gemini",
            judge_model="modelo-juiz-b",
            prompt_hash="prompt",
            prompt_version="v1",
        )

        self.assertNotEqual(primeira, segunda)

    def test_localiza_evidencia_exportada_por_referencia_do_modelo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auditado_dir = root / "FUNARJ"
            auditado_dir.mkdir()
            esperado = auditado_dir / "00009_02_decreto-funarj-n.49.691-altera-e-consolida-a-estrutura-organizacional-e-o-estatuto-da-funarj.pdf"
            esperado.write_text("decreto", encoding="utf-8")
            grupo = agrupar_opinioes_por_evidencia(
                [
                    _registro(
                        identity="a",
                        provider="gemini",
                        model="modelo-a",
                        auditado="FUNARJ",
                        evidencia="Decreto%20FUNARJ%20%28N.49.691%29%20-%20Altera%20e%20consolida%20a%20Estrutura%20Organizacional%20e%20o%20Estatuto%20da%20FUNARJ.pdf",
                    )
                ]
            )[0]

            caminho = localizar_evidencia(
                root,
                grupo.chave,
                referencias_arquivos=referencias_arquivos_do_grupo(grupo),
            )

        self.assertEqual(caminho, esperado)

    def test_localiza_evidencia_exportada_por_match_limesurvey(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auditado_dir = root / "FUNARJ"
            auditado_dir.mkdir()
            esperado = auditado_dir / "00009_03_competencias-atribuicoes.zip"
            esperado.write_text("zip", encoding="utf-8")
            grupo = agrupar_opinioes_por_evidencia(
                [
                    _registro(
                        identity="a",
                        provider="gemini",
                        model="modelo-a",
                        auditado="FUNARJ",
                        evidencia="competencias%20atribuicoes.zip",
                    )
                ]
            )[0]

            caminho = localizar_evidencia(root, grupo.chave)

        self.assertEqual(caminho, esperado)

    def test_cli_fake_gera_checkpoint_e_relatorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            analyses = root / "analyses.jsonl"
            out_dir = root / "out"
            analyses.write_text(
                "\n".join(
                    [
                        json.dumps(_registro(identity="a", provider="gemini", model="modelo-a"), ensure_ascii=False),
                        json.dumps(_registro(identity="b", provider="openrouter", model="modelo-b"), ensure_ascii=False),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code = main([str(analyses), "--out-dir", str(out_dir), "--quiet"])

            checkpoint = out_dir / "consolidated.jsonl"
            self.assertEqual(exit_code, 0)
            self.assertTrue(checkpoint.is_file())
            self.assertTrue((out_dir / "pareceres_consolidados.xlsx").is_file())
            registros = [json.loads(line) for line in checkpoint.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0]["status"], "completed")
            self.assertEqual(registros[0]["opinion_count"], 2)

    def test_relatorio_usa_parecer_mais_recente_por_evidencia_e_juiz(self):
        antigo = {
            **_registro(identity="old", provider="gemini", model="modelo-a"),
            "judge_provider": "gemini",
            "judge_model": "juiz",
            "finished_at": "2026-05-18T10:00:00+00:00",
            "evidence_hash": "",
        }
        novo = {
            **_registro(identity="new", provider="gemini", model="modelo-a", estado="nao_conforme"),
            "judge_provider": "gemini",
            "judge_model": "juiz",
            "finished_at": "2026-05-18T11:00:00+00:00",
            "evidence_hash": "hash-real",
        }

        recentes = registros_pareceres_mais_recentes([antigo, novo])

        self.assertEqual([registro["identity"] for registro in recentes], ["new"])

    def test_relatorio_nao_duplica_parecer_antigo_da_mesma_evidencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoint = root / "consolidated.jsonl"
            destino = root / "pareceres.xlsx"
            antigo = {
                **_registro(identity="old", provider="gemini", model="modelo-a"),
                "judge_provider": "gemini",
                "judge_model": "juiz",
                "finished_at": "2026-05-18T10:00:00+00:00",
                "evidence_hash": "",
            }
            novo = {
                **_registro(identity="new", provider="gemini", model="modelo-a", estado="nao_conforme"),
                "judge_provider": "gemini",
                "judge_model": "juiz",
                "finished_at": "2026-05-18T11:00:00+00:00",
                "evidence_hash": "hash-real",
            }
            checkpoint.write_text(
                json.dumps(antigo, ensure_ascii=False) + "\n" + json.dumps(novo, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            linhas = gerar_relatorio_pareceres(checkpoint, destino)

        self.assertEqual(linhas, 1)


if __name__ == "__main__":
    unittest.main()
