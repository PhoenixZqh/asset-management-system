"""Windows 兼容性相关的可本地复现断言（无需真实 Windows）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path, PureWindowsPath
from unittest import mock

from sqlalchemy.engine.url import make_url


def test_sqlite_url_uses_posix_slashes() -> None:
    from app.core.config import _sqlite_url

    url = _sqlite_url(Path("/tmp/fake") / "asset_management.db")
    assert "\\" not in url
    assert url.startswith("sqlite:///")
    assert make_url(url).drivername == "sqlite"

    # 旧写法 Path 进 f-string 在 Windows 会留下反斜杠；as_posix 可消除
    win_db = PureWindowsPath(r"C:\Users\demo\AppData\Roaming\AssetManagement\asset_management.db")
    legacy = f"sqlite:///{win_db}"
    fixed = f"sqlite:///{win_db.as_posix()}"
    assert "\\" in legacy
    assert "\\" not in fixed
    parsed = make_url(fixed)
    assert parsed.drivername == "sqlite"
    assert "Users/demo" in (parsed.database or "").replace("\\", "/")


def test_configure_webview_gui_skips_force_qt_on_windows() -> None:
    from app import desktop

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("PYWEBVIEW_GUI", None)
        with mock.patch("sys.platform", "win32"):
            desktop._configure_webview_gui()
        assert "PYWEBVIEW_GUI" not in os.environ


def test_configure_webview_gui_sets_qt_on_linux() -> None:
    from app import desktop

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("PYWEBVIEW_GUI", None)
        with mock.patch("sys.platform", "linux"):
            desktop._configure_webview_gui()
        assert os.environ.get("PYWEBVIEW_GUI") == "qt"
        # 清理，避免污染后续用例
        os.environ.pop("PYWEBVIEW_GUI", None)


def test_desktop_spec_collects_pyqt5_and_console_flag() -> None:
    spec = Path(__file__).resolve().parents[1] / "desktop.spec"
    text = spec.read_text(encoding="utf-8")
    assert 'collect_all(pkg)' in text or 'collect_all("PyQt5")' in text
    assert "AMS_DESKTOP_CONSOLE" in text
    assert "pythonnet" in text


def test_ensure_stdio_for_windowed_mode() -> None:
    """PyInstaller console=False / pythonw 下 stdout/stderr 为 None，须先补上。"""
    from app import desktop

    real_out, real_err = sys.stdout, sys.stderr
    try:
        sys.stdout = None  # type: ignore[assignment]
        sys.stderr = None  # type: ignore[assignment]
        desktop._ensure_stdio()
        assert sys.stdout is not None
        assert sys.stderr is not None
        assert hasattr(sys.stdout, "isatty")
        assert hasattr(sys.stderr, "isatty")
        assert sys.stdout.isatty() is False
        assert sys.stderr.isatty() is False
    finally:
        sys.stdout, sys.stderr = real_out, real_err


def test_uvicorn_config_survives_none_stdio() -> None:
    """无控制台时 uvicorn.Config 不得因 ColourizedFormatter.isatty 崩溃。"""
    import uvicorn

    from app import desktop

    real_out, real_err = sys.stdout, sys.stderr
    try:
        sys.stdout = None  # type: ignore[assignment]
        sys.stderr = None  # type: ignore[assignment]
        desktop._ensure_stdio()
        # 与 desktop.main 相同参数；能构造成功即过
        config = uvicorn.Config(
            "app.main:app",
            host="127.0.0.1",
            port=0,
            log_level="warning",
            use_colors=False,
        )
        assert config is not None
    finally:
        sys.stdout, sys.stderr = real_out, real_err
