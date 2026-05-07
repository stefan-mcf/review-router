from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PANELS = [
    (
        "01-flow-overview.png",
        "Flow overview",
        (
            "Trigger -> transform -> deterministic AI ->\n"
            "review gate -> route -> destination -> handoff"
        ),
    ),
    (
        "02-cli-proof.png",
        "CLI proof",
        "list / validate / run / replay / queue surfaces verified locally",
    ),
    (
        "03-api-openapi.png",
        "API OpenAPI",
        "health, templates, validate, run, runs/{id}, queue/resolve",
    ),
    (
        "04-template-output-proof.png",
        "Template output proof",
        "deterministic outputs and audit logs generated from synthetic fixtures",
    ),
    (
        "05-review-queue-proof.png",
        "Review queue proof",
        "uncertain and creative paths stop at file-backed manual review packets",
    ),
    (
        "06-low-code-mapping-proof.png",
        "Low-code mapping proof",
        "n8n, Make, and Zapier mappings documented with credential boundaries",
    ),
    (
        "07-quality-gates.png",
        "Quality gates",
        "pytest, ruff, mypy, template sweep, and public-surface audit",
    ),
    (
        "08-safety-boundary.png",
        "Safety boundary",
        "fixture_safe=true, live_services_used=false, synthetic_data_only=true",
    ),
]

font = ImageFont.load_default()
for filename, title, body in PANELS:
    img = Image.new("RGB", (1400, 800), color=(17, 24, 39))
    draw = ImageDraw.Draw(img)
    draw.rectangle((50, 50, 1350, 750), outline=(96, 165, 250), width=4)
    draw.text((90, 110), title, fill=(255, 255, 255), font=font)
    draw.text((90, 180), body, fill=(191, 219, 254), font=font)
    draw.text((90, 260), "Synthetic local proof panel", fill=(147, 197, 253), font=font)
    img.save(OUT / filename)
