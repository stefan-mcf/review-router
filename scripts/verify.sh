#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-}"

if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3.11"
  fi
fi

PYTHONPATH=src "$PYTHON_BIN" -m pytest -q
"$PYTHON_BIN" -m ruff check .
PYTHONPATH=src "$PYTHON_BIN" -m mypy src
PYTHONPATH=src "$PYTHON_BIN" scripts/template_validation_sweep.py
PYTHONPATH=src "$PYTHON_BIN" scripts/public_readiness_check.py
PYTHONPATH=src "$PYTHON_BIN" scripts/generate_screenshots.py --check
