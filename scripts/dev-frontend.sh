#!/usr/bin/env bash
# 本地开发：启动前端 Vite（需先启动后端）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then npm install; fi
exec npm run dev
