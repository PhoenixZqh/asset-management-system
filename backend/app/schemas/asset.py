from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssetBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=64, description="资产编码，唯一")
    name: str = Field(..., min_length=1, max_length=128)
    category: str = Field(default="未分类", max_length=64)
    unit: str = Field(default="件", max_length=16)
    spec: str | None = Field(default=None, max_length=128)
    location: str | None = Field(default=None, max_length=128)
    unit_price: float = Field(default=0, ge=0)
    safety_stock: int = Field(default=0, ge=0)


class AssetCreate(AssetBase):
    stock_qty: int = Field(default=0, ge=0, description="初始库存")


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, max_length=64)
    unit: str | None = Field(default=None, max_length=16)
    spec: str | None = Field(default=None, max_length=128)
    location: str | None = Field(default=None, max_length=128)
    unit_price: float | None = Field(default=None, ge=0)
    safety_stock: int | None = Field(default=None, ge=0)


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_qty: int
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class AssetPage(BaseModel):
    items: list[AssetRead]
    total: int
    page: int
    page_size: int
