# API Reference

Local fixture-safe FastAPI app:

- `GET /health`
- `GET /templates`
- `POST /validate`
- `POST /run`
- `GET /runs/{id}`
- `POST /queue/resolve`

All responses include:
- `fixture_safe: true`
- `live_services_used: false`
- `synthetic_data_only: true`

Local launch:

```bash
PYTHONPATH=src python3.11 -c "from review_router.api import create_app; import uvicorn; uvicorn.run(create_app(), host='127.0.0.1', port=8000)"
```
