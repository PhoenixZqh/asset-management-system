export type MovementType = "IN" | "OUT";

export interface Asset {
  id: number;
  code: string;
  name: string;
  category: string;
  unit: string;
  spec: string | null;
  location: string | null;
  unit_price: number;
  stock_qty: number;
  safety_stock: number;
  is_low_stock: boolean;
  created_at: string;
  updated_at: string;
}

export interface Movement {
  id: number;
  asset_id: number;
  asset_code: string;
  asset_name: string;
  unit: string;
  type: MovementType;
  quantity: number;
  unit_price: number;
  balance_after: number;
  operator: string;
  ref_no: string | null;
  remark: string | null;
  recipient: string | null;
  placement_location: string | null;
  is_return: boolean;
  return_of_id: number | null;
  created_at: string;
}

export interface StockStats {
  total_assets: number;
  total_stock_qty: number;
  total_stock_value: number;
  low_stock_count: number;
  today_in: number;
  today_out: number;
  month_in: number;
  month_out: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface MovementPayload {
  asset_id: number;
  type: MovementType;
  quantity: number;
  unit_price?: number | null;
  operator?: string;
  ref_no?: string | null;
  remark?: string | null;
  recipient?: string | null;
  placement_location?: string | null;
  is_return?: boolean;
  return_of_id?: number | null;
}

export interface OutstandingMovement {
  id: number;
  asset_id: number;
  asset_code: string;
  asset_name: string;
  unit: string;
  recipient: string | null;
  placement_location: string | null;
  quantity: number;
  returned_quantity: number;
  outstanding_quantity: number;
  created_at: string;
}

export interface AssetPayload {
  code: string;
  name: string;
  category: string;
  unit: string;
  spec?: string | null;
  location?: string | null;
  unit_price: number;
  stock_qty: number;
  safety_stock: number;
}
