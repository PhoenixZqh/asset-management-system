import type {
  Asset,
  AssetPayload,
  Movement,
  MovementPayload,
  MovementType,
  OutstandingMovement,
  Page,
  StockStats,
} from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let message = `请求失败 (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(message);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface MovementQuery {
  keyword?: string;
  type?: MovementType | "";
  start?: string;
  end?: string;
  page?: number;
  page_size?: number;
}

function toQuery(params: object): string {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      qs.set(key, String(value));
    }
  });
  const str = qs.toString();
  return str ? `?${str}` : "";
}

export const api = {
  stats: () => request<StockStats>("/stock/stats"),

  listMovements: (query: MovementQuery) =>
    request<Page<Movement>>(`/stock/movements${toQuery(query)}`),

  createMovement: (payload: MovementPayload) =>
    request<Movement>("/stock/movements", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  outstanding: (assetId: number) =>
    request<OutstandingMovement[]>(`/stock/outstanding${toQuery({ asset_id: assetId })}`),

  listAssets: (query: { keyword?: string; category?: string; page?: number; page_size?: number }) =>
    request<Page<Asset>>(`/assets${toQuery(query)}`),

  listCategories: () => request<string[]>("/assets/categories"),

  createAsset: (payload: AssetPayload) =>
    request<Asset>("/assets", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  deleteAsset: (id: number) =>
    request<void>(`/assets/${id}`, { method: "DELETE" }),
};
