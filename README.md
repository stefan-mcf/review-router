# Review Router

Deterministic, auditable review-gated AI workflow templates for n8n, Make, Zapier, Python, and API-first automation delivery.

## What it includes

| Surface | What it proves |
|---|---|
| Typed workflow contract | Every workflow declares trigger, AI step, review gate, route, destination, and handoff boundaries. |
| Deterministic runner | Fixture-safe runs emit audit trails and replay with matching hashes. |
| Review queue | Uncertain or creative outputs stop at a file-backed manual review packet. |
| Template pack | Six client-shaped workflows cover lead routing, inbox triage, support escalation, content summarization, creative review, and workflow debugging. |
| CLI + API | Clean-checkout operator surfaces work without live credentials or external services. |
| Low-code mapping | n8n, Make, and Zapier mappings are documented with explicit credential boundary tables. |

## Safety boundary

Synthetic fixtures only. Empty credential placeholders only. No live external-service calls, customer data, cloud resources, public visibility changes, releases, or external sharing actions are part of this local proof. Public export, live external-service proof, credentials, and GitHub push/visibility changes remain human-gated.

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH=src python3.11 -m pytest -q
PYTHONPATH=src python3.11 -m review_router.cli list
```

## Evidence package

![Flow overview](docs/screenshots/01-flow-overview.png)
![CLI proof](docs/screenshots/02-cli-proof.png)
![API OpenAPI](docs/screenshots/03-api-openapi.png)
![Template output proof](docs/screenshots/04-template-output-proof.png)
![Review queue proof](docs/screenshots/05-review-queue-proof.png)
![Low-code mapping proof](docs/screenshots/06-low-code-mapping-proof.png)
![Quality gates](docs/screenshots/07-quality-gates.png)
![Safety boundary](docs/screenshots/08-safety-boundary.png)

## CLI reference

```bash
review-router list
review-router validate <template>
review-router run <template> --fixture <path>
review-router replay <run_id>
review-router queue list
review-router queue claim <packet_id> --reviewer stefan
review-router queue resolve <packet_id> --reviewer stefan --decision approve --note "Approved"
```

## API reference

```bash
GET  /health
GET  /templates
POST /validate
POST /run
GET  /runs/{id}
POST /queue/resolve
```

## Built on Automation Kit

Review Router is a thin spoke around Automation Kit vocabulary and safety rules while remaining fully standalone. See `docs/automation-kit-backbone.md`.

## Project docs

| Path | Purpose |
|---|---|
| `docs/architecture.md` | package boundaries, runtime flow, and credential boundary model |
| `docs/api.md` | local FastAPI integration surface |
| `docs/case-study.md` | client problem and proof-story framing |
| `docs/evidence.md` | reproducible verification commands and proof notes |
| `docs/sandbox-walkthrough.md` | end-to-end fixture-safe operator walkthrough |
| `docs/public-readiness-checklist.md` | public-surface checklist |
| `docs/automation-kit-backbone.md` | backbone relationship and optional integration path |
| `docs/low-code/` | n8n, Make, and Zapier mapping details |
| `docs/proposal-mapping.md` | capability-to-keyword fit and use-case positioning |

## Quality gates

```bash
bash scripts/verify.sh
```

## Environment

| Variable | Purpose |
|---|---|
| `REVIEW_ROUTER_ENABLE_LIVE_SERVICES` | remains empty for fixture-safe mode |
| `REVIEW_ROUTER_API_HOST` | local API host |
| `REVIEW_ROUTER_API_PORT` | local API port |
| `REVIEW_ROUTER_QUEUE_DIR` | local queue path |
| `REVIEW_ROUTER_RUN_DIR` | local run path |
| `N8N_API_KEY` | placeholder only |
| `MAKE_API_TOKEN` | placeholder only |
| `ZAPIER_WEBHOOK_SECRET` | placeholder only |
| `AIRTABLE_API_KEY` | placeholder only |
| `GOOGLE_SHEETS_CREDENTIALS_JSON` | placeholder only |

## Repository layout

```text
src/review_router/         package modules
templates/                 workflow templates, fixtures, expected outputs
scripts/                   verification and screenshot generation
artifacts/                 gitignored queue and run outputs created at runtime
docs/                      architecture, API, evidence, mappings, screenshots
tests/                     unit and integration tests
```

## License

MIT License. See LICENSE.
