from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.movement import MovementType
from app.schemas.movement import (
    MovementCreate,
    MovementPage,
    MovementRead,
    OutstandingMovement,
    StockStats,
)
from app.services import stock_service
from app.services.asset_service import AssetNotFoundError

router = APIRouter(prefix="/stock", tags=["出入库"])


@router.get("/movements", response_model=MovementPage)
def list_movements(
    keyword: str | None = Query(default=None),
    asset_id: int | None = Query(default=None),
    type: MovementType | None = Query(default=None, description="IN 入库 / OUT 出库"),
    start: datetime | None = Query(default=None, description="起始时间(含)"),
    end: datetime | None = Query(default=None, description="结束时间(含)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> MovementPage:
    items, total = stock_service.list_movements(
        db,
        keyword=keyword,
        asset_id=asset_id,
        type=type,
        start=start,
        end=end,
        page=page,
        page_size=page_size,
    )
    return MovementPage(
        items=[MovementRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/movements", response_model=MovementRead, status_code=status.HTTP_201_CREATED
)
def create_movement(
    payload: MovementCreate, db: Session = Depends(get_db)
) -> MovementRead:
    try:
        movement = stock_service.create_movement(db, payload)
    except AssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except stock_service.InsufficientStockError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except stock_service.InvalidReturnError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return MovementRead.model_validate(movement)


@router.get("/outstanding", response_model=list[OutstandingMovement])
def list_outstanding(
    asset_id: int = Query(..., ge=1, description="资产 ID"),
    db: Session = Depends(get_db),
) -> list[OutstandingMovement]:
    """该资产尚未全部归还的出库记录，供归还时选择并套用领用人。"""
    return stock_service.list_outstanding(db, asset_id)


@router.get("/stats", response_model=StockStats)
def get_stats(db: Session = Depends(get_db)) -> StockStats:
    return stock_service.get_stats(db)
