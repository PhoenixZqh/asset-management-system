from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.movement import StockMovement


class Asset(Base, TimestampMixin):
    """资产/物料主数据。库存数量由出入库记录驱动更新。"""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="未分类", nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="件", nullable=False)
    spec: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    movements: Mapped[list[StockMovement]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )

    @property
    def is_low_stock(self) -> bool:
        return self.stock_qty <= self.safety_stock
