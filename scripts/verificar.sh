#!/usr/bin/env bash
# Portão local antes de cada commit: o mesmo que o CI roda (.github/workflows/ci.yml).
# Para no primeiro erro e devolve código diferente de zero.
set -euo pipefail

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$raiz"
bin=".venv/bin"

echo "== lint";        "$bin/ruff" check .
echo "== formatação";  "$bin/ruff" format --check .
echo "== tipos";       "$bin/mypy"
echo "== testes";      "$bin/pytest" -q "$@"
echo "Portão local aprovado."
