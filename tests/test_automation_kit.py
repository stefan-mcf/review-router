from __future__ import annotations

from review_router.automation_kit import automation_kit_status


def test_optional_automation_kit_import_guard() -> None:
    status = automation_kit_status()
    assert status["integration_mode"] in {"standalone", "optional-import"}
