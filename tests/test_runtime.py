from __future__ import annotations

from pathlib import Path

from review_router.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


def test_run_generates_deterministic_audit_log(tmp_path: Path) -> None:
    runtime = build_runtime(ROOT)
    fixture = runtime.registry.load_fixture("inbox-triage-router", "sample-input.json")
    result = runtime.run("inbox-triage-router", fixture)

    assert result["routing_decision"] == "support"
    assert result["review_required"] is False
    assert len(result["audit_trail"]) >= 6
    audit_log = runtime.get_run(result["run_id"])
    assert audit_log["result"]["run_id"] == result["run_id"]


def test_replay_is_deterministic() -> None:
    runtime = build_runtime(ROOT)
    fixture = runtime.registry.load_fixture("lead-enrichment-router", "sample-input.json")
    result = runtime.run("lead-enrichment-router", fixture)
    replay = runtime.replay(result["run_id"])
    assert replay["hash_match"] is True


def test_uncertain_route_enqueues_review_packet() -> None:
    runtime = build_runtime(ROOT)
    fixture = {"subject": "Question", "body": "Can someone take a look at this?"}
    result = runtime.run("inbox-triage-router", fixture)
    assert result["review_required"] is True
    pending = runtime.queue.list_pending()
    assert any(packet.packet_id == result["review_packet_id"] for packet in pending)


def test_runtime_honors_isolated_artifact_directories(tmp_path: Path, monkeypatch) -> None:
    queue_dir = tmp_path / "queue"
    run_dir = tmp_path / "runs"
    monkeypatch.setenv("REVIEW_ROUTER_QUEUE_DIR", str(queue_dir))
    monkeypatch.setenv("REVIEW_ROUTER_RUN_DIR", str(run_dir))

    runtime = build_runtime(ROOT)
    fixture = runtime.registry.load_fixture("inbox-triage-router", "sample-input.json")
    result = runtime.run("inbox-triage-router", fixture)

    assert runtime.queue.root == queue_dir
    assert runtime.run_root == run_dir
    assert (run_dir / result["run_id"] / "audit-log.json").is_file()
