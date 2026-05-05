# Low-Code AI Workflows

n8n, Make, and Zapier-style AI workflow templates with safe mock AI steps, routing, manual review, and handoff proof.

## Role in the Automation Kit portfolio

Concrete proof project for low-code + AI jobs: controlled AI steps inside auditable workflows, with node mappings and deterministic local proof.

Automation Kit is the reusable local proof framework for running and validating automation patterns. This repo is a concrete client-shaped proof asset: it narrows the story to one Upwork job lane so proposals can link directly to the most relevant evidence.

## Client-facing promise

I can add AI to workflows without making them fragile, unreviewable, or dependent on live credentials for the first proof.

## Systems and workflows addressed

- n8n
- Make.com
- Zapier
- Claude/OpenAI-style LLMs
- Airtable
- Gmail/email inbox
- Slack
- CRM/webhooks

## Initial proof flows

- Lead intake -> AI classify/enrich -> CRM/Airtable route
- Inbox message -> AI classify -> support/sales/manual-review queue
- RSS/content source -> AI summary -> Slack review queue

## First milestone shape

Build one AI-assisted workflow template with sample input, controlled output, and a manual-review path before connecting live credentials.

## Current repo status

This repository currently contains concept, scope, and planning artifacts. The implementation baseline is intentionally local/private and synthetic-first.

## Included files

- `CONCEPT_SCOPE.md` — project concept, market fit, workflow scope, evidence target, and safety boundaries.
- `PLAN.md` — comprehensive tranched implementation plan.
- `.env.example` — empty credential placeholders for later local implementation.
- `.gitignore` — keeps secrets, build outputs, and local artifacts out of git.

## Safety baseline

## Safety and scope boundaries

- Local/private proof repo by default.
- Synthetic fixtures only until explicit approval is given for real client data.
- Empty credential placeholders only.
- No live SaaS calls in the proof baseline.
- No Upwork submission, client message, or off-platform delivery action.
- No public repo visibility change without explicit approval.
- No cloud deployment, paid resource, or production-readiness claim in the initial proof sprint.
- Evidence should be deterministic: sample input, sample output, validation log, test output, and handoff notes.
