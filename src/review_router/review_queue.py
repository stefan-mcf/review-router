from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ReviewPacket:
    packet_id: str
    workflow_name: str
    workflow_version: str
    reason_for_review: str
    candidate_routes: list[str]
    evidence_snippets: list[str]
    recommended_next_action: str
    queue: str
    status: str = "pending"
    claimed_by: str | None = None
    resolution: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class FileReviewQueue:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.pending_dir = root / "pending"
        self.claimed_dir = root / "claimed"
        self.resolved_dir = root / "resolved"
        self.dead_letter_dir = root / "dead-letter"
        for directory in [
            self.pending_dir,
            self.claimed_dir,
            self.resolved_dir,
            self.dead_letter_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _path_for(self, directory: Path, packet_id: str) -> Path:
        return directory / f"{packet_id}.json"

    def _save(self, directory: Path, packet: ReviewPacket) -> ReviewPacket:
        self._path_for(directory, packet.packet_id).write_text(
            json.dumps(packet.to_dict(), indent=2) + "\n"
        )
        return packet

    def enqueue(
        self,
        workflow_name: str,
        workflow_version: str,
        reason_for_review: str,
        candidate_routes: list[str],
        evidence_snippets: list[str],
        recommended_next_action: str,
        queue: str = "default",
    ) -> ReviewPacket:
        seed = json.dumps(
            {
                "workflow_name": workflow_name,
                "workflow_version": workflow_version,
                "reason": reason_for_review,
                "candidate_routes": candidate_routes,
                "evidence": evidence_snippets,
                "recommended_next_action": recommended_next_action,
                "queue": queue,
            },
            sort_keys=True,
        )
        packet_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        packet = ReviewPacket(
            packet_id=packet_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
            reason_for_review=reason_for_review,
            candidate_routes=candidate_routes,
            evidence_snippets=evidence_snippets,
            recommended_next_action=recommended_next_action,
            queue=queue,
        )
        return self._save(self.pending_dir, packet)

    def _load(self, path: Path) -> ReviewPacket:
        return ReviewPacket(**json.loads(path.read_text()))

    def list_pending(self) -> list[ReviewPacket]:
        return [self._load(path) for path in sorted(self.pending_dir.glob("*.json"))]

    def claim(self, packet_id: str, reviewer: str) -> ReviewPacket:
        src = self._path_for(self.pending_dir, packet_id)
        packet = self._load(src)
        packet.status = "claimed"
        packet.claimed_by = reviewer
        src.unlink()
        return self._save(self.claimed_dir, packet)

    def resolve(self, packet_id: str, reviewer: str, resolution: dict[str, Any]) -> ReviewPacket:
        src = self._path_for(self.claimed_dir, packet_id)
        packet = self._load(src)
        packet.status = "resolved"
        packet.claimed_by = reviewer
        packet.resolution = resolution
        src.unlink()
        return self._save(self.resolved_dir, packet)

    def dead_letter(self, packet_id: str, reason: str) -> ReviewPacket:
        for directory in [self.pending_dir, self.claimed_dir]:
            candidate = self._path_for(directory, packet_id)
            if candidate.exists():
                packet = self._load(candidate)
                packet.status = "dead_letter"
                packet.resolution = {"reason": reason}
                candidate.unlink()
                return self._save(self.dead_letter_dir, packet)
        raise FileNotFoundError(packet_id)
