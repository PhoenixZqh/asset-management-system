import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import type { AssetPayload } from "../types";
import { Modal } from "./Modal";

interface Props {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

const empty: AssetPayload = {
  code: "",
  name: "",
  category: "未分类",
  unit: "件",
  spec: "",
  location: "",
  unit_price: 0,
  stock_qty: 0,
  safety_stock: 0,
};

export function AssetModal({ open, onClose, onCreated }: Props) {
  const [form, setForm] = useState<AssetPayload>(empty);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setForm(empty);
      setError(null);
    }
  }, [open]);

  const set = <K extends keyof AssetPayload>(key: K, value: AssetPayload[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!form.code.trim() || !form.name.trim()) {
      setError("编码与名称不能为空");
      return;
    }
    setSubmitting(true);
    try {
      await api.createAsset(form);
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      title="新增资产"
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-ghost" onClick={onClose} type="button">
            取消
          </button>
          <button className="btn btn-primary" type="submit" form="asset-form" disabled={submitting}>
            {submitting ? "保存中..." : "保存"}
          </button>
        </>
      }
    >
      <form id="asset-form" className="form" onSubmit={submit}>
        <div className="field-row">
          <label className="field">
            <span>资产编码 *</span>
            <input value={form.code} onChange={(e) => set("code", e.target.value)} placeholder="如 IT-1002" />
          </label>
          <label className="field">
            <span>资产名称 *</span>
            <input value={form.name} onChange={(e) => set("name", e.target.value)} />
          </label>
        </div>
        <div className="field-row">
          <label className="field">
            <span>类别</span>
            <input value={form.category} onChange={(e) => set("category", e.target.value)} />
          </label>
          <label className="field">
            <span>单位</span>
            <input value={form.unit} onChange={(e) => set("unit", e.target.value)} />
          </label>
        </div>
        <div className="field-row">
          <label className="field">
            <span>规格</span>
            <input value={form.spec ?? ""} onChange={(e) => set("spec", e.target.value)} />
          </label>
          <label className="field">
            <span>存放位置</span>
            <input value={form.location ?? ""} onChange={(e) => set("location", e.target.value)} />
          </label>
        </div>
        <div className="field-row three">
          <label className="field">
            <span>单价(元)</span>
            <input
              type="number"
              min={0}
              step="0.01"
              value={form.unit_price}
              onChange={(e) => set("unit_price", Number(e.target.value))}
            />
          </label>
          <label className="field">
            <span>初始库存</span>
            <input
              type="number"
              min={0}
              step={1}
              value={form.stock_qty}
              onChange={(e) => set("stock_qty", Number(e.target.value))}
            />
          </label>
          <label className="field">
            <span>安全库存</span>
            <input
              type="number"
              min={0}
              step={1}
              value={form.safety_stock}
              onChange={(e) => set("safety_stock", Number(e.target.value))}
            />
          </label>
        </div>
        {error && <div className="form-error">{error}</div>}
      </form>
    </Modal>
  );
}
