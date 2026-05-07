from __future__ import annotations

from fastapi.testclient import TestClient

from review_router.api import create_app

client = TestClient(create_app())


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["fixture_safe"] is True
    assert payload["live_services_used"] is False
    assert payload["synthetic_data_only"] is True


def test_templates_endpoint() -> None:
    response = client.get("/templates")
    assert response.status_code == 200
    assert "inbox-triage-router" in response.json()["templates"]


def test_run_endpoint() -> None:
    response = client.post(
        "/run",
        json={
            "template": "inbox-triage-router",
            "fixture": {"subject": "Need help", "body": "Login broken"},
        },
    )
    assert response.status_code == 200
    assert response.json()["routing_decision"] == "support"
