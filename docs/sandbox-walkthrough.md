# Sandbox Walkthrough

1. List available templates.
2. Validate a template contract.
3. Run a fixture through the deterministic runtime.
4. Inspect the emitted audit log.
5. If review is required, claim and resolve the review packet.
6. Replay the run and confirm deterministic hash match.

Example flow:

```bash
PYTHONPATH=src python3.11 -m review_router.cli list
PYTHONPATH=src python3.11 -m review_router.cli validate inbox-triage-router
PYTHONPATH=src python3.11 -m review_router.cli run inbox-triage-router --fixture templates/inbox-triage-router/fixtures/sample-input.json
PYTHONPATH=src python3.11 -m review_router.cli replay <run_id>
```
