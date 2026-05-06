from __future__ import annotations

from lowcode_ai_workflows.workflow import run_ai_triage


def test_clear_support_email_routes_without_live_ai() -> None:
    result = run_ai_triage({"subject": "Need help", "body": "My account login is broken"})

    assert result["mock_ai_output"]["category"] == "support"
    assert result["review_required"] is False
    assert result["lowcode_mapping"]["n8n"] == "Webhook -> Set -> Mock AI Classifier -> Switch"
    assert result["live_services_used"] is False


def test_uncertain_email_goes_to_manual_review() -> None:
    result = run_ai_triage({"subject": "Question", "body": "Can someone look at this?"})

    assert result["mock_ai_output"]["category"] == "manual_review"
    assert result["review_required"] is True
    assert result["handoff_note"].startswith("Review before using")
