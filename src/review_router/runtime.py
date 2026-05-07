from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from review_router.models import (
    AIStep,
    DestinationStep,
    HandoffStep,
    ReviewGateStep,
    RouteStep,
    TransformStep,
    TriggerStep,
    WorkflowTemplate,
)
from review_router.review_queue import FileReviewQueue
from review_router.validator import WorkflowValidator


class TemplateRegistry:
    def __init__(self, templates_root: Path) -> None:
        self.templates_root = templates_root

    def list_templates(self) -> list[str]:
        return sorted(path.name for path in self.templates_root.iterdir() if path.is_dir())

    def template_dir(self, template_name: str) -> Path:
        return self.templates_root / template_name

    def load_template(self, template_name: str) -> WorkflowTemplate:
        data = json.loads((self.template_dir(template_name) / "workflow.json").read_text())
        return WorkflowTemplate.model_validate(data)

    def fixture_path(self, template_name: str, fixture_name: str) -> Path:
        return self.template_dir(template_name) / "fixtures" / fixture_name

    def load_fixture(self, template_name: str, fixture_name: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads(self.fixture_path(template_name, fixture_name).read_text()),
        )

    def expected_output(self, template_name: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads((self.template_dir(template_name) / "expected_output.json").read_text()),
        )


class WorkflowRuntime:
    def __init__(self, registry: TemplateRegistry, queue: FileReviewQueue, run_root: Path) -> None:
        self.registry = registry
        self.queue = queue
        self.run_root = run_root
        self.validator = WorkflowValidator()
        self.run_root.mkdir(parents=True, exist_ok=True)

    def validate_template(self, template_name: str) -> dict[str, object]:
        template = self.registry.load_template(template_name)
        return self.validator.validate(template).to_dict()

    def _hash_payload(self, payload: Any) -> str:
        rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    def _classify_template(self, template_name: str, fixture: dict[str, Any]) -> dict[str, Any]:
        text = json.dumps(fixture, sort_keys=True).lower()
        if template_name == "lead-enrichment-router":
            high_intent = any(term in text for term in ["demo", "pricing", "enterprise"])
            return {
                "category": "crm_route" if high_intent else "manual_research",
                "confidence": 0.93 if high_intent else 0.62,
                "reason": "high-intent lead keywords"
                if high_intent
                else "insufficient enrichment confidence",
            }
        if template_name == "inbox-triage-router":
            if any(term in text for term in ["invoice", "refund", "billing"]):
                return {"category": "billing", "confidence": 0.9, "reason": "billing keywords"}
            if any(term in text for term in ["broken", "login", "error", "support"]):
                return {"category": "support", "confidence": 0.91, "reason": "support keywords"}
            if any(term in text for term in ["quote", "demo", "sales"]):
                return {"category": "sales", "confidence": 0.88, "reason": "sales keywords"}
            return {
                "category": "manual_review",
                "confidence": 0.48,
                "reason": "low confidence inbox classification",
            }
        if template_name == "support-urgency-sentiment":
            urgent = any(term in text for term in ["outage", "down", "production", "urgent"])
            return {
                "category": "escalate" if urgent else "normal_queue",
                "confidence": 0.92 if urgent else 0.83,
                "reason": "urgency terms" if urgent else "standard support tone",
            }
        if template_name == "content-rss-summarizer":
            publishable = any(term in text for term in ["benchmark", "release", "workflow"])
            return {
                "category": "publish_queue" if publishable else "review_queue",
                "confidence": 0.86 if publishable else 0.64,
                "reason": "relevant automation topic"
                if publishable
                else "summary requires editorial review",
            }
        if template_name == "creative-pack-review":
            return {
                "category": "review_required",
                "confidence": 0.55,
                "reason": "creative output always requires review before generation",
            }
        if template_name == "workflow-debug-replay":
            transient = any(term in text for term in ["timeout", "429", "rate limit"])
            return {
                "category": "retry_fix" if transient else "logic_fix",
                "confidence": 0.89 if transient else 0.81,
                "reason": "transient failure signal" if transient else "workflow logic mismatch",
            }
        return {"category": "manual_review", "confidence": 0.4, "reason": "unknown template"}

    def run(self, template_name: str, fixture: dict[str, Any]) -> dict[str, Any]:
        template = self.registry.load_template(template_name)
        validation = self.validator.validate(template)
        if not validation.valid:
            raise ValueError(validation.to_text())

        run_id = self._hash_payload(
            {"template": template_name, "fixture": fixture, "version": template.version}
        )[:16]
        run_dir = self.run_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        state: dict[str, Any] = {
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
            "template_name": template.name,
            "template_version": template.version,
            "template_description": template.description,
            "input": fixture,
            "review_required": False,
            "routing_decision": "manual_review",
            "review_packet_id": None,
            "review_reason": None,
            "candidate_routes": [],
            "recommended_next_action": None,
            "audit_trail": [],
            "output": {},
        }

        ai_result: dict[str, Any] | None = None
        for step in template.steps:
            input_hash = self._hash_payload(state)
            output_snapshot: dict[str, Any] = {}
            error: str | None = None
            try:
                if isinstance(step, TriggerStep):
                    output_snapshot = {"source": step.source, "record_count": 1}
                elif isinstance(step, TransformStep):
                    if step.transform == "normalize_input":
                        state["normalized_input"] = {k: v for k, v in fixture.items()}
                        output_snapshot = {
                            "normalized_keys": sorted(state["normalized_input"].keys())
                        }
                    elif step.transform == "draft_summary":
                        title = str(fixture.get("title", "Untitled"))
                        snippet = str(fixture.get("snippet", ""))
                        state["draft_summary"] = f"{title}: {snippet[:80]}"
                        output_snapshot = {"draft_summary": state["draft_summary"]}
                    elif step.transform == "build_creative_manifest":
                        state["creative_manifest"] = {
                            "workflow": "creative-pack-review",
                            "brief": fixture.get("brief", ""),
                            "prompts": fixture.get("prompts", []),
                            "comfyui_boundary": "review gate before any live generation",
                        }
                        output_snapshot = state["creative_manifest"]
                    elif step.transform == "parse_failure_log":
                        state["diagnosis_input"] = {
                            "error": fixture.get("error", ""),
                            "context": fixture.get("context", ""),
                        }
                        output_snapshot = state["diagnosis_input"]
                    else:
                        output_snapshot = {"transform": step.transform}
                elif isinstance(step, AIStep):
                    ai_result = self._classify_template(template_name, fixture)
                    state["ai_result"] = ai_result
                    output_snapshot = ai_result
                elif isinstance(step, ReviewGateStep):
                    assert ai_result is not None
                    requires_review = ai_result["confidence"] < 0.75 or ai_result["category"] in {
                        "review_required",
                        "manual_review",
                        "review_queue",
                    }
                    state["review_required"] = requires_review
                    state["review_reason"] = ai_result["reason"] if requires_review else None
                    state["candidate_routes"] = step.policy.candidate_routes
                    state["recommended_next_action"] = step.policy.recommended_next_action
                    output_snapshot = {
                        "review_required": requires_review,
                        "reason": state["review_reason"],
                    }
                    if requires_review:
                        packet = self.queue.enqueue(
                            workflow_name=template.name,
                            workflow_version=template.version,
                            reason_for_review=step.policy.reason + ": " + ai_result["reason"],
                            candidate_routes=step.policy.candidate_routes,
                            evidence_snippets=[
                                f"confidence={ai_result['confidence']}",
                                ai_result["reason"],
                            ],
                            recommended_next_action=step.policy.recommended_next_action,
                            queue=step.policy.queue,
                        )
                        state["review_packet_id"] = packet.packet_id
                elif isinstance(step, RouteStep):
                    assert ai_result is not None
                    route_key = ai_result["category"]
                    if state["review_required"]:
                        route_key = "manual_review"
                    state["routing_decision"] = route_key
                    output_snapshot = {"route_key": route_key}
                elif isinstance(step, DestinationStep):
                    if state["review_required"] and step.destination != "review_queue":
                        output_snapshot = {"skipped_destination": step.destination}
                    else:
                        state["destination"] = step.destination
                        output_snapshot = {"destination": step.destination}
                elif isinstance(step, HandoffStep):
                    note = step.note_template.format(
                        routing_decision=state["routing_decision"],
                        review_required=str(state["review_required"]).lower(),
                        review_reason=state["review_reason"] or "not required",
                    )
                    state["handoff_note"] = note
                    output_snapshot = {"handoff_note": note}
            except Exception as exc:  # pragma: no cover
                error = str(exc)
            output_hash = self._hash_payload({"state": state, "step_output": output_snapshot})
            state["audit_trail"].append(
                {
                    "step_id": step.id,
                    "step_type": step.type,
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "timestamp": f"deterministic:{template.version}:{step.id}",
                    "error": error,
                }
            )

        result = {
            "run_id": run_id,
            "workflow_name": template.name,
            "workflow_version": template.version,
            "routing_decision": state["routing_decision"],
            "review_required": state["review_required"],
            "review_packet_id": state["review_packet_id"],
            "review_reason": state["review_reason"],
            "candidate_routes": state["candidate_routes"],
            "recommended_next_action": state["recommended_next_action"],
            "mock_ai_output": ai_result,
            "handoff_note": state.get("handoff_note"),
            "audit_trail": state["audit_trail"],
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
            "destination": state.get(
                "destination",
                "review_queue" if state["review_required"] else state["routing_decision"],
            ),
            "template_output": {
                "classification": ai_result,
                "normalized_input": state.get("normalized_input", fixture),
                "draft_summary": state.get("draft_summary"),
                "creative_manifest": state.get("creative_manifest"),
                "diagnosis_input": state.get("diagnosis_input"),
            },
        }
        audit_log = {
            "run_id": run_id,
            "template": template.model_dump(mode="json"),
            "fixture": fixture,
            "result": result,
        }
        (run_dir / "audit-log.json").write_text(json.dumps(audit_log, indent=2) + "\n")
        return result

    def get_run(self, run_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads((self.run_root / run_id / "audit-log.json").read_text()),
        )

    def replay(self, run_id: str) -> dict[str, Any]:
        audit_log = self.get_run(run_id)
        rerun = self.run(audit_log["template"]["name"], audit_log["fixture"])
        original_result = audit_log["result"]
        return {
            "run_id": run_id,
            "replay_run_id": rerun["run_id"],
            "hash_match": self._hash_payload(original_result) == self._hash_payload(rerun),
            "original_result_hash": self._hash_payload(original_result),
            "replay_result_hash": self._hash_payload(rerun),
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
        }


def build_runtime(base_path: Path | None = None) -> WorkflowRuntime:
    repo_root = Path(__file__).resolve().parents[2] if base_path is None else base_path
    registry = TemplateRegistry(repo_root / "templates")
    queue = FileReviewQueue(repo_root / "artifacts" / "local" / "queue")
    return WorkflowRuntime(
        registry=registry, queue=queue, run_root=repo_root / "artifacts" / "local" / "runs"
    )
