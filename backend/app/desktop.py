"""桌面应用入口（Linux / Windows 通用）。

启动本地 Uvicorn 服务（托管 API + 已构建前端），再用 pywebview 打开原生窗口。
若无可用图形环境，则自动退回系统默认浏览器打开。
"""

from __future__ import annotations

import socket
import threading
import time
import urllib.request
import webbrowser

import uvicorn

from app.core.config import settings


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


def _open_window(url: str, server_thread: threading.Thread) -> None:
    # 强制使用 Qt 后端，避免依赖系统 WebView / GTK，便于跨平台打包
    import os

    os.environ.setdefault("PYWEBVIEW_GUI", "qt")
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
    except Exception:  # noqa: BLE001 - 无 GUI 时退回浏览器
        webbrowser.open(url)
        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass


def main() -> None:
    from app.main import app

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    _wait_until_ready(f"{base_url}/health")
    _open_window(base_url, server_thread)


if __name__ == "__main__":
    main()
