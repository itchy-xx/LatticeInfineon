# Lattice — Infineon Supply Chain Visibility

Lattice is a read-only foundation for visibility across Infineon and partner supply chains. It normalizes partner data into shared contracts and exposes shipment, production, hand-off, and exception visibility without replacing source systems.

> No proprietary data is included. Everything in `data/mock/` is synthetic mock data.

## Architecture

- React, TypeScript and Vite frontend with a typed API client
- FastAPI, Pydantic, SQLAlchemy and PostgreSQL backend
- Pandas ingestion with isolated source mappings and validation
- OpenAPI/JSON Schema language-neutral shared contracts
- Pytest, Vitest, Docker Compose and GitHub Actions

The proposal's living-map, event reasoning, freshness/confidence and notification concepts are represented as extension seams. Graph/AI/optimization logic is intentionally deferred until real data and rules are known.

## Structure

```text
apps/frontend/           React dashboard shell
apps/backend/            FastAPI and database access
services/data_pipeline/  Ingestion, mapping, validation and processing
packages/contracts/      Shared OpenAPI and JSON Schema contracts
data/mock/               Synthetic fixtures only
config/                  Non-secret configuration
docs/                    Architecture, API and integration guidance
infrastructure/          Deployment placeholders
migrations/              Alembic migration location
scripts/                 Developer commands
tests/integration/       Cross-service tests
```

## Run locally

With Docker Desktop:

```bash
cp .env.example .env
docker compose up --build
```

The local-only `.env` is ignored. Open the UI at `http://localhost:5173`, API docs at `http://localhost:8000/docs`, and health check at `http://localhost:8000/api/v1/health`.

Without Docker (Node 20+, Python 3.12+):

```bash
./scripts/bootstrap.sh
./scripts/dev.sh
```

Run checks with `./scripts/test.sh` and `./scripts/lint.sh`. To run independently, use `cd apps/backend && uvicorn app.main:app --reload` and `cd apps/frontend && npm run dev` in separate terminals.

## Environment and data safety

Root and service `.env.example` files document variables. Never commit `.env`, secrets, credentials, partner files, production URLs, or proprietary data. `VITE_*` values are visible in the browser and must never contain secrets.

Temporary synthetic fixtures belong in `data/mock/` and must use `.mock.` filenames and `mock-` IDs. Real files must stay outside Git in an approved secure location.

## Integrating tomorrow's data

1. Profile files securely and record owners, cadence, sensitivity and source-of-record precedence.
2. Update `packages/contracts/` with confirmed canonical concepts.
3. Add a read-only adapter in `services/data_pipeline/src/data_pipeline/ingestion/`.
4. Put raw-column mappings only in `services/data_pipeline/src/data_pipeline/mappings/`.
5. Add validation and transformation tests using synthetic/anonymized fixtures.
6. Update backend models/repositories and create an Alembic migration.
7. Update frontend contract types, labels and API behavior.
8. Configure credentials through the approved secret manager and run all checks.

See `docs/data-integration-checklist.md` and `docs/architecture/overview.md`.
