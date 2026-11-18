#!/usr/bin/env bash
# 一键推送到 GitHub 并打 tag，触发 Actions 构建 Windows/Linux 版本并发布 Release。
# 用法: ./scripts/publish-release.sh <owner/repo> [tag]
# 例:   ./scripts/publish-release.sh zhang/asset-management-system v1.0.0
set -euo pipefail

REPO="${1:-}"
TAG="${2:-v1.0.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "$REPO" ]; then
  echo "用法: $0 <owner/repo> [tag]"
  exit 1
fi

command -v gh >/dev/null || { echo "请先安装 GitHub CLI: https://cli.github.com/"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "请先登录: gh auth login"; exit 1; }

# 仓库不存在则创建（私有），已存在则直接使用
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  echo "==> 创建仓库 $REPO"
  gh repo create "$REPO" --private --source=. --remote=origin
fi

# 初始化并提交
if [ ! -d .git ]; then
  git init -q
fi
git add .
git commit -m "feat: 资产出入库管理系统（领用人/归还/放置地点 + 桌面端与发布流水线）" || echo "(无新增改动可提交)"
git branch -M main

# 关联 remote
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${REPO}.git"
git push -u origin main

# 打 tag 触发发布
git tag -d "$TAG" 2>/dev/null || true
git tag "$TAG"
git push origin "$TAG"

echo
echo "==> 完成：已推送代码并创建 tag $TAG"
echo "GitHub Actions 正在构建 Windows / Linux 版本并发布 Release："
echo "  https://github.com/${REPO}/actions"
echo "发布完成后可在以下地址下载：https://github.com/${REPO}/releases"
