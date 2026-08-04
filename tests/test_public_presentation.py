from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image
from scripts import generate_screenshots

EXPECTED_IMAGES = [
    "01-system-flow.png",
    "02-interface-surface.png",
    "03-core-processing.png",
    "04-guardrail-path.png",
    "05-output-readback.png",
    "06-validation-scope.png",
]


def test_six_image_sequence_has_clean_semantic_metadata() -> None:
    paths = sorted(Path("docs/screenshots").glob("*.png"))
    assert [path.name for path in paths] == EXPECTED_IMAGES
    retired = ("pro" + "of", "evi" + "dence", "walk" + "through", "tuto" + "rial")
    for path in paths:
        with Image.open(path) as image:
            assert image.size == (1400, 800)
            copy = str(image.info["PortfolioCopy"])
            assert not any(term in copy.lower() for term in retired)
            assert "/" + "Users/" not in copy
            assert "/" + "home/" not in copy
            assert image.info["ValidationStatus"] == "passed"


def test_renderer_rejects_failed_commands() -> None:
    with pytest.raises(RuntimeError, match="command returned 9"):
        generate_screenshots.run([sys.executable, "-c", "raise SystemExit(9)"])
