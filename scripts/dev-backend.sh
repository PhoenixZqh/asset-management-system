#!/usr/bin/env bash
# 启动后端（FastAPI + Uvicorn），默认监听 127.0.0.1:8010
set -euo pipefail
cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements.txt
fi

exec ./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
