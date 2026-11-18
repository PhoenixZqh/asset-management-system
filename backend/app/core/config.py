import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _user_data_dir() -> Path:
    """可写的数据目录：桌面版把数据库放到用户目录，避免写入安装目录。"""
    if sys.platform.startswith("win"):
        root = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    return root / "AssetManagement"


def _resource_dir() -> Path:
    """打包后资源所在目录；Packaged 时指向解包目录，否则为项目根。"""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return BASE_DIR


DATA_DIR = _user_data_dir()
FRONTEND_DIST = _resource_dir() / "frontend_dist"


def _default_database_url() -> str:
    # 打包后的桌面版写入用户数据目录；开发态沿用项目内数据库，保留既有数据
    if _is_frozen():
        return f"sqlite:///{_user_data_dir() / 'asset_management.db'}"
    return f"sqlite:///{BASE_DIR / 'asset_management.db'}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AMS_", env_file=".env", extra="ignore")

    app_name: str = "资产出入库管理系统"
    api_prefix: str = "/api"
    database_url: str = _default_database_url()
    frontend_dir: str = str(FRONTEND_DIST)
    debug: bool = False


settings = Settings()

# 确保数据目录与数据库所在目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
_db_path = settings.database_url.replace("sqlite:///", "", 1)
if settings.database_url.startswith("sqlite:///"):
    Path(_db_path).parent.mkdir(parents=True, exist_ok=True)
