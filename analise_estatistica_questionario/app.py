#!/usr/bin/env python3
"""
Dashboard iGovTI 2026 — Servidor Flask
Recebe XLSX via upload, processa via analise_igovti.py e retorna JSON.
"""

import os
import sys
import tempfile
import json
from flask import Flask, render_template, request, jsonify

# Garantir que analise_igovti.py está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analise_igovti import analisar_questionario

app = Flask(__name__, template_folder='.', static_folder='assets', static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


@app.route("/")
def index():
    return render_template("template.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio"}), 400

    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Formato inválido. Envie um arquivo Excel (.xlsx)"}), 400

    # Salvar temporariamente
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        resultado = analisar_questionario(tmp_path)
        return jsonify(resultado)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
