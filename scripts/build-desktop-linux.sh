#!/usr/bin/env bash
# 构建 Linux 桌面可执行程序（PyInstaller onedir）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> [1/4] 构建前端"
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  npm install
fi
npm run build

echo "==> [2/4] 拷贝前端产物到后端资源目录"
rm -rf "$ROOT/backend/frontend_dist"
cp -r "$ROOT/frontend/dist" "$ROOT/backend/frontend_dist"

echo "==> [3/4] 安装打包依赖"
cd "$ROOT/backend"
python3 -m venv .venv-build
./.venv-build/bin/pip install --upgrade pip
./.venv-build/bin/pip install -r requirements-desktop.txt pyinstaller==6.11.1

echo "==> [4/4] PyInstaller 打包"
./.venv-build/bin/pyinstaller --noconfirm desktop.spec

echo
echo "完成！可执行程序位于：$ROOT/backend/dist/AssetManagement/AssetManagement"
echo "提示：Linux 运行需系统已安装 WebKitGTK，例如："
echo "  Ubuntu/Debian: sudo apt install libwebkit2gtk-4.1-0 libgtk-3-0"
