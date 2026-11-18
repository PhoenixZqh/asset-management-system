import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { MovementModal } from "../components/MovementModal";
import type { Movement, MovementType, Page } from "../types";

export function MovementsView({ onChanged }: { onChanged: () => void }) {
  const [data, setData] = useState<Page<Movement> | null>(null);
  const [assets, setAssets] = useState<Awaited<ReturnType<typeof api.listAssets>>["items"]>([]);
  const [keyword, setKeyword] = useState("");
  const [type, setType] = useState<MovementType | "">("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<MovementType>("IN");

  const pageSize = 15;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listMovements({
        keyword,
        type,
        start: start ? `${start}T00:00:00` : undefined,
        end: end ? `${end}T23:59:59` : undefined,
        page,
        page_size: pageSize,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }, [keyword, type, start, end, page]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    api.listAssets({ page_size: 200 }).then((res) => setAssets(res.items)).catch(() => undefined);
  }, []);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  const openNew = (movementType: MovementType) => {
    setModalType(movementType);
    setModalOpen(true);
  };

  return (
    <div className="panel">
      <div className="toolbar">
        <div className="filters">
          <input
            className="input-search"
            placeholder="搜索编码/名称/单据号/操作人/领用人"
            value={keyword}
            onChange={(e) => {
              setKeyword(e.target.value);
              setPage(1);
            }}
          />
          <select
            value={type}
            onChange={(e) => {
              setType(e.target.value as MovementType | "");
              setPage(1);
            }}
          >
            <option value="">全部类型</option>
            <option value="IN">入库</option>
            <option value="OUT">出库</option>
          </select>
          <input type="date" value={start} onChange={(e) => { setStart(e.target.value); setPage(1); }} />
          <input type="date" value={end} onChange={(e) => { setEnd(e.target.value); setPage(1); }} />
          {(keyword || type || start || end) && (
            <button
              className="btn btn-ghost"
              onClick={() => {
                setKeyword("");
                setType("");
                setStart("");
                setEnd("");
                setPage(1);
              }}
            >
              重置
            </button>
          )}
        </div>
        <div className="actions">
          <button className="btn btn-success" onClick={() => openNew("IN")}>
            + 新建入库
          </button>
          <button className="btn btn-outline" onClick={() => openNew("OUT")}>
            + 新建出库
          </button>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>单据号</th>
              <th>资产编码</th>
              <th>资产名称</th>
              <th>类型</th>
              <th>领用人</th>
              <th>数量</th>
              <th>单价</th>
              <th>结存</th>
              <th>放置地点</th>
              <th>操作人</th>
              <th>时间</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={12} className="empty">加载中...</td></tr>
            )}
            {!loading && data?.items.length === 0 && (
              <tr><td colSpan={12} className="empty">暂无出入库记录</td></tr>
            )}
            {!loading &&
              data?.items.map((m) => (
                <tr key={m.id}>
                  <td className="mono">{m.ref_no ?? "-"}</td>
                  <td className="mono">{m.asset_code}</td>
                  <td>{m.asset_name}</td>
                  <td>
                    <span className={`tag ${m.type === "IN" ? "tag-in" : "tag-out"}`}>
                      {m.type === "IN" ? (m.is_return ? "归还入库" : "入库") : "出库"}
                    </span>
                  </td>
                  <td>{m.recipient ?? "-"}</td>
                  <td className="num">
                    {m.type === "IN" ? "+" : "-"}
                    {m.quantity}
                    {m.unit}
                  </td>
                  <td className="num">¥{m.unit_price.toFixed(2)}</td>
                  <td className="num strong">{m.balance_after}{m.unit}</td>
                  <td className="truncate">{m.placement_location ?? "-"}</td>
                  <td>{m.operator}</td>
                  <td className="mono small">{m.created_at.replace("T", " ").slice(0, 16)}</td>
                  <td className="truncate">{m.remark ?? "-"}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="pager">
        <span className="muted">
          共 {data?.total ?? 0} 条 · 第 {page}/{totalPages} 页
        </span>
        <div className="pager-btns">
          <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            上一页
          </button>
          <button className="btn btn-ghost" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            下一页
          </button>
        </div>
      </div>

      {modalOpen && (
        <MovementModal
          open
          initialType={modalType}
          assets={assets}
          onClose={() => setModalOpen(false)}
          onCreated={() => {
            load();
            onChanged();
          }}
        />
      )}
    </div>
  );
}
