"""桌面应用入口（Linux / Windows 通用）。

启动本地 Uvicorn 服务（托管 API + 已构建前端），再用 pywebview 打开原生窗口。
若无可用图形环境，则自动退回系统默认浏览器打开。
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

import uvicorn

from app.core.config import settings


def _ensure_stdio() -> None:
    """无控制台环境（PyInstaller console=False / pythonw）下补齐 stdio。

    此时 sys.stdout / sys.stderr 为 None，uvicorn ColourizedFormatter 调用
    isatty() 会直接崩溃。按 PyInstaller 官方建议重定向到 os.devnull。
    """
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")  # noqa: SIM115


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_ready(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except Exception:  # noqa: BLE001 - 启动阶段忽略连接错误
            time.sleep(0.2)
    raise RuntimeError("本地服务启动超时")


def _configure_webview_gui() -> None:
    """按平台选择 pywebview 后端。

    Windows 优先系统 WebView2（edgechromium），不要强制 Qt：
    强制 Qt 时必须完整打进 WebEngine，否则常见白屏/起不来且 console=False 时无报错。
    Linux/macOS 仍用 Qt，便于与打包脚本一致、少依赖系统 WebKit。
    """
    if sys.platform.startswith("win"):
        # 不强制 Qt；已设置的 PYWEBVIEW_GUI 仍尊重，便于本机排障
        return
    os.environ.setdefault("PYWEBVIEW_GUI", "qt")


def _log_gui_fallback(exc: BaseException) -> None:
    """GUI 失败时写日志，避免打包后 console=False 完全吞掉错误。"""
    from pathlib import Path

    from app.core.config import DATA_DIR

    try:
        log_path = Path(DATA_DIR) / "desktop-gui-fallback.log"
        log_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def _open_window(url: str, server_thread: threading.Thread) -> None:
    _configure_webview_gui()
    try:
        import webview

        webview.create_window(
            settings.app_name,
            url,
            width=1280,
            height=820,
            min_size=(1024, 680),
        )
        webview.start()
    except Exception as exc:  # noqa: BLE001 - 无 GUI 时退回浏览器
        _log_gui_fallback(exc)
        webbrowser.open(url)
        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass


def main() -> None:
    _ensure_stdio()
    from app.main import app

    port = _free_port()
    # use_colors=False：避免无 TTY / None stdio 时 ColourizedFormatter 再踩 isatty
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        use_colors=False,
    )
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    _wait_until_ready(f"{base_url}/health")
    _open_window(base_url, server_thread)


if __name__ == "__main__":
    main()
