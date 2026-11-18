from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.asset import AssetCreate, AssetPage, AssetRead, AssetUpdate
from app.services import asset_service

router = APIRouter(prefix="/assets", tags=["资产"])


@router.get("", response_model=AssetPage)
def list_assets(
    keyword: str | None = Query(default=None, description="按编码/名称/类别模糊搜索"),
    category: str | None = Query(default=None),
    low_stock_only: bool = Query(default=False, description="仅看低库存"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> AssetPage:
    items, total = asset_service.list_assets(
        db,
        keyword=keyword,
        category=category,
        low_stock_only=low_stock_only,
        page=page,
        page_size=page_size,
    )
    return AssetPage(
        items=[AssetRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)) -> list[str]:
    return asset_service.list_categories(db)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> AssetRead:
    try:
        asset = asset_service.get_asset(db, asset_id)
    except asset_service.AssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return AssetRead.model_validate(asset)


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> AssetRead:
    try:
        asset = asset_service.create_asset(db, payload)
    except asset_service.DuplicateCodeError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return AssetRead.model_validate(asset)


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(
    asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)
) -> AssetRead:
    try:
        asset = asset_service.update_asset(db, asset_id, payload)
    except asset_service.AssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return AssetRead.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> None:
    try:
        asset_service.delete_asset(db, asset_id)
    except asset_service.AssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
