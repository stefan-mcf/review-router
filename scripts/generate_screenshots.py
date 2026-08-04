from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

from review_router.api import create_app

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
MANIFEST = OUT / "manifest.json"
EXPECTED_IMAGES = [
    "01-system-flow.png",
    "02-interface-surface.png",
    "03-core-processing.png",
    "04-guardrail-path.png",
    "05-output-readback.png",
    "06-validation-scope.png",
]

WIDTH = 1400
HEIGHT = 800
BG = "#0b1120"
PANEL = "#111827"
HEADER = "#182235"
BORDER = "#334155"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#60a5fa"
SUCCESS = "#4ade80"
ERROR = "#f87171"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        ("/System/Library/Fonts/Menlo.ttc", 1 if bold else 0),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            0,
        ),
        (
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
            0,
        ),
    ]
    for candidate, index in candidates:
        try:
            return ImageFont.truetype(candidate, size=size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
SUBTITLE_FONT = font(18)
PANEL_TITLE_FONT = font(18, bold=True)
BODY_FONT = font(16)
CODE_FONT = font(15)
FOOTER_FONT = font(15)


def public_text(value: str) -> str:
    cleaned = value.replace(str(ROOT), ".").replace(str(Path.home()), "<home>")
    return re.sub(r"\s+in\s+\d+(?:\.\d+)?s\b", "", cleaned)


def display_command(command: list[str]) -> str:
    rendered = ["python" if part == sys.executable else public_text(part) for part in command]
    return shlex.join(rendered)


def run(command: list[str], *, timeout: int = 120, max_lines: int = 8) -> list[str]:
    python_bin = str(Path(sys.executable).resolve().parent)
    env = {
        **os.environ,
        "PYTHONPATH": os.environ.get("PYTHONPATH", "src"),
        "PATH": f"{python_bin}:{os.environ.get('PATH', '')}",
    }
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"command timed out: {display_command(command)}") from exc
    output = public_text(result.stdout.strip())
    if result.returncode != 0:
        raise RuntimeError(
            f"command returned {result.returncode}: {display_command(command)}\n{output}"
        )
    lines = output.splitlines()[-max_lines:] if output else ["completed with no output"]
    return [f"$ {display_command(command)}", "PASS", *lines]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def compact_json_lines(payload: dict[str, Any], keys: list[str]) -> list[str]:
    lines: list[str] = []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (dict, list)):
            encoded = json.dumps(value, sort_keys=True)
            lines.append(f"{key}={encoded}")
        else:
            lines.append(f"{key}={value}")
    return lines


def wrap_lines(lines: list[str], width: int) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(
            textwrap.wrap(
                public_text(line),
                width=width,
                replace_whitespace=False,
                drop_whitespace=False,
            )
            or [line]
        )
    return wrapped


def draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    accent: str = ACCENT,
    code: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1 + 20, x1 + 5, y2 - 20), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=PANEL_TITLE_FONT, fill=accent)
    selected_font = CODE_FONT if code else BODY_FONT
    max_chars = max(34, (x2 - x1 - 68) // (9 if code else 10))
    y = y1 + 58
    for line in wrap_lines(lines, max_chars):
        if y > y2 - 34:
            break
        fill = TEXT
        if line == "PASS" or line.startswith(("fixture_safe=true", "live_services_used=false")):
            fill = SUCCESS
        elif line.startswith(("review_required=true", "blocked")):
            fill = ERROR
        elif line.startswith(("$", "GET ", "POST ")):
            fill = ACCENT
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 27


def validate_public_copy(copy: str) -> None:
    retired = ("pro" + "of", "evi" + "dence", "walk" + "through", "tuto" + "rial")
    lowered = copy.lower()
    matches = [term for term in retired if term in lowered]
    if matches:
        raise RuntimeError(f"public copy contains retired terminology: {matches}")
    unsafe_markers = (
        "/" + "Users/",
        "/" + "home/",
        "command_exit_code",
        "FAILED",
        "\nFAIL\n",
    )
    if any(marker in copy for marker in unsafe_markers):
        raise RuntimeError("public copy contains a local path or command error marker")


def source_paths() -> list[Path]:
    paths = [
        Path(__file__),
        ROOT / ".env.example",
        ROOT / "src" / "review_router" / "api.py",
        ROOT / "src" / "review_router" / "cli.py",
        ROOT / "src" / "review_router" / "runtime.py",
        ROOT / "src" / "review_router" / "review_queue.py",
        ROOT / "scripts" / "public_readiness_check.py",
        ROOT / "scripts" / "template_validation_sweep.py",
    ]
    paths.extend(sorted((ROOT / "templates").glob("**/*.json")))
    return paths


def source_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in source_paths():
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def render(
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    *,
    fingerprint: str,
    footer: str = "Local inputs | No model calls | No provider writes",
) -> dict[str, str]:
    public_copy = public_text(
        json.dumps(
            {
                "title": title,
                "subtitle": subtitle,
                "footer": footer,
                "panels": [
                    {"title": str(panel["title"]), "lines": list(panel["lines"])}
                    for panel in panels
                ],
            },
            sort_keys=True,
        )
    )
    validate_public_copy(public_copy)

    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((32, 28, 1368, 122), radius=24, fill=HEADER, outline=BORDER, width=2)
    draw.text((60, 50), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 94), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    for panel in panels:
        draw_panel(
            draw,
            panel["box"],
            str(panel["title"]),
            list(panel["lines"]),
            accent=str(panel.get("accent", ACCENT)),
            code=bool(panel.get("code", False)),
        )
    draw.rounded_rectangle((32, 730, 1368, 772), radius=16, fill=HEADER, outline=BORDER, width=1)
    draw.text((56, 741), footer, font=FOOTER_FONT, fill=MUTED)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("PortfolioCopy", public_copy)
    metadata.add_text("SourceFingerprint", fingerprint)
    metadata.add_text("ValidationStatus", "passed")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 30_000 or max(stat.stddev) < 18:
        raise RuntimeError(
            f"image may be unreadable: {path.name} size={path.stat().st_size} stddev={stat.stddev}"
        )
    return {
        "file": path.name,
        "copy_sha256": hashlib.sha256(public_copy.encode()).hexdigest(),
    }


def write_manifest(fingerprint: str, artifacts: list[dict[str, str]]) -> None:
    payload = {
        "schema_version": 1,
        "source_fingerprint": fingerprint,
        "validation_status": "passed",
        "artifacts": artifacts,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def check_images() -> None:
    manifest = json.loads(MANIFEST.read_text())
    expected_fingerprint = source_fingerprint()
    if manifest.get("source_fingerprint") != expected_fingerprint:
        raise RuntimeError("portfolio images are stale; regenerate them")
    artifacts = manifest.get("artifacts", [])
    if [item.get("file") for item in artifacts] != EXPECTED_IMAGES:
        raise RuntimeError("portfolio image manifest does not match the six-image sequence")
    for item in artifacts:
        path = OUT / str(item["file"])
        with Image.open(path) as image:
            if image.size != (WIDTH, HEIGHT):
                raise RuntimeError(f"unexpected image dimensions: {path.name}")
            copy = str(image.info.get("PortfolioCopy", ""))
            validate_public_copy(copy)
            if image.info.get("SourceFingerprint") != expected_fingerprint:
                raise RuntimeError(f"stale source fingerprint: {path.name}")
            if image.info.get("ValidationStatus") != "passed":
                raise RuntimeError(f"validation status missing: {path.name}")
            if hashlib.sha256(copy.encode()).hexdigest() != item.get("copy_sha256"):
                raise RuntimeError(f"public copy hash mismatch: {path.name}")
    print("portfolio images current and semantically valid")


def generate_images() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fingerprint = source_fingerprint()
    py = sys.executable
    artifacts: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="review-router-render-") as temp_root:
        previous_queue = os.environ.get("REVIEW_ROUTER_QUEUE_DIR")
        previous_runs = os.environ.get("REVIEW_ROUTER_RUN_DIR")
        os.environ["REVIEW_ROUTER_QUEUE_DIR"] = str(Path(temp_root) / "queue")
        os.environ["REVIEW_ROUTER_RUN_DIR"] = str(Path(temp_root) / "runs")
        try:
            client = TestClient(create_app())
            list_output = run([py, "-m", "review_router.cli", "list"], max_lines=8)
            validate_output = run(
                [py, "-m", "review_router.cli", "validate", "inbox-triage-router"],
                max_lines=6,
            )
            health = client.get("/health").json()

            lead_fixture = load_json("templates/lead-enrichment-router/fixtures/sample-input.json")
            lead_run = client.post(
                "/run",
                json={"template": "lead-enrichment-router", "fixture": lead_fixture},
            ).json()

            uncertain_fixture = {
                "subject": "Question about an existing request",
                "body": "Can an operator review this before it is routed?",
            }
            uncertain_run = client.post(
                "/run",
                json={"template": "inbox-triage-router", "fixture": uncertain_fixture},
            ).json()
            packet_id = str(uncertain_run["review_packet_id"])
            pending_path = (
                Path(os.environ["REVIEW_ROUTER_QUEUE_DIR"]) / "pending" / f"{packet_id}.json"
            )
            pending_record = json.loads(pending_path.read_text())
            run(
                [
                    py,
                    "-m",
                    "review_router.cli",
                    "queue",
                    "claim",
                    packet_id,
                    "--reviewer",
                    "operator-1",
                ],
                max_lines=9,
            )
            claimed_path = (
                Path(os.environ["REVIEW_ROUTER_QUEUE_DIR"]) / "claimed" / f"{packet_id}.json"
            )
            claimed_record = json.loads(claimed_path.read_text())
            run(
                [
                    py,
                    "-m",
                    "review_router.cli",
                    "queue",
                    "resolve",
                    packet_id,
                    "--reviewer",
                    "operator-1",
                    "--decision",
                    "support",
                    "--note",
                    "Route confirmed",
                ],
                max_lines=10,
            )
            resolved_path = (
                Path(os.environ["REVIEW_ROUTER_QUEUE_DIR"]) / "resolved" / f"{packet_id}.json"
            )
            resolved_record = json.loads(resolved_path.read_text())
            replay_output = run(
                [py, "-m", "review_router.cli", "replay", str(lead_run["run_id"])],
                max_lines=9,
            )

            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[0],
                    "Human review routing flow",
                    (
                        "Supplied classification metadata passes through deterministic policy "
                        "before any destination action."
                    ),
                    [
                        {
                            "box": (52, 154, 452, 670),
                            "title": "Supplied metadata",
                            "lines": [
                                "category",
                                "confidence",
                                "rationale",
                                "candidate routes",
                                "workflow context",
                                "Local fixtures use rule adapters",
                            ],
                        },
                        {
                            "box": (500, 154, 900, 670),
                            "title": "Policy layer",
                            "lines": [
                                "Validate typed contract",
                                "Apply confidence threshold",
                                "Evaluate signoff policy",
                                "Continue allowed routes",
                                "Pause uncertain routes",
                                "No model is loaded or called",
                            ],
                        },
                        {
                            "box": (948, 154, 1348, 670),
                            "title": "Controlled result",
                            "lines": [
                                "Destination route",
                                "Human review packet",
                                "Queue claim and resolution",
                                "Replayable run record",
                                "Operator handoff note",
                                "External action remains gated",
                            ],
                            "accent": SUCCESS,
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )
            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[1],
                    "Operator interfaces",
                    (
                        "CLI and FastAPI expose the same templates, policy checks, run records, "
                        "and queue controls."
                    ),
                    [
                        {
                            "box": (52, 154, 674, 670),
                            "title": "CLI readback",
                            "lines": [*list_output, "", *validate_output],
                            "code": True,
                        },
                        {
                            "box": (726, 154, 1348, 670),
                            "title": "Local API",
                            "lines": [
                                "GET /health",
                                "GET /templates",
                                "POST /validate",
                                "POST /run",
                                "GET /runs/{id}",
                                "POST /queue/resolve",
                                "",
                                *compact_json_lines(
                                    health,
                                    [
                                        "status",
                                        "fixture_safe",
                                        "live_services_used",
                                        "synthetic_data_only",
                                    ],
                                ),
                            ],
                            "code": True,
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )
            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[2],
                    "Deterministic policy processing",
                    (
                        "A committed rule adapter supplies classifier-shaped metadata for "
                        "repeatable local validation."
                    ),
                    [
                        {
                            "box": (52, 154, 674, 670),
                            "title": "Classifier-shaped input",
                            "lines": [
                                f"company={lead_fixture.get('company')}",
                                f"contact={lead_fixture.get('contact')}",
                                f"notes={lead_fixture.get('notes')}",
                                "",
                                *compact_json_lines(
                                    lead_run["mock_ai_output"],
                                    ["category", "confidence", "reason"],
                                ),
                                "adapter=deterministic local rules",
                                "model_call=false",
                            ],
                            "code": True,
                        },
                        {
                            "box": (726, 154, 1348, 670),
                            "title": "Policy result",
                            "lines": compact_json_lines(
                                lead_run,
                                [
                                    "routing_decision",
                                    "review_required",
                                    "destination",
                                    "candidate_routes",
                                    "recommended_next_action",
                                    "run_id",
                                ],
                            ),
                            "code": True,
                            "accent": SUCCESS,
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )
            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[3],
                    "Human-review guardrail",
                    (
                        "Low-confidence or signoff-required routes stop in a typed queue before "
                        "any external action."
                    ),
                    [
                        {
                            "box": (52, 154, 674, 670),
                            "title": "Policy stop",
                            "lines": [
                                f"subject={uncertain_fixture['subject']}",
                                *compact_json_lines(
                                    uncertain_run["mock_ai_output"],
                                    ["category", "confidence", "reason"],
                                ),
                                f"review_required={str(uncertain_run['review_required']).lower()}",
                                f"review_packet_id={packet_id}",
                                f"destination={uncertain_run['destination']}",
                            ],
                            "code": True,
                            "accent": ERROR,
                        },
                        {
                            "box": (726, 154, 1348, 670),
                            "title": "Queue readback",
                            "lines": compact_json_lines(
                                pending_record,
                                [
                                    "packet_id",
                                    "workflow_name",
                                    "reason_for_review",
                                    "review_context",
                                    "candidate_routes",
                                    "recommended_next_action",
                                    "status",
                                    "claimed_by",
                                ],
                            ),
                            "code": True,
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )
            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[4],
                    "Decision and replay readback",
                    (
                        "Operator ownership and deterministic replay remain inspectable after "
                        "the route is resolved."
                    ),
                    [
                        {
                            "box": (52, 154, 674, 670),
                            "title": "Claim and resolution",
                            "lines": [
                                "Claimed packet",
                                *compact_json_lines(
                                    claimed_record,
                                    ["packet_id", "status", "claimed_by", "queue"],
                                ),
                                "",
                                "Resolved packet",
                                *compact_json_lines(
                                    resolved_record,
                                    ["packet_id", "status", "claimed_by", "resolution"],
                                ),
                            ],
                            "code": True,
                            "accent": SUCCESS,
                        },
                        {
                            "box": (726, 154, 1348, 670),
                            "title": "Replay readback",
                            "lines": replay_output,
                            "code": True,
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )

            validation_lines: list[str] = []
            commands = [
                ([py, "-m", "pytest", "-q", "--disable-warnings"], 180),
                ([py, "-m", "ruff", "check", "."], 90),
                ([py, "-m", "mypy", "src"], 120),
                ([py, "scripts/template_validation_sweep.py"], 90),
                ([py, "scripts/public_readiness_check.py"], 90),
            ]
            for command, timeout in commands:
                validation_lines.extend(run(command, timeout=timeout, max_lines=2))
                validation_lines.append("")
            artifacts.append(
                render(
                    OUT / EXPECTED_IMAGES[5],
                    "Validation and operating scope",
                    (
                        "Automated checks pass locally while model calls, provider writes, and "
                        "customer data remain excluded."
                    ),
                    [
                        {
                            "box": (52, 154, 820, 670),
                            "title": "Core validation readback",
                            "lines": validation_lines,
                            "code": True,
                            "accent": SUCCESS,
                        },
                        {
                            "box": (872, 154, 1348, 670),
                            "title": "Scope and image checks",
                            "lines": [
                                "Image sequence: 6 current files",
                                "Semantic freshness: checked after render",
                                "Public copy scanner enabled",
                                "",
                                "Synthetic fixtures only",
                                "Deterministic rule adapters",
                                "No embedded model",
                                "No model-provider calls",
                                "No customer records",
                                "No live service credentials",
                                "No external destination writes",
                            ],
                        },
                    ],
                    fingerprint=fingerprint,
                )
            )
        finally:
            if previous_queue is None:
                os.environ.pop("REVIEW_ROUTER_QUEUE_DIR", None)
            else:
                os.environ["REVIEW_ROUTER_QUEUE_DIR"] = previous_queue
            if previous_runs is None:
                os.environ.pop("REVIEW_ROUTER_RUN_DIR", None)
            else:
                os.environ["REVIEW_ROUTER_RUN_DIR"] = previous_runs

    write_manifest(fingerprint, artifacts)
    check_images()
    print("portfolio images rendered")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_images()
    else:
        generate_images()


if __name__ == "__main__":
    main()
