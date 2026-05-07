from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
issues: list[str] = []

banned_patterns = [
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
    re.compile(r"PRIVATE KEY"),
    re.compile(r"api[_-]?key\s*[:=]\s*[A-Za-z0-9]"),
]

for rel in tracked:
    path = ROOT / rel
    if not path.is_file():
        continue
    text = path.read_text(errors="ignore")
    if rel != "scripts/public_readiness_check.py":
        for pattern in banned_patterns:
            if pattern.search(text):
                issues.append(f"{rel}: banned pattern {pattern.pattern}")
    if rel.endswith((".json", ".md", ".py")):
        if "fixture_safe" in text and "live_services_used" not in text:
            issues.append(f"{rel}: fixture_safe appears without live_services_used")

readme = (ROOT / "README.md").read_text()
for forbidden_link in ["docs/plans/", "artifacts/local/"]:
    if forbidden_link in readme:
        issues.append(f"README.md links to non-public/internal path {forbidden_link}")

report = {"ok": not issues, "issues": issues}
print(json.dumps(report, indent=2))
if issues:
    raise SystemExit(1)
