# n8n Mapping

Each template maps to the same control pattern:
- Webhook / Trigger
- Set or Code step for normalization
- upstream classifier placeholder step
- IF / Switch node for review gate and route split
- destination node or review queue persistence

Credential boundaries are placeholders only: `N8N_API_KEY` with workflow-read scope notes.
