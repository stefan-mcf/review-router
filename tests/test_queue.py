from __future__ import annotations

import json
from pathlib import Path

from review_router.review_queue import FileReviewQueue


def test_file_review_queue_lifecycle(tmp_path: Path) -> None:
    queue = FileReviewQueue(tmp_path)
    packet = queue.enqueue(
        workflow_name="inbox-triage-router",
        workflow_version="1.0.0",
        reason_for_review="low confidence",
        candidate_routes=["support", "sales"],
        review_context=["confidence=0.48"],
        recommended_next_action="inspect packet",
    )
    public_packet = json.loads((tmp_path / "pending" / f"{packet.packet_id}.json").read_text())
    assert public_packet["review_context"] == ["confidence=0.48"]
    assert queue.list_pending()[0].packet_id == packet.packet_id
    claimed = queue.claim(packet.packet_id, "stefan")
    assert claimed.status == "claimed"
    resolved = queue.resolve(
        packet.packet_id, "stefan", {"decision": "support", "note": "looks good"}
    )
    assert resolved.status == "resolved"
