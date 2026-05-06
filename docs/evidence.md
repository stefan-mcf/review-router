# Evidence

Verified locally with:

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
PYTHONPATH=src python -m mypy src
```

Evidence files:

- `examples/input/support-email.json`
- `examples/output/triage-result.json`
- `docs/low-code-mapping.md`
