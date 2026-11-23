# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置，Linux / Windows 通用。

在 backend/ 目录下执行：
    pyinstaller --noconfirm desktop.spec
产物位于 backend/dist/AssetManagement/。

诊断打包时（需要看启动报错）可设：
    AMS_DESKTOP_CONSOLE=1 pyinstaller --noconfirm desktop.spec
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

hiddenimports = collect_submodules("uvicorn")
hiddenimports += [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
    "sqlalchemy.dialects.sqlite",
    "pydantic_settings",
    # pywebview / Qt（Linux 主后端；Windows 作 WebView2 失败时的回退）
    "webview",
    "qtpy",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "PyQt5.QtWebEngineWidgets",
    "PyQt5.QtWebEngineCore",
    # Windows WebView2（edgechromium）常用依赖
    "clr_loader",
    "pythonnet",
]

# 收集 webview + PyQt5 的静态资源与二进制（缺 WebEngine/qwindows 会导致白屏）
datas = [("frontend_dist", "frontend_dist")]
binaries = []
for pkg in ("webview", "PyQt5"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    except Exception:  # noqa: BLE001 - 环境未装该包时跳过
        continue
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

# 默认无控制台；设 AMS_DESKTOP_CONSOLE=1 便于排查启动失败
console = os.environ.get("AMS_DESKTOP_CONSOLE", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

a = Analysis(
    ["app/desktop.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PySide2", "PySide6"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AssetManagement",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AssetManagement",
)
