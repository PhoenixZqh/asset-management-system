import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { StatsBar } from "./components/StatsBar";
import type { StockStats } from "./types";
import { AssetsView } from "./views/AssetsView";
import { MovementsView } from "./views/MovementsView";

type Tab = "movements" | "assets";

export default function App() {
  const [tab, setTab] = useState<Tab>("movements");
  const [stats, setStats] = useState<StockStats | null>(null);

  const refreshStats = useCallback(() => {
    api.stats().then(setStats).catch(() => undefined);
  }, []);

  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="logo">◧</span>
          <div>
            <div className="brand-name">资产管理</div>
            <div className="brand-sub">出入库平台</div>
          </div>
        </div>
        <nav className="nav">
          <button
            className={`nav-item ${tab === "movements" ? "active" : ""}`}
            onClick={() => setTab("movements")}
          >
            <span className="nav-ico">⇅</span> 出入库管理
          </button>
          <button
            className={`nav-item ${tab === "assets" ? "active" : ""}`}
            onClick={() => setTab("assets")}
          >
            <span className="nav-ico">▤</span> 资产台账
          </button>
        </nav>
        <div className="sidebar-foot">v1.0.0 · 演示环境</div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>{tab === "movements" ? "出入库管理" : "资产台账"}</h1>
            <p className="muted">
              {tab === "movements"
                ? "登记每一笔入库与出库，实时更新库存结存"
                : "维护资产主数据与安全库存水位"}
            </p>
          </div>
          <div className="topbar-date">
            {new Date().toLocaleDateString("zh-CN", {
              year: "numeric",
              month: "long",
              day: "numeric",
              weekday: "long",
            })}
          </div>
        </header>

        <StatsBar stats={stats} />

        {tab === "movements" ? (
          <MovementsView onChanged={refreshStats} />
        ) : (
          <AssetsView onChanged={refreshStats} />
        )}
      </main>
    </div>
  );
}
