from __future__ import annotations

import json

from review_router.runtime import build_runtime

runtime = build_runtime()
report = {name: runtime.validate_template(name) for name in runtime.registry.list_templates()}
print(json.dumps(report, indent=2))
if not all(item["valid"] for item in report.values()):
    raise SystemExit(1)
