# Review Router

Controlled AI workflow proof for n8n, Make, Zapier, and Python delivery work. This repo shows AI as one auditable workflow step, not a vague agent claim.

## What it proves

- controlled AI workflow template;
- deterministic mock AI output;
- manual review branch;
- n8n/Make/Zapier-style workflow mapping;
- tests and evidence package.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
```

## Safety boundary

Synthetic fixtures only. Empty credential placeholders only. No live OpenAI, Claude, n8n, Make, Zapier, cloud, payment, or delivery side effects by default. No Upwork action is performed.

## Evidence

- `docs/case-study.md`
- `docs/evidence.md`
- `docs/low-code-mapping.md`
- `docs/upwork-proposal-mapping.md`
- `examples/input/support-email.json`
- `examples/output/triage-result.json`
