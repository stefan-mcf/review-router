from __future__ import annotations

import argparse
import json
from pathlib import Path

from review_router.runtime import build_runtime


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review-router")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    validate = sub.add_parser("validate")
    validate.add_argument("template")

    run = sub.add_parser("run")
    run.add_argument("template")
    run.add_argument("--fixture", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("run_id")

    queue = sub.add_parser("queue")
    queue_sub = queue.add_subparsers(dest="queue_command", required=True)
    queue_sub.add_parser("list")
    claim = queue_sub.add_parser("claim")
    claim.add_argument("packet_id")
    claim.add_argument("--reviewer", required=True)
    resolve = queue_sub.add_parser("resolve")
    resolve.add_argument("packet_id")
    resolve.add_argument("--reviewer", required=True)
    resolve.add_argument("--decision", required=True)
    resolve.add_argument("--note", required=True)

    args = parser.parse_args(argv)
    runtime = build_runtime()

    if args.command == "list":
        print(_json_dump({"templates": runtime.registry.list_templates()}), end="")
        return 0
    if args.command == "validate":
        print(_json_dump(runtime.validate_template(args.template)), end="")
        return 0
    if args.command == "run":
        fixture = json.loads(Path(args.fixture).read_text())
        print(_json_dump(runtime.run(args.template, fixture)), end="")
        return 0
    if args.command == "replay":
        print(_json_dump(runtime.replay(args.run_id)), end="")
        return 0
    if args.command == "queue":
        if args.queue_command == "list":
            print(
                _json_dump(
                    {"pending": [packet.to_dict() for packet in runtime.queue.list_pending()]}
                ),
                end="",
            )
            return 0
        if args.queue_command == "claim":
            print(
                _json_dump(runtime.queue.claim(args.packet_id, args.reviewer).to_dict()),
                end="",
            )
            return 0
        if args.queue_command == "resolve":
            resolution = {"decision": args.decision, "note": args.note}
            print(
                _json_dump(
                    runtime.queue.resolve(
                        args.packet_id,
                        args.reviewer,
                        resolution,
                    ).to_dict()
                ),
                end="",
            )
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
