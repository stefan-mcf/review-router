# Case study: deterministic policy before workflow action

Human Review Router addresses a common client problem: how to consume classifier output in a workflow without losing auditability or forcing an immediate destination action.

Implemented scenario families:
- lead enrichment routed toward CRM or manual research;
- inbox triage across support, sales, billing, and manual review;
- support severity routing with fixture-safe notification planning;
- RSS/content summarization into publish-vs-review decisions;
- optional creative-pack review boundary before ComfyUI-style generation;
- workflow debug/replay classification paired to automation repair work.

Why this matters:
- clients buying n8n, Make, Zapier, Airtable, and API integration work often need explicit confidence policies and human signoff;
- review gates and replayable audit logs reduce trust risk during the first delivery milestone;
- the repository consumes category, confidence, and rationale fields but does not load or call a model.
