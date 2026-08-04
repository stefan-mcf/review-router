# Validation

Primary verification bundle:

```bash
bash scripts/verify.sh
```

Key interface commands:

```bash
PYTHONPATH=src python3.11 -m review_router.cli list
PYTHONPATH=src python3.11 -m review_router.cli validate inbox-triage-router
PYTHONPATH=src python3.11 -m review_router.cli run inbox-triage-router --fixture templates/inbox-triage-router/fixtures/sample-input.json
PYTHONPATH=src python3.11 -m review_router.cli run creative-pack-review --fixture templates/creative-pack-review/fixtures/sample-input.json
PYTHONPATH=src python3.11 -m review_router.cli queue list
```

Validated behavior:
- typed workflow contracts validate locally;
- deterministic runs emit audit trails and replay cleanly;
- uncertain or signoff-required outputs stop at a manual review packet;
- API and CLI surfaces remain fixture-safe;
- public-surface audit checks run before any human push or visibility gate;
- committed images carry a current semantic source fingerprint and passed validation status.
