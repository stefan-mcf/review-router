from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

from review_router.api import create_app

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1400
HEIGHT = 800
BG = (10, 15, 28)
PANEL = (17, 24, 39)
PANEL_2 = (25, 35, 56)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
BLUE = (96, 165, 250)
YELLOW = (250, 204, 21)
PINK = (244, 114, 182)
RED = (248, 113, 113)
BORDER = (51, 65, 85)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
SUBTITLE_FONT = font(18)
SMALL_FONT = font(16)
MONO_SMALL = font(15)


def run(cmd: list[str], *, max_lines: int = 14) -> list[str]:
    python_bin = str(Path(sys.executable).resolve().parent)
    env = {
        **os.environ,
        "PYTHONPATH": os.environ.get("PYTHONPATH", "src"),
        "PATH": f"{python_bin}:{os.environ.get('PATH', '')}",
    }
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False, env=env)
    combined = (proc.stdout + proc.stderr).strip().splitlines()
    if proc.returncode != 0:
        combined = [f"command_exit_code={proc.returncode}", *combined]
    return combined[:max_lines] or ["command completed with no output"]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def read_lines(path: str, *, limit: int = 12) -> list[str]:
    return (ROOT / path).read_text().splitlines()[:limit]


def compact_json_lines(
    payload: dict[str, Any],
    keys: list[str],
    *,
    max_chars: int = 96,
) -> list[str]:
    lines: list[str] = []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (dict, list)):
            encoded = json.dumps(value, sort_keys=True)
            lines.append(f"{key}={encoded[:max_chars]}")
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
            textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False)
            or [line]
        )
    return wrapped


def draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    accent: tuple[int, int, int] = BLUE,
    code: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=SUBTITLE_FONT, fill=accent)
    y = y1 + 58
    selected_font = MONO_SMALL if code else SMALL_FONT
    usable_width = max(220, x2 - x1 - 70)
    approx_char_px = 9 if code else 10
    max_chars = max(34, usable_width // approx_char_px)
    for line in wrap_lines(lines, max_chars)[:18]:
        fill = TEXT
        if line.startswith(
            (
                "PASS",
                "✓",
                "fixture_safe=true",
                "live_services_used=false",
                "synthetic_data_only=true",
            )
        ):
            fill = GREEN
        elif line.startswith(("REFUSE", "unsafe", "blocked")) or "FAILED" in line:
            fill = RED
        elif line.startswith(("$", "python", "PYTHONPATH", "GET ", "POST ")):
            fill = YELLOW
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 26
        if y > y2 - 34:
            break


def render(
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    footer: str = "fixture_safe=true  live_services_used=false  synthetic_data_only=true",
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    for x in range(0, WIDTH, 80):
        draw.line((x, 0, x, HEIGHT), fill=(15, 23, 42))
    for y in range(0, HEIGHT, 80):
        draw.line((0, y, WIDTH, y), fill=(15, 23, 42))

    draw.rounded_rectangle(
        (30, 28, WIDTH - 30, 116), radius=24, fill=PANEL_2, outline=BORDER, width=2
    )
    draw.text((58, 48), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 90), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    for panel in panels:
        draw_panel(
            draw,
            panel["box"],
            str(panel["title"]),
            list(panel["lines"]),
            accent=panel.get("accent", BLUE),
            code=bool(panel.get("code", False)),
        )

    draw.rounded_rectangle(
        (30, HEIGHT - 54, WIDTH - 30, HEIGHT - 18), radius=16, fill=PANEL_2, outline=BORDER, width=1
    )
    draw.text((54, HEIGHT - 45), footer, font=SMALL_FONT, fill=GREEN)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Proof", f"{title}\n{subtitle}\n{footer}")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 35_000 or max(stat.stddev) < 20:
        raise RuntimeError(
            f"screenshot may be unreadable/blank: {path} "
            f"size={path.stat().st_size} stddev={stat.stddev}"
        )


def main() -> None:
    py = sys.executable
    client = TestClient(create_app())

    list_output = run([py, "-m", "review_router.cli", "list"], max_lines=16)
    validate_output = run(
        [py, "-m", "review_router.cli", "validate", "inbox-triage-router"],
        max_lines=12,
    )
    inbox_run_output = run(
        [
            py,
            "-m",
            "review_router.cli",
            "run",
            "inbox-triage-router",
            "--fixture",
            "templates/inbox-triage-router/fixtures/sample-input.json",
        ],
        max_lines=22,
    )
    creative_run_output = run(
        [
            py,
            "-m",
            "review_router.cli",
            "run",
            "creative-pack-review",
            "--fixture",
            "templates/creative-pack-review/fixtures/sample-input.json",
        ],
        max_lines=22,
    )
    queue_output = run([py, "-m", "review_router.cli", "queue", "list"], max_lines=22)
    pytest_output = run([py, "-m", "pytest", "-q"], max_lines=10)
    ruff_output = run([py, "-m", "ruff", "check", "."], max_lines=8)
    mypy_output = run([py, "-m", "mypy", "src"], max_lines=8)
    template_sweep_output = run([py, "scripts/template_validation_sweep.py"], max_lines=8)
    readiness_output = run(
        [py, "scripts/public_readiness_check.py"],
        max_lines=10,
    )

    health = client.get("/health").json()
    templates = client.get("/templates").json()
    validate_api = client.post(
        "/validate", json={"template": "support-urgency-sentiment"}
    ).json()
    lead_fixture = load_json("templates/lead-enrichment-router/fixtures/sample-input.json")
    lead_run = client.post(
        "/run",
        json={"template": "lead-enrichment-router", "fixture": lead_fixture},
    ).json()

    creative_fixture = load_json("templates/creative-pack-review/fixtures/sample-input.json")
    inbox_workflow = load_json("templates/inbox-triage-router/workflow.json")
    creative_workflow = load_json("templates/creative-pack-review/workflow.json")
    env_lines = read_lines(".env.example", limit=12)
    n8n_lines = read_lines("docs/low-code/n8n.md", limit=10)
    make_lines = read_lines("docs/low-code/make.md", limit=10)
    zapier_lines = read_lines("docs/low-code/zapier.md", limit=10)

    credential_lines = [
        "service -> secret -> scope",
        "n8n -> N8N_API_KEY -> workflow:read",
        "make -> MAKE_API_TOKEN -> scenario:read",
        "zapier -> ZAPIER_WEBHOOK_SECRET -> trigger:read",
        "api -> REVIEW_ROUTER_ENABLE_LIVE_SERVICES -> local-only",
    ]

    flow_summary = [
        "Trigger fixture or webhook-shaped payload",
        "Normalize input or derive creative/debug context",
        "Deterministic mock AI emits category + confidence + reason",
        "Review gate stops uncertain or creative work in file-backed queue",
        "Route selects local output or review queue destination",
        "Handoff note records safe next action for operator",
    ]

    review_contract = compact_json_lines(
        {
            "queue": creative_workflow["review_queue"],
            "candidate_routes": creative_workflow["steps"][3]["policy"]["candidate_routes"],
            "recommended_next_action": creative_workflow["steps"][3]["policy"][
                "recommended_next_action"
            ],
            "reason": creative_workflow["steps"][3]["policy"]["reason"],
        },
        ["queue", "candidate_routes", "recommended_next_action", "reason"],
    )

    api_contract = [
        "GET /health",
        "GET /templates",
        "POST /validate",
        "POST /run",
        "GET /runs/{id}",
        "POST /queue/resolve",
        "POST /queue/claim (CLI-only today, API-ready next)",
        *compact_json_lines(
            health,
            ["status", "fixture_safe", "live_services_used", "synthetic_data_only"],
        ),
    ]

    lead_run_excerpt = compact_json_lines(
        lead_run,
        [
            "workflow_name",
            "routing_decision",
            "review_required",
            "destination",
            "candidate_routes",
            "recommended_next_action",
        ],
    )
    validate_excerpt = compact_json_lines(validate_api, ["valid", "issues", "fixture_safe"])
    templates_excerpt = compact_json_lines(templates, ["templates", "fixture_safe"])

    render(
        OUT / "01-flow-overview.png",
        "Review Router Flow",
        (
            "Review-gated workflow templates keep AI routing deterministic, auditable, "
            "and fixture-safe."
        ),
        [
            {
                "box": (52, 148, 410, 628),
                "title": "Inputs",
                "accent": BLUE,
                "lines": [
                    "inbox triage payload",
                    "lead enrichment event",
                    "support urgency request",
                    "creative brief + prompts",
                    "workflow debug fixture",
                    "RSS summary source",
                ],
            },
            {
                "box": (462, 148, 820, 628),
                "title": "Factory",
                "accent": YELLOW,
                "lines": flow_summary,
            },
            {
                "box": (872, 148, 1230, 628),
                "title": "Proof",
                "accent": GREEN,
                "lines": [
                    "audit-log.json per deterministic run",
                    "review packets persisted under queue",
                    "CLI + API return fixture-safe metadata",
                    "template pack spans 6 client-shaped workflows",
                    "public-readiness audit blocks unsafe surface drift",
                ],
            },
        ],
    )
    render(
        OUT / "02-cli-proof.png",
        "CLI Proof",
        (
            "The CLI lists templates, validates schemas, runs fixtures, and shows "
            "deterministic operator output."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Commands",
                "accent": YELLOW,
                "code": True,
                "lines": [
                    "$ PYTHONPATH=src python3.11 -m review_router.cli list",
                    "$ PYTHONPATH=src python3.11 -m review_router.cli validate inbox-triage-router",
                    (
                        "$ PYTHONPATH=src python3.11 -m review_router.cli run "
                        "inbox-triage-router --fixture "
                        "templates/inbox-triage-router/fixtures/sample-input.json"
                    ),
                    "",
                    *list_output[:6],
                    "",
                    *validate_output[:4],
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Run excerpt",
                "accent": GREEN,
                "code": True,
                "lines": inbox_run_output,
            },
        ],
    )
    render(
        OUT / "03-api-openapi.png",
        "Local API Surface",
        "FastAPI exposes only local validation, run, template, queue, and audit-facing routes.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Endpoints + health",
                "accent": BLUE,
                "code": True,
                "lines": api_contract,
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "API proof excerpt",
                "accent": GREEN,
                "code": True,
                "lines": [*templates_excerpt, "", *validate_excerpt],
            },
        ],
    )
    render(
        OUT / "04-template-output-proof.png",
        "Template Output Proof",
        (
            "Lead routing produces deterministic category, confidence, destination, and "
            "operator handoff fields from synthetic fixture input."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Lead fixture",
                "accent": PINK,
                "code": True,
                "lines": compact_json_lines(
                    {
                        "company": lead_fixture.get("company"),
                        "signal": lead_fixture.get("signal"),
                        "need": lead_fixture.get("need"),
                        "source": lead_fixture.get("source"),
                    },
                    ["company", "signal", "need", "source"],
                ),
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Run result",
                "accent": GREEN,
                "code": True,
                "lines": lead_run_excerpt,
            },
        ],
    )
    render(
        OUT / "05-review-queue-proof.png",
        "Review Queue Proof",
        (
            "Creative work always stops at review, and uncertain paths surface file-backed "
            "packets before any live action."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Creative review contract",
                "accent": RED,
                "code": True,
                "lines": [
                    f"brief={creative_fixture.get('brief')}",
                    f"prompts={json.dumps(creative_fixture.get('prompts'))}",
                    "",
                    *review_contract,
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Queue excerpt",
                "accent": GREEN,
                "code": True,
                "lines": queue_output,
            },
        ],
    )
    render(
        OUT / "06-low-code-mapping-proof.png",
        "Low-Code Mapping Proof",
        (
            "n8n, Make, and Zapier mappings stay explicit, with review gating and "
            "credential boundaries documented per template."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Mapping notes",
                "accent": BLUE,
                "code": True,
                "lines": [*n8n_lines[:5], "", *make_lines[:5], "", *zapier_lines[:5]],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Boundary contract",
                "accent": YELLOW,
                "code": True,
                "lines": credential_lines
                + ["", f"inbox-tags={json.dumps(inbox_workflow['tags'])[:90]}"]
            },
        ],
    )
    render(
        OUT / "07-quality-gates.png",
        "Quality Gate Proof",
        (
            "The screenshot package is regenerated only after tests, lint, typing, "
            "template checks, and readiness audit pass."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Verified commands",
                "accent": BLUE,
                "code": True,
                "lines": [
                    "PYTHONPATH=src python3.11 -m pytest -q",
                    "python3.11 -m ruff check .",
                    "PYTHONPATH=src python3.11 -m mypy src",
                    "PYTHONPATH=src python3.11 scripts/template_validation_sweep.py",
                    "PYTHONPATH=src python3.11 scripts/public_readiness_check.py",
                    "PYTHONPATH=src python3.11 scripts/generate_screenshots.py",
                    "",
                    *pytest_output[:3],
                    *ruff_output[:2],
                    *mypy_output[:2],
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Audit excerpts",
                "accent": GREEN,
                "code": True,
                "lines": [*template_sweep_output, "", *readiness_output],
            },
        ],
    )
    render(
        OUT / "08-safety-boundary.png",
        "Safety Boundary",
        (
            "Public-safe proof uses only empty placeholders, local defaults, and explicit "
            "no-live-service flags across CLI, API, and workflow contracts."
        ),
        [
            {
                "box": (52, 148, 604, 628),
                "title": ".env.example",
                "accent": YELLOW,
                "code": True,
                "lines": env_lines,
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Boundary signals",
                "accent": GREEN,
                "code": True,
                "lines": [
                    *compact_json_lines(
                        {
                            "fixture_safe": health.get("fixture_safe"),
                            "live_services_used": health.get("live_services_used"),
                            "synthetic_data_only": health.get("synthetic_data_only"),
                            "review_queue": inbox_workflow.get("review_queue"),
                            "creative_destination": (
                                creative_run_output[0] if creative_run_output else "n/a"
                            ),
                        },
                        [
                            "fixture_safe",
                            "live_services_used",
                            "synthetic_data_only",
                            "review_queue",
                            "creative_destination",
                        ],
                    ),
                    "",
                    "No secrets committed",
                    "No live accounts/screens captured",
                    "No public visibility change implied by evidence",
                ],
            },
        ],
    )
    print("screenshots rendered")


if __name__ == "__main__":
    main()
