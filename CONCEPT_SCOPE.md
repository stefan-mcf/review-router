# Review Router — Concept and Scope

Date: 2026-05-05
Repo: review-router
Visibility target: private proof repo

## Concept pitch

Concrete proof project for review-gated AI workflow jobs: controlled AI steps inside auditable workflows, with node mappings and deterministic local proof.

This project exists because Automation Kit is a reusable tool/framework, while Upwork clients respond faster to concrete proof of a specific business workflow. The repo should prove one thing clearly: I can add AI to workflows without making them fragile, unreviewable, or dependent on live credentials for the first proof.

## Mined Upwork demand addressed

## Upwork mining signals this project responds to

Source: /Users/stefan/upwork-memory-profile, May 2026 mining and strategy files.

- API integration: 751 jobs / 39% in the demand landscape; API/REST appears as connective tissue across the market.
- AI/LLM workflow work: 673 jobs / 35%, strongest when framed as controlled workflow steps rather than vague agent claims.
- n8n/Make/Zapier workflow work: 593 jobs / 31%; Zapier, Make.com, and n8n repeatedly appear in premium and quick-win shortlists.
- Google Sheets automation: 199 jobs / 10% with strong hourly bands; Sheets work is boring but high-trust and easy to close.
- Airtable build/automation: 273 jobs / 14%; Airtable + Make and Airtable + API requests recur in premium shortlists.
- Automation fix/debug: 119 jobs in the 168h mining report; excellent early-review target because clients are already in pain.
- GHL/HubSpot/CRM cluster: 279 jobs / 9.9% in the 168h mining report; high-volume wedge, even if average rates are lower.
- Slack/Discord bots: lower volume but high median niche; useful as an ops-notification proof asset.

Portfolio rule: each repo proves one client-shaped outcome. Automation Kit remains the reusable local proof framework for running and validating automation patterns; these companion repos show concrete project implementations that can be linked one at a time in Upwork proposals.

## Systems and workflows this repo should make visible

- n8n
- Make.com
- Zapier
- Claude/OpenAI-style LLMs
- Airtable
- Gmail/email inbox
- Slack
- CRM/webhooks

## Concrete proof flows

- Lead intake -> AI classify/enrich -> CRM/Airtable route
- Inbox message -> AI classify -> support/sales/manual-review queue
- RSS/content source -> AI summary -> Slack review queue

## Evidence target

A complete proof package should eventually include:

- sample input fixture;
- deterministic local run;
- structured output JSON/CSV/report;
- validation or audit log;
- client-readable handoff notes;
- README with problem, solution, proof, and safety boundary;
- screenshots of the strongest proof surface;
- tests or validators that prove repeatability.

## Proposal use

Best used when a job mentions any of these systems or patterns:

- n8n
- Make.com
- Zapier
- Claude/OpenAI-style LLMs
- Airtable
- Gmail/email inbox
- Slack
- CRM/webhooks

First milestone to suggest:

> Build one AI-assisted workflow template with sample input, controlled output, and a manual-review path before connecting live credentials.

## Relationship to Automation Kit

- Automation Kit remains the reusable pattern library and local validation framework.
- This repo is a client-shaped implementation/proof wrapper.
- If implementation proceeds, prefer reusing Automation Kit vocabulary: workflow contract, fixtures, mock adapters, validation result, audit log, and handoff note.
- Do not bloat Automation Kit with every vertical proof; use these companion repos to keep each portfolio link focused.

## Safety and scope boundaries

- Local/private proof repo by default.
- Synthetic fixtures only until explicit approval is given for real client data.
- Empty credential placeholders only.
- No live SaaS calls in the proof baseline.
- No Upwork submission, client message, or off-platform delivery action.
- No public repo visibility change without explicit approval.
- No cloud deployment, paid resource, or production-readiness claim in the initial proof sprint.
- Evidence should be deterministic: sample input, sample output, validation log, test output, and handoff notes.
