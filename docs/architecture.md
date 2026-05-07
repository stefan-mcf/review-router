# Architecture

Review Router models a workflow as a strict chain of typed steps:

1. trigger
2. transform
3. AI step (deterministic mock)
4. review gate
5. route
6. destination
7. handoff

Core modules:
- `review_router.models`: typed workflow contract.
- `review_router.validator`: contract enforcement and readable validation reports.
- `review_router.review_queue`: file-backed queue proof implementation.
- `review_router.runtime`: registry, runner, audit logs, replay.
- `review_router.cli`: local operator surface.
- `review_router.api`: fixture-safe FastAPI integration surface.

Run lifecycle:
- load template from `templates/<name>/workflow.json`
- validate schema + boundaries
- execute deterministic mock step logic
- route low-confidence outcomes into the review queue
- write `artifacts/local/runs/<run_id>/audit-log.json`
- replay the same fixture to confirm matching result hashes

Credential boundary model:
- every step declares low-code or API credential boundaries;
- all boundaries are placeholders only;
- no boundary enables live traffic by default.
