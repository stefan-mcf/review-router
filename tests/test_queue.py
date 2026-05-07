from __future__ import annotations

from pathlib import Path

from review_router.review_queue import FileReviewQueue


def test_file_review_queue_lifecycle(tmp_path: Path) -> None:
    queue = FileReviewQueue(tmp_path)
    packet = queue.enqueue(
        workflow_name="inbox-triage-router",
        workflow_version="1.0.0",
        reason_for_review="low confidence",
        candidate_routes=["support", "sales"],
        evidence_snippets=["confidence=0.48"],
        recommended_next_action="inspect packet",
    )
    assert queue.list_pending()[0].packet_id == packet.packet_id
    claimed = queue.claim(packet.packet_id, "stefan")
    assert claimed.status == "claimed"
    resolved = queue.resolve(
        packet.packet_id, "stefan", {"decision": "support", "note": "looks good"}
    )
    assert resolved.status == "resolved"
