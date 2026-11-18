from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.movement import MovementType


class MovementCreate(BaseModel):
    asset_id: int = Field(..., ge=1)
    type: MovementType
    quantity: int = Field(..., gt=0, description="本次出入库数量，必须大于 0")
    unit_price: float | None = Field(default=None, ge=0, description="留空则沿用资产单价")
    operator: str = Field(default="系统", max_length=64)
    ref_no: str | None = Field(default=None, max_length=64)
    remark: str | None = Field(default=None, max_length=255)
    recipient: str | None = Field(default=None, max_length=64, description="领用人/借用人")
    placement_location: str | None = Field(
        default=None, max_length=128, description="入库放置地点 / 出库放置地点"
    )
    is_return: bool = Field(default=False, description="入库是否为归还")
    return_of_id: int | None = Field(default=None, ge=1, description="归还对应的出库记录 ID")


class MovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    asset_code: str
    asset_name: str
    unit: str
    type: MovementType
    quantity: int
    unit_price: float
    balance_after: int
    operator: str
    ref_no: str | None
    remark: str | None
    recipient: str | None
    placement_location: str | None
    is_return: bool
    return_of_id: int | None
    created_at: datetime


class MovementPage(BaseModel):
    items: list[MovementRead]
    total: int
    page: int
    page_size: int


class OutstandingMovement(BaseModel):
    """尚未（全部）归还的出库记录，用于归还时选择并套用领用人。"""

    id: int
    asset_id: int
    asset_code: str
    asset_name: str
    unit: str
    recipient: str | None
    placement_location: str | None
    quantity: int
    returned_quantity: int
    outstanding_quantity: int
    created_at: datetime


class StockStats(BaseModel):
    total_assets: int
    total_stock_qty: int
    total_stock_value: float
    low_stock_count: int
    today_in: int
    today_out: int
    month_in: int
    month_out: int
