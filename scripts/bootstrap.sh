#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
.venv/bin/pip install -r apps/backend/requirements-dev.txt -r services/data_pipeline/requirements.txt
npm install
