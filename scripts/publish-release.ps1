# 一键推送到 GitHub 并打 tag，触发 Actions 构建 Windows/Linux 版本并发布 Release。
# 用法: .\scripts\publish-release.ps1 -Repo <owner/repo> [-Tag v1.0.0]
param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [string]$Tag = "v1.0.0"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) { throw "请先安装 GitHub CLI: https://cli.github.com/" }
gh auth status 2>$null
if ($LASTEXITCODE -ne 0) { throw "请先登录: gh auth login" }

# 仓库不存在则创建（私有）
$exists = $true
gh repo view $Repo 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { $exists = $false }
if (-not $exists) {
  Write-Host "==> 创建仓库 $Repo"
  gh repo create $Repo --private --source=. --remote=origin
}

if (-not (Test-Path ".git")) { git init -q }
git add .
git commit -m "feat: 资产出入库管理系统（领用人/归还/放置地点 + 桌面端与发布流水线）"
git branch -M main

git remote remove origin 2>$null
git remote add origin "https://github.com/$Repo.git"
git push -u origin main

git tag -d $Tag 2>$null
git tag $Tag
git push origin $Tag

Write-Host ""
Write-Host "==> 完成：已推送代码并创建 tag $Tag"
Write-Host "GitHub Actions 正在构建 Windows / Linux 版本并发布 Release："
Write-Host "  https://github.com/$Repo/actions"
Write-Host "发布完成后可在 $([char]0x25BC) 下载：https://github.com/$Repo/releases"
