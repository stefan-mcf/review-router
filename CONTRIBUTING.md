# Contributing

This repository is optimized for fixture-safe, deterministic automation proofs.

Rules for contributions:
- keep synthetic fixtures only;
- do not add live credentials or customer data;
- preserve `fixture_safe: true`, `live_services_used: false`, and `synthetic_data_only: true` semantics;
- add or update tests for behavior changes;
- run `bash scripts/verify.sh` before opening a pull request.
