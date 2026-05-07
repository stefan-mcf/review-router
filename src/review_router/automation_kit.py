from __future__ import annotations

from importlib.util import find_spec


def automation_kit_status() -> dict[str, object]:
    installed = find_spec("automation_kit") is not None
    return {
        "automation_kit_available": installed,
        "integration_mode": "optional-import" if installed else "standalone",
    }
