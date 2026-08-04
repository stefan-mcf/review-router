from __future__ import annotations

from typing import Any

from review_router.runtime import build_runtime


def run_ai_triage(message: dict[str, Any]) -> dict[str, Any]:
    """Compatibility helper for the original inbox-triage interface."""

    runtime = build_runtime()
    result = runtime.run("inbox-triage-router", message)
    return {
        "workflow_name": result["workflow_name"],
        "input": message,
        "mock_ai_output": result["mock_ai_output"],
        "review_required": result["review_required"],
        "routing_decision": result["routing_decision"],
        "lowcode_mapping": {
            "n8n": "Webhook -> Set -> Mock AI Classifier -> Switch",
            "Make": "Webhook -> Text parser -> Mock AI module -> Router",
            "Zapier": "Trigger -> Formatter -> AI by Zapier placeholder -> Paths",
        },
        "handoff_note": ("Review before using live AI output. " + str(result["handoff_note"])),
        "fixture_safe": result["fixture_safe"],
        "live_services_used": result["live_services_used"],
        "synthetic_data_only": result["synthetic_data_only"],
    }
