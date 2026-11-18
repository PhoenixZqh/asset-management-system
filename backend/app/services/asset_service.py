from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


class DuplicateCodeError(Exception):
    pass


class AssetNotFoundError(Exception):
    pass


def _apply_search(stmt, keyword: str | None):
    if keyword:
        like = f"%{keyword.strip()}%"
        stmt = stmt.where(
            (Asset.code.ilike(like))
            | (Asset.name.ilike(like))
            | (Asset.category.ilike(like))
        )
    return stmt


def list_assets(
    db: Session,
    *,
    keyword: str | None = None,
    category: str | None = None,
    low_stock_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Asset], int]:
    stmt = select(Asset)
    if category:
        stmt = stmt.where(Asset.category == category)
    stmt = _apply_search(stmt, keyword)
    if low_stock_only:
        stmt = stmt.where(Asset.stock_qty <= Asset.safety_stock)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Asset.id.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).all())
    return items, total


def get_asset(db: Session, asset_id: int) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise AssetNotFoundError(f"资产 {asset_id} 不存在")
    return asset


def create_asset(db: Session, payload: AssetCreate) -> Asset:
    exists = db.scalar(select(Asset).where(Asset.code == payload.code))
    if exists:
        raise DuplicateCodeError(f"资产编码 {payload.code} 已存在")

    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(db: Session, asset_id: int, payload: AssetUpdate) -> Asset:
    asset = get_asset(db, asset_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id: int) -> None:
    asset = get_asset(db, asset_id)
    db.delete(asset)
    db.commit()


def list_categories(db: Session) -> list[str]:
    rows = db.scalars(select(Asset.category).distinct().order_by(Asset.category)).all()
    return [row for row in rows if row]
