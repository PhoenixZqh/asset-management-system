from fastapi import APIRouter

from app.api import assets, stock

api_router = APIRouter()
api_router.include_router(assets.router)
api_router.include_router(stock.router)

__all__ = ["api_router"]
