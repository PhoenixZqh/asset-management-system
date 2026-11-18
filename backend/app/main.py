from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.migrate import run_lightweight_migrations
from app.db.session import SessionLocal, engine
from app.models.asset import Asset


def _seed_if_empty() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Asset.id).limit(1)) is not None:
            return
        db.add_all(
            [
                Asset(
                    code="IT-1001",
                    name="联想 ThinkPad 笔记本",
                    category="办公设备",
                    unit="台",
                    spec="T14 Gen4 / i7 / 32G",
                    location="A区-01-03",
                    unit_price=8800,
                    stock_qty=12,
                    safety_stock=5,
                ),
                Asset(
                    code="OF-2001",
                    name="A4 复印纸",
                    category="办公耗材",
                    unit="箱",
                    spec="70g / 5包/箱",
                    location="B区-02-01",
                    unit_price=120,
                    stock_qty=40,
                    safety_stock=20,
                ),
                Asset(
                    code="NW-3001",
                    name="千兆交换机",
                    category="网络设备",
                    unit="台",
                    spec="24口 全千兆",
                    location="C区-01-02",
                    unit_price=1500,
                    stock_qty=6,
                    safety_stock=8,
                ),
            ]
        )
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()
    _seed_if_empty()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["系统"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


# ---------- 桌面版：托管前端静态资源（单页应用） ----------
_frontend = Path(settings.frontend_dir)
if (_frontend / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=_frontend / "assets"), name="assets")

_api_root = settings.api_prefix.strip("/")


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    if full_path == "health" or full_path == _api_root or full_path.startswith(_api_root + "/"):
        raise HTTPException(status_code=404)

    candidate = _frontend / full_path
    if full_path and candidate.is_file():
        return FileResponse(candidate)

    index = _frontend / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(
        status_code=404, detail="前端资源未构建，请先在 frontend 目录执行 npm run build"
    )
