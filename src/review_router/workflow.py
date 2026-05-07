"""Controlled AI workflow proof with deterministic mock AI output."""

from __future__ import annotations

from typing import Any


def _classify(text: str) -> dict[str, Any]:
    lowered = text.lower()
    if any(term in lowered for term in ["login", "broken", "help", "account"]):
        return {"category": "support", "confidence": 0.91, "reason": "support keywords"}
    if any(term in lowered for term in ["price", "quote", "demo", "sales"]):
        return {"category": "sales", "confidence": 0.88, "reason": "sales keywords"}
    return {"category": "manual_review", "confidence": 0.42, "reason": "low confidence"}


def run_ai_triage(message: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic AI-style triage workflow with manual review branch."""

    text = f"{message.get('subject', '')} {message.get('body', '')}"
    mock_ai_output = _classify(text)
    review_required = mock_ai_output["confidence"] < 0.75
    return {
        "workflow_name": "controlled-ai-triage",
        "input": message,
        "mock_ai_output": mock_ai_output,
        "review_required": review_required,
        "routing_decision": "manual_review" if review_required else mock_ai_output["category"],
        "lowcode_mapping": {
            "n8n": "Webhook -> Set -> Mock AI Classifier -> Switch",
            "Make": "Webhook -> Text parser -> Mock AI module -> Router",
            "Zapier": "Trigger -> Formatter -> AI by Zapier placeholder -> Paths",
        },
        "handoff_note": (
            "Review before using live AI output. Replace mock classifier only after approval."
        ),
        "fixture_safe": True,
        "live_services_used": False,
    }
