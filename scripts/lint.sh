#!/usr/bin/env bash
set -euo pipefail
.venv/bin/ruff check apps/backend services/data_pipeline
npm run lint
npx prettier --check .
