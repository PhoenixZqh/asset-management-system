# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置，Linux / Windows 通用。

在 backend/ 目录下执行：
    pyinstaller --noconfirm desktop.spec
产物位于 backend/dist/AssetManagement/。
"""

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
    # pywebview Qt 后端
    "webview",
    "qtpy",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "PyQt5.QtWebEngineWidgets",
    "PyQt5.QtWebEngineCore",
]

# 收集 webview 的静态资源（含其注入脚本）
datas = [("frontend_dist", "frontend_dist")]
binaries = []
wv_datas, wv_binaries, wv_hidden = collect_all("webview")
datas += wv_datas
binaries += wv_binaries
hiddenimports += wv_hidden

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
    console=False,
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
