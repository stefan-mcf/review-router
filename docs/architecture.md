# Architecture

Review Router models a workflow as a strict chain of typed steps:

1. trigger
2. transform
3. classifier-output adapter (deterministic local rules)
4. review gate
5. route
6. destination
7. handoff

Core modules:
- `review_router.models`: typed workflow contract.
- `review_router.validator`: contract enforcement and readable validation reports.
- `review_router.review_queue`: file-backed queue implementation.
- `review_router.runtime`: registry, runner, audit logs, replay.
- `review_router.cli`: local operator surface.
- `review_router.api`: fixture-safe FastAPI integration surface.

Run lifecycle:
- load template from `templates/<name>/workflow.json`
- validate schema + boundaries
- derive classifier-shaped metadata through deterministic local rules
- route low-confidence outcomes into the review queue
- write `artifacts/local/runs/<run_id>/audit-log.json`
- replay the same fixture to confirm matching result hashes

The local adapter exists only to make policy behavior reproducible. It does not load, host, train, or call an AI model. Production use supplies category, confidence, and rationale from an approved upstream classifier.

Credential boundary model:
- every step declares low-code or API credential boundaries;
- all boundaries are placeholders only;
- no boundary enables live traffic by default.
