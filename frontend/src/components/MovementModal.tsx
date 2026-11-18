import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Asset, MovementType, OutstandingMovement } from "../types";
import { Modal } from "./Modal";

interface Props {
  open: boolean;
  initialType: MovementType;
  assets: Asset[];
  onClose: () => void;
  onCreated: () => void;
}

export function MovementModal({ open, initialType, assets, onClose, onCreated }: Props) {
  const [type, setType] = useState<MovementType>(initialType);
  const [isReturn, setIsReturn] = useState(false);
  const [assetId, setAssetId] = useState<number | "">("");
  const [returnOfId, setReturnOfId] = useState<number | "">("");
  const [recipient, setRecipient] = useState("");
  const [placement, setPlacement] = useState("");
  const [quantity, setQuantity] = useState<string>("1");
  const [operator, setOperator] = useState("管理员");
  const [refNo, setRefNo] = useState("");
  const [remark, setRemark] = useState("");
  const [outstanding, setOutstanding] = useState<OutstandingMovement[]>([]);
  const [loadingOutstanding, setLoadingOutstanding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const selected = useMemo(
    () => assets.find((a) => a.id === assetId),
    [assets, assetId]
  );
  const returning = type === "IN" && isReturn;

  useEffect(() => {
    if (open) {
      setType(initialType);
      setIsReturn(false);
      setAssetId("");
      setReturnOfId("");
      setRecipient("");
      setPlacement("");
      setQuantity("1");
      setRefNo("");
      setRemark("");
      setOutstanding([]);
      setError(null);
    }
  }, [open, initialType]);

  useEffect(() => {
    if (!open || !returning || !assetId) {
      setOutstanding([]);
      return;
    }
    setLoadingOutstanding(true);
    api
      .outstanding(Number(assetId))
      .then((list) => setOutstanding(list))
      .catch(() => setOutstanding([]))
      .finally(() => setLoadingOutstanding(false));
  }, [open, returning, assetId]);

  const chooseAsset = (value: number | "") => {
    setAssetId(value);
    setReturnOfId("");
    if (type === "OUT") setRecipient("");
  };

  const chooseReturn = (value: number | "") => {
    setReturnOfId(value);
    const record = outstanding.find((o) => o.id === value);
    if (record) {
      setRecipient(record.recipient ?? "");
      setQuantity(String(record.outstanding_quantity));
      if (!placement && selected?.location) setPlacement(selected.location);
    }
  };

  const changeType = (next: MovementType) => {
    setType(next);
    setIsReturn(false);
    setReturnOfId("");
    setRecipient("");
    setPlacement("");
    setError(null);
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!assetId) {
      setError("请选择资产");
      return;
    }
    const qty = Number(quantity);
    if (!Number.isInteger(qty) || qty <= 0) {
      setError("数量必须为大于 0 的整数");
      return;
    }
    if (!placement.trim()) {
      setError(type === "IN" ? "请填写入库放置地点" : "请填写出库放置地点");
      return;
    }
    if (type === "OUT") {
      if (!recipient.trim()) {
        setError("请填写领用人");
        return;
      }
      if (selected && qty > selected.stock_qty) {
        setError(`库存不足，当前库存 ${selected.stock_qty}${selected.unit}`);
        return;
      }
    }
    let returnPayload: { is_return: boolean; return_of_id: number | null } = {
      is_return: false,
      return_of_id: null,
    };
    if (returning) {
      if (!returnOfId) {
        setError("归还入库请选择关联的出库记录");
        return;
      }
      const record = outstanding.find((o) => o.id === returnOfId);
      if (record && qty > record.outstanding_quantity) {
        setError(`归还数量超过未归还数量（最多 ${record.outstanding_quantity}${record.unit}）`);
        return;
      }
      returnPayload = { is_return: true, return_of_id: Number(returnOfId) };
    }

    setSubmitting(true);
    try {
      await api.createMovement({
        asset_id: Number(assetId),
        type,
        quantity: qty,
        operator: operator || "系统",
        ref_no: refNo || null,
        remark: remark || null,
        recipient: type === "OUT" ? recipient.trim() : returning ? recipient || null : null,
        placement_location: placement.trim(),
        ...returnPayload,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  const placementLabel = type === "IN" ? "入库放置地点" : "出库放置地点";

  return (
    <Modal
      open={open}
      title={type === "IN" ? "新建入库单" : "新建出库单"}
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-ghost" onClick={onClose} type="button">
            取消
          </button>
          <button className="btn btn-primary" type="submit" form="movement-form" disabled={submitting}>
            {submitting ? "提交中..." : "确认提交"}
          </button>
        </>
      }
    >
      <form id="movement-form" className="form" onSubmit={submit}>
        <div className="type-switch">
          <button
            type="button"
            className={`type-option ${type === "IN" ? "active in" : ""}`}
            onClick={() => changeType("IN")}
          >
            ↓ 入库
          </button>
          <button
            type="button"
            className={`type-option ${type === "OUT" ? "active out" : ""}`}
            onClick={() => changeType("OUT")}
          >
            ↑ 出库
          </button>
        </div>

        {type === "IN" && (
          <div className="type-switch">
            <button
              type="button"
              className={`type-option ${!isReturn ? "active in" : ""}`}
              onClick={() => {
                setIsReturn(false);
                setReturnOfId("");
                setRecipient("");
              }}
            >
              普通入库
            </button>
            <button
              type="button"
              className={`type-option ${isReturn ? "active in" : ""}`}
              onClick={() => setIsReturn(true)}
            >
              归还入库
            </button>
          </div>
        )}

        <label className="field">
          <span>资产</span>
          <select
            value={assetId}
            onChange={(e) => chooseAsset(e.target.value ? Number(e.target.value) : "")}
          >
            <option value="">请选择资产</option>
            {assets.map((a) => (
              <option key={a.id} value={a.id}>
                {a.code} · {a.name}（库存 {a.stock_qty}
                {a.unit}）
              </option>
            ))}
          </select>
        </label>

        {returning && (
          <label className="field">
            <span>关联出库记录（归还）</span>
            <select
              value={returnOfId}
              onChange={(e) => chooseReturn(e.target.value ? Number(e.target.value) : "")}
              disabled={!assetId || loadingOutstanding || outstanding.length === 0}
            >
              <option value="">
                {!assetId
                  ? "请先选择资产"
                  : loadingOutstanding
                  ? "加载中..."
                  : outstanding.length === 0
                  ? "该资产没有待归还的出库记录"
                  : "请选择出库记录"}
              </option>
              {outstanding.map((o) => (
                <option key={o.id} value={o.id}>
                  #{o.id} · 领用人 {o.recipient ?? "未登记"} · 未归还 {o.outstanding_quantity}
                  {o.unit}
                </option>
              ))}
            </select>
          </label>
        )}

        {(type === "OUT" || returning) && (
          <label className="field">
            <span>领用人{type === "OUT" ? " *" : ""}</span>
            <input
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              placeholder={returning ? "选择出库记录后自动带入" : "请输入领用人"}
              readOnly={returning}
            />
          </label>
        )}

        <label className="field">
          <span>{placementLabel} *</span>
          <input
            value={placement}
            onChange={(e) => setPlacement(e.target.value)}
            placeholder={
              type === "IN" ? "如 A区-01-03（存放位置）" : "如 研发部-3楼（领用/送达位置）"
            }
          />
        </label>

        <div className="field-row">
          <label className="field">
            <span>数量</span>
            <input
              type="number"
              min={1}
              step={1}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </label>
          <label className="field">
            <span>操作人</span>
            <input value={operator} onChange={(e) => setOperator(e.target.value)} />
          </label>
        </div>

        <label className="field">
          <span>单据号（可选）</span>
          <input
            placeholder={type === "IN" ? "如 RK20261118001" : "如 CK20261118001"}
            value={refNo}
            onChange={(e) => setRefNo(e.target.value)}
          />
        </label>

        <label className="field">
          <span>备注（可选）</span>
          <textarea rows={2} value={remark} onChange={(e) => setRemark(e.target.value)} />
        </label>

        {selected && !returning && (
          <div className="hint">
            提交后库存：
            <strong>
              {type === "IN"
                ? selected.stock_qty + (Number(quantity) || 0)
                : selected.stock_qty - (Number(quantity) || 0)}
            </strong>{" "}
            {selected.unit}
          </div>
        )}
        {error && <div className="form-error">{error}</div>}
      </form>
    </Modal>
  );
}
