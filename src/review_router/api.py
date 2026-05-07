from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from review_router.runtime import build_runtime


class ValidateRequest(BaseModel):
    template: str


class RunRequest(BaseModel):
    template: str
    fixture: dict[str, Any]


class ResolveRequest(BaseModel):
    packet_id: str
    reviewer: str
    decision: str
    note: str


def create_app() -> FastAPI:
    runtime = build_runtime()
    app = FastAPI(title="Review Router API", version="0.2.0")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
        }

    @app.get("/templates")
    def templates() -> dict[str, Any]:
        return {
            "templates": runtime.registry.list_templates(),
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
        }

    @app.post("/validate")
    def validate(payload: ValidateRequest) -> dict[str, Any]:
        return {
            **runtime.validate_template(payload.template),
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
        }

    @app.post("/run")
    def run(payload: RunRequest) -> dict[str, Any]:
        return runtime.run(payload.template, payload.fixture)

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        try:
            audit_log = runtime.get_run(run_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc
        return {
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
            "audit_log": audit_log,
        }

    @app.post("/queue/resolve")
    def resolve_queue(payload: ResolveRequest) -> dict[str, Any]:
        packet = runtime.queue.resolve(
            payload.packet_id,
            payload.reviewer,
            {"decision": payload.decision, "note": payload.note},
        )
        return {
            "fixture_safe": True,
            "live_services_used": False,
            "synthetic_data_only": True,
            "packet": packet.to_dict(),
        }

    return app
