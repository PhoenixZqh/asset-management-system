#!/usr/bin/env bash
# 本地以桌面窗口方式运行（开发/调试用，不打包）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> 构建前端"
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  npm install
fi
npm run build

rm -rf "$ROOT/backend/frontend_dist"
cp -r "$ROOT/frontend/dist" "$ROOT/backend/frontend_dist"

echo "==> 准备运行环境"
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements-desktop.txt
fi

echo "==> 启动桌面窗口"
exec ./.venv/bin/python -m app.desktop
