#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "Iniciando Dashboard iGovTI 2026..."
echo "Acesse: http://localhost:5000"
echo ""

export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

python3 -m flask run --host=0.0.0.0 --port=5000
