from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class MovementType(str, enum.Enum):
    IN = "IN"    # 入库
    OUT = "OUT"  # 出库


class StockMovement(Base, TimestampMixin):
    """出入库流水。每次入库/出库生成一条不可变记录。"""

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, native_enum=False, length=8), index=True, nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    # 操作后的库存结存，便于回溯对账
    balance_after: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    operator: Mapped[str] = mapped_column(String(64), default="系统", nullable=False)
    ref_no: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 领用人/借用人：出库时记录领取人，归还入库时直接沿用原出库的领用人
    recipient: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # 放置地点：入库为存储位置，出库为领用/送达位置
    placement_location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 归一字段：是否为归还入库
    is_return: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 归还入库关联的原出库记录
    return_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_movements.id", ondelete="SET NULL"), nullable=True, index=True
    )

    asset: Mapped[Asset] = relationship(back_populates="movements")

    @property
    def asset_code(self) -> str:
        return self.asset.code

    @property
    def asset_name(self) -> str:
        return self.asset.name

    @property
    def unit(self) -> str:
        return self.asset.unit
