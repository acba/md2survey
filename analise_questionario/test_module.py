#!/usr/bin/env python3
"""Teste rápido do app Flask sem servidor HTTP."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analise_igovti import analisar_questionario

print("Testando analise_igovti.py...")
resultado = analisar_questionario("sample_data/kimi_dummy.xlsx")

assert "metricas" in resultado
assert "figuras_base64" in resultado
assert "estagios_geral" in resultado
assert "pca_por_pratica" in resultado
assert "correlacoes_implicitas" in resultado
assert "matriz_correlacao" in resultado
assert "heatmap_organizacoes" in resultado

m = resultado["metricas"]
print(f"✓ Cronbach: {m['cronbach']}")
print(f"✓ KMO: {m['kmo']}")
print(f"✓ iGovTI média: {m['igovti_mean']}")
print(f"✓ Figuras: {list(resultado['figuras_base64'].keys())}")
print(f"✓ Práticas: {list(resultado['pca_por_pratica'].keys())}")
print(f"✓ Estágios: {resultado['estagios_geral']}")

# Verificar se é serializável em JSON
import json
json_str = json.dumps(resultado)
print(f"✓ JSON serializado: {len(json_str)} caracteres")

print("\n✓ Todos os testes passaram!")
