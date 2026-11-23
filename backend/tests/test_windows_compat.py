"""Windows 兼容性相关的可本地复现断言（无需真实 Windows）。"""

from __future__ import annotations

import os
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
