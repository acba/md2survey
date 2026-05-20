#!/usr/bin/env python3
"""Teste rápido do app Flask."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

client = app.test_client()

print("Testando rotas do Flask...")

# Test GET /
resp = client.get('/')
assert resp.status_code == 200
assert b'Dashboard iGovTI 2026' in resp.data
print(f"✓ GET / → {resp.status_code}")

# Test POST /upload
with open("sample_data/kimi_dummy.xlsx", "rb") as f:
    resp = client.post('/upload', data={"file": f}, content_type="multipart/form-data")
assert resp.status_code == 200
assert resp.content_type == "application/json"
data = resp.get_json()
assert "metricas" in data
assert "figuras_base64" in data
assert data["metricas"]["cronbach"] > 0.9
print(f"✓ POST /upload → {resp.status_code}, Cronbach={data['metricas']['cronbach']}")

print("\n✓ Todas as rotas do Flask estão OK!")
