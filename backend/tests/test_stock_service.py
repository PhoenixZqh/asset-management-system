from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.asset import Asset
from app.models.movement import MovementType
from app.schemas.movement import MovementCreate
from app.services import stock_service


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)
    session = SessionLocal()
    session.add(Asset(code="T-1", name="测试物料", unit="件", unit_price=10, stock_qty=10, safety_stock=3))
    session.commit()
    try:
        yield session
    finally:
        session.close()


def test_inbound_increases_stock(db: Session) -> None:
    movement = stock_service.create_movement(
        db, MovementCreate(asset_id=1, type=MovementType.IN, quantity=5)
    )
    assert movement.balance_after == 15
    assert db.get(Asset, 1).stock_qty == 15


def test_outbound_decreases_stock(db: Session) -> None:
    movement = stock_service.create_movement(
        db, MovementCreate(asset_id=1, type=MovementType.OUT, quantity=4)
    )
    assert movement.balance_after == 6
    assert db.get(Asset, 1).stock_qty == 6


def test_outbound_exceeding_stock_rejected(db: Session) -> None:
    with pytest.raises(stock_service.InsufficientStockError):
        stock_service.create_movement(
            db, MovementCreate(asset_id=1, type=MovementType.OUT, quantity=999)
        )
    assert db.get(Asset, 1).stock_qty == 10


def test_return_reuses_recipient(db: Session) -> None:
    out = stock_service.create_movement(
        db,
        MovementCreate(
            asset_id=1,
            type=MovementType.OUT,
            quantity=4,
            recipient="王五",
            placement_location="研发部",
        ),
    )
    ret = stock_service.create_movement(
        db,
        MovementCreate(
            asset_id=1, type=MovementType.IN, quantity=2, is_return=True, return_of_id=out.id
        ),
    )
    assert ret.recipient == "王五"
    assert ret.is_return is True
    assert db.get(Asset, 1).stock_qty == 8  # 10 - 4 + 2


def test_outstanding_and_return_limit(db: Session) -> None:
    out = stock_service.create_movement(
        db, MovementCreate(asset_id=1, type=MovementType.OUT, quantity=4, recipient="赵六")
    )
    outstanding = stock_service.list_outstanding(db, 1)
    assert len(outstanding) == 1
    assert outstanding[0].outstanding_quantity == 4

    stock_service.create_movement(
        db,
        MovementCreate(
            asset_id=1, type=MovementType.IN, quantity=3, is_return=True, return_of_id=out.id
        ),
    )
    outstanding = stock_service.list_outstanding(db, 1)
    assert outstanding[0].outstanding_quantity == 1

    with pytest.raises(stock_service.InvalidReturnError):
        stock_service.create_movement(
            db,
            MovementCreate(
                asset_id=1,
                type=MovementType.IN,
                quantity=2,
                is_return=True,
                return_of_id=out.id,
            ),
        )


def test_return_requires_original_outbound(db: Session) -> None:
    with pytest.raises(stock_service.InvalidReturnError):
        stock_service.create_movement(
            db, MovementCreate(asset_id=1, type=MovementType.IN, quantity=1, is_return=True)
        )
