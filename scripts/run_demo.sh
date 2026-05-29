#!/usr/bin/env bash
# Ejecuta la suite completa y abre el dashboard de Allure (Linux / macOS).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/2] Ejecutando suite de pruebas de API..."
python -m pytest --alluredir=allure-results

echo "[2/2] Abriendo dashboard de Allure..."
if command -v allure >/dev/null 2>&1; then
    allure serve allure-results
else
    echo "Allure CLI no encontrado. Instalalo con: npm install -g allure-commandline"
fi
