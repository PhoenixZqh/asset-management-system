import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { AssetModal } from "../components/AssetModal";
import type { Asset, Page } from "../types";

export function AssetsView({ onChanged }: { onChanged: () => void }) {
  const [data, setData] = useState<Page<Asset> | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const pageSize = 12;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listAssets({ keyword, category, page, page_size: pageSize });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }, [keyword, category, page]);

  const loadCategories = useCallback(() => {
    api.listCategories().then(setCategories).catch(() => undefined);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  const remove = async (asset: Asset) => {
    if (!confirm(`确认删除资产「${asset.name}」？其出入库记录也会一并删除。`)) return;
    try {
      await api.deleteAsset(asset.id);
      load();
      loadCategories();
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    }
  };

  return (
    <div className="panel">
      <div className="toolbar">
        <div className="filters">
          <input
            className="input-search"
            placeholder="搜索编码/名称"
            value={keyword}
            onChange={(e) => {
              setKeyword(e.target.value);
              setPage(1);
            }}
          />
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
          >
            <option value="">全部类别</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="actions">
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
            + 新增资产
          </button>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>编码</th>
              <th>名称</th>
              <th>类别</th>
              <th>规格</th>
              <th>位置</th>
              <th>单价</th>
              <th>库存</th>
              <th>安全库存</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={10} className="empty">加载中...</td></tr>
            )}
            {!loading && data?.items.length === 0 && (
              <tr><td colSpan={10} className="empty">暂无资产，请点击右上角新增</td></tr>
            )}
            {!loading &&
              data?.items.map((a) => (
                <tr key={a.id}>
                  <td className="mono">{a.code}</td>
                  <td>{a.name}</td>
                  <td><span className="chip">{a.category}</span></td>
                  <td className="truncate">{a.spec ?? "-"}</td>
                  <td className="truncate">{a.location ?? "-"}</td>
                  <td className="num">¥{a.unit_price.toFixed(2)}</td>
                  <td className="num strong">{a.stock_qty}{a.unit}</td>
                  <td className="num">{a.safety_stock}{a.unit}</td>
                  <td>
                    {a.is_low_stock ? (
                      <span className="tag tag-out">低库存</span>
                    ) : (
                      <span className="tag tag-in">正常</span>
                    )}
                  </td>
                  <td>
                    <button className="link-danger" onClick={() => remove(a)}>
                      删除
                    </button>
                  </td>
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

      <AssetModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={() => {
          load();
          loadCategories();
          onChanged();
        }}
      />
    </div>
  );
}
