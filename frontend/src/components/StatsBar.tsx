import type { StockStats } from "../types";

const currency = (value: number) =>
  value.toLocaleString("zh-CN", { style: "currency", currency: "CNY", maximumFractionDigits: 0 });

export function StatsBar({ stats }: { stats: StockStats | null }) {
  const cards = [
    { label: "资产种类", value: stats ? stats.total_assets : "-", sub: "在管品类", tone: "blue" },
    { label: "当前库存", value: stats ? stats.total_stock_qty.toLocaleString("zh-CN") : "-", sub: "总件数", tone: "green" },
    { label: "库存总值", value: stats ? currency(stats.total_stock_value) : "-", sub: "按单价估算", tone: "purple" },
    { label: "今日入库", value: stats ? stats.today_in : "-", sub: `本月 ${stats?.month_in ?? 0}`, tone: "teal" },
    { label: "今日出库", value: stats ? stats.today_out : "-", sub: `本月 ${stats?.month_out ?? 0}`, tone: "orange" },
    { label: "低库存预警", value: stats ? stats.low_stock_count : "-", sub: "需及时补货", tone: stats && stats.low_stock_count > 0 ? "red" : "gray" },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card) => (
        <div key={card.label} className={`stat-card tone-${card.tone}`}>
          <div className="stat-label">{card.label}</div>
          <div className="stat-value">{card.value}</div>
          <div className="stat-sub">{card.sub}</div>
        </div>
      ))}
    </div>
  );
}
