# Low-Code Mapping Overview

Detailed per-platform docs:
- `docs/low-code/n8n.md`
- `docs/low-code/make.md`
- `docs/low-code/zapier.md`

Per-template credential boundary summary:

| Template | n8n | Make | Zapier | Review gate |
|---|---|---|---|---|
| lead-enrichment-router | Webhook -> Set -> AI placeholder -> Switch -> CRM/manual research | Webhook -> Tools -> Router | Trigger -> Formatter -> Paths | low-confidence enrichment |
| inbox-triage-router | Inbox trigger -> Switch | Email parser -> Router | Email trigger -> Paths | uncertain classification |
| support-urgency-sentiment | Ticket trigger -> urgency route | Ticket parser -> Router | Ticket trigger -> Paths | low-confidence escalation |
| content-rss-summarizer | RSS -> summarize -> publish/review | Feed -> Router | Feed trigger -> Paths | editorial review |
| creative-pack-review | brief -> manifest -> review | brief -> manifest -> review | brief -> manifest -> review | always required |
| workflow-debug-replay | log -> diagnose -> fix path | log -> diagnose -> router | log -> diagnose -> paths | human approves fix path |
