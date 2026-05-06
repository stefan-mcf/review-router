# Low-Code AI Workflows

n8n, Make, and Zapier-style AI workflow templates with safe mock AI steps, routing, manual review, and handoff proof.

## Role in the Automation Kit portfolio

Concrete proof project for low-code + AI jobs: controlled AI steps inside auditable workflows, with node mappings and deterministic local proof.

Automation Kit is the reusable local proof framework for running and validating automation patterns. This repo is a concrete client-shaped proof asset: it narrows the story to one Upwork job lane so proposals can link directly to the most relevant evidence.


## Current promotion status

Priority: Fourth.

Role: Controlled AI-in-workflow proof for n8n, Make, Zapier, Claude, and OpenAI jobs.

Rationale: High market coverage, but stronger after the core API and deterministic workflow proof are visible.


## Automation Kit usage-case contract

This repo exists to prove Automation Kit usage in one buyer-shaped workflow. It should stay thin: reusable runner logic belongs in `automation-kit`; this repo owns the case-study fixtures, workflow-specific wrapper, output evidence, and proposal-facing explanation.

Ready-to-link requirements:

- thin wrapper around Automation Kit rather than a duplicate framework;
- synthetic input fixtures and deterministic output examples;
- tests for the main flow and one failure or review path;
- case-study documentation with first milestone shape;
- screenshot or text evidence from one verified local run;
- empty credential placeholders only;
- no live SaaS, cloud, payment, or delivery side effects by default.

Until those requirements are met, keep this repo private and treat it as a scoped backlog proof project, not a portfolio link.

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
