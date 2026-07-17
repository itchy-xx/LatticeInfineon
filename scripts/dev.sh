#!/usr/bin/env bash
set -euo pipefail
trap 'kill 0' EXIT
(cd apps/backend && ../../.venv/bin/uvicorn app.main:app --reload) &
npm run dev &
wait
