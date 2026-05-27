from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _run(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-m", "review_router.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=ENV,
        check=True,
    )
    return json.loads(completed.stdout)


def test_cli_list_templates() -> None:
    payload = _run("list")
    assert "inbox-triage-router" in payload["templates"]


def test_cli_validate_template() -> None:
    payload = _run("validate", "lead-enrichment-router")
    assert payload["valid"] is True


def test_cli_run_template() -> None:
    payload = _run(
        "run",
        "support-urgency-sentiment",
        "--fixture",
        "templates/support-urgency-sentiment/fixtures/sample-input.json",
    )
    assert payload["routing_decision"] == "escalate"
