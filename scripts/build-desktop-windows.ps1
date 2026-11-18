# 构建 Windows 桌面可执行程序（PyInstaller onedir）
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> [1/4] 构建前端"
Set-Location "$Root\frontend"
if (-not (Test-Path node_modules)) { npm install }
npm run build

Write-Host "==> [2/4] 拷贝前端产物到后端资源目录"
$dest = "$Root\backend\frontend_dist"
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
Copy-Item -Recurse "$Root\frontend\dist" $dest

Write-Host "==> [3/4] 安装打包依赖"
Set-Location "$Root\backend"
python -m venv .venv-build
& ".\.venv-build\Scripts\pip.exe" install --upgrade pip
& ".\.venv-build\Scripts\pip.exe" install -r requirements-desktop.txt pyinstaller==6.11.1

Write-Host "==> [4/4] PyInstaller 打包"
& ".\.venv-build\Scripts\pyinstaller.exe" --noconfirm desktop.spec

Write-Host ""
Write-Host "完成！可执行程序位于：$Root\backend\dist\AssetManagement\AssetManagement.exe"
