from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.asset import Asset
from app.models.movement import MovementType, StockMovement
from app.schemas.movement import MovementCreate, OutstandingMovement, StockStats
from app.services.asset_service import AssetNotFoundError


class InsufficientStockError(Exception):
    pass


class InvalidReturnError(Exception):
    pass


def _returned_qty(db: Session, out_id: int) -> int:
    """某条出库记录已被归还的数量。"""
    value = db.scalar(
        select(func.coalesce(func.sum(StockMovement.quantity), 0)).where(
            StockMovement.return_of_id == out_id,
            StockMovement.type == MovementType.IN,
            StockMovement.is_return.is_(True),
        )
    )
    return int(value or 0)


def _get_locked_asset(db: Session, asset_id: int) -> Asset:
    asset = db.scalars(
        select(Asset).where(Asset.id == asset_id).with_for_update()
    ).first()
    if asset is None:
        raise AssetNotFoundError(f"资产 {asset_id} 不存在")
    return asset


def create_movement(db: Session, payload: MovementCreate) -> StockMovement:
    asset = _get_locked_asset(db, payload.asset_id)

    recipient = payload.recipient
    is_return = bool(payload.is_return)
    return_of_id = payload.return_of_id

    if payload.type is MovementType.IN and is_return:
        # 归还入库：必须关联原出库记录，并直接套用原出库的领用人
        if not return_of_id:
            raise InvalidReturnError("归还入库必须选择关联的原出库记录")
        original = db.get(StockMovement, return_of_id)
        if original is None or original.type is not MovementType.OUT:
            raise InvalidReturnError("关联的原出库记录不存在")
        if original.asset_id != asset.id:
            raise InvalidReturnError("归还的资产与所选出库记录不一致")
        outstanding = original.quantity - _returned_qty(db, original.id)
        if payload.quantity > outstanding:
            raise InvalidReturnError(
                f"归还数量超过未归还数量，最多可归还 {outstanding}{asset.unit}"
            )
        recipient = original.recipient
    else:
        is_return = False
        return_of_id = None

    if payload.type is MovementType.OUT:
        if payload.quantity > asset.stock_qty:
            raise InsufficientStockError(
                f"库存不足：{asset.name} 当前库存 {asset.stock_qty}{asset.unit}，"
                f"本次需出库 {payload.quantity}{asset.unit}"
            )
        asset.stock_qty -= payload.quantity
    else:
        asset.stock_qty += payload.quantity

    unit_price = asset.unit_price if payload.unit_price is None else payload.unit_price

    movement = StockMovement(
        asset_id=asset.id,
        type=payload.type,
        quantity=payload.quantity,
        unit_price=unit_price,
        balance_after=asset.stock_qty,
        operator=payload.operator or "系统",
        ref_no=payload.ref_no,
        remark=payload.remark,
        recipient=recipient,
        placement_location=payload.placement_location,
        is_return=is_return,
        return_of_id=return_of_id,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def list_outstanding(db: Session, asset_id: int) -> list[OutstandingMovement]:
    """列出某资产尚未全部归还的出库记录，供归还时选择并套用领用人。"""
    stmt = (
        select(StockMovement)
        .where(
            StockMovement.asset_id == asset_id,
            StockMovement.type == MovementType.OUT,
        )
        .options(joinedload(StockMovement.asset))
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
    )
    result: list[OutstandingMovement] = []
    for movement in db.scalars(stmt).all():
        returned = _returned_qty(db, movement.id)
        outstanding = movement.quantity - returned
        if outstanding <= 0:
            continue
        result.append(
            OutstandingMovement(
                id=movement.id,
                asset_id=movement.asset_id,
                asset_code=movement.asset.code,
                asset_name=movement.asset.name,
                unit=movement.asset.unit,
                recipient=movement.recipient,
                placement_location=movement.placement_location,
                quantity=movement.quantity,
                returned_quantity=returned,
                outstanding_quantity=outstanding,
                created_at=movement.created_at,
            )
        )
    return result


def list_movements(
    db: Session,
    *,
    keyword: str | None = None,
    asset_id: int | None = None,
    type: MovementType | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[StockMovement], int]:
    stmt = select(StockMovement).join(StockMovement.asset)
    if asset_id:
        stmt = stmt.where(StockMovement.asset_id == asset_id)
    if type:
        stmt = stmt.where(StockMovement.type == type)
    if start:
        stmt = stmt.where(StockMovement.created_at >= start)
    if end:
        stmt = stmt.where(StockMovement.created_at <= end)
    if keyword:
        like = f"%{keyword.strip()}%"
        stmt = stmt.where(
            (Asset.code.ilike(like))
            | (Asset.name.ilike(like))
            | (StockMovement.ref_no.ilike(like))
            | (StockMovement.operator.ilike(like))
            | (StockMovement.recipient.ilike(like))
            | (StockMovement.placement_location.ilike(like))
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = (
        stmt.options(joinedload(StockMovement.asset))
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).all())
    return items, total


def get_stats(db: Session) -> StockStats:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_assets = db.scalar(select(func.count(Asset.id))) or 0
    total_qty = db.scalar(select(func.coalesce(func.sum(Asset.stock_qty), 0))) or 0
    total_value = db.scalar(
        select(func.coalesce(func.sum(Asset.stock_qty * Asset.unit_price), 0))
    ) or 0
    low_stock = (
        db.scalar(
            select(func.count(Asset.id)).where(Asset.stock_qty <= Asset.safety_stock)
        )
        or 0
    )

    def sum_qty(type_: MovementType, since: datetime) -> int:
        value = db.scalar(
            select(func.coalesce(func.sum(StockMovement.quantity), 0)).where(
                StockMovement.type == type_, StockMovement.created_at >= since
            )
        )
        return int(value or 0)

    return StockStats(
        total_assets=int(total_assets),
        total_stock_qty=int(total_qty),
        total_stock_value=float(total_value),
        low_stock_count=int(low_stock),
        today_in=sum_qty(MovementType.IN, today_start),
        today_out=sum_qty(MovementType.OUT, today_start),
        month_in=sum_qty(MovementType.IN, month_start),
        month_out=sum_qty(MovementType.OUT, month_start),
    )
