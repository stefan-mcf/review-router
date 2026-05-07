from __future__ import annotations

import json
from pathlib import Path

from review_router.models import WorkflowTemplate
from review_router.validator import WorkflowValidator

ROOT = Path(__file__).resolve().parents[1]


def _load_template(name: str) -> WorkflowTemplate:
    data = json.loads((ROOT / "templates" / name / "workflow.json").read_text())
    return WorkflowTemplate.model_validate(data)


def test_validator_accepts_complete_template() -> None:
    report = WorkflowValidator().validate(_load_template("inbox-triage-router"))
    assert report.valid is True
    assert report.issues == []


def test_validator_rejects_missing_manual_review_path() -> None:
    data = json.loads((ROOT / "templates" / "inbox-triage-router" / "workflow.json").read_text())
    data["steps"] = [step for step in data["steps"] if step["type"] != "review_gate"]
    template = WorkflowTemplate.model_validate(data)
    report = WorkflowValidator().validate(template)
    assert report.valid is False
    assert any(issue.code == "missing_review_path" for issue in report.issues)


def test_validator_rejects_unknown_failure_target() -> None:
    data = json.loads((ROOT / "templates" / "lead-enrichment-router" / "workflow.json").read_text())
    data["steps"][0]["failure"]["next_step_id"] = "nope"
    template = WorkflowTemplate.model_validate(data)
    report = WorkflowValidator().validate(template)
    assert report.valid is False
    assert any(issue.code == "unknown_failure_target" for issue in report.issues)
