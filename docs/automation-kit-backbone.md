# Built on Automation Kit

Review Router is a thin spoke around the Automation Kit backbone.

What Review Router reuses conceptually:
- fixture-safe workflow execution;
- deterministic mock adapters;
- audit-log and handoff-note vocabulary;
- explicit live-service boundaries.

What remains unique to Review Router:
- typed workflow contract with mandatory review-gate step;
- file-backed review queue implementation;
- low-code mapping tables for n8n, Make, and Zapier;
- client-shaped workflow templates and buyer-facing implementation copy.

Optional integration contract:
- if `automation_kit` is installed, Review Router can detect it and report optional integration status;
- if not installed, Review Router remains fully standalone.
