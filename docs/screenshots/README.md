# Portfolio images

The six images in this directory are generated from synthetic local scenarios after the CLI, API, runtime, template, lint, typing, and public-surface checks pass.

| File | Content |
|---|---|
| `01-system-flow.png` | Supplied metadata, deterministic policy, and controlled route flow. |
| `02-interface-surface.png` | Authentic CLI and FastAPI readback. |
| `03-core-processing.png` | Classifier-shaped local input and policy result. |
| `04-guardrail-path.png` | Low-confidence policy stop and file-backed queue packet. |
| `05-output-readback.png` | Queue ownership, decision resolution, and deterministic replay. |
| `06-validation-scope.png` | Current validation output and explicit operating boundary. |

Regenerate and check the set:

```bash
PYTHONPATH=src python scripts/generate_screenshots.py
PYTHONPATH=src python scripts/generate_screenshots.py --check
```

Boundary: `fixture_safe=true`, `live_services_used=false`, `model_calls=false`, `provider_writes=false`.
