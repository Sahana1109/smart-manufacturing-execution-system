"use client";

import React, { useState, useEffect } from "react";
import { X, ArrowRightLeft, CheckCircle2, AlertCircle } from "lucide-react";
import { Material, WorkOrder, MovementType } from "@/types";

interface StockOperationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOperationCompleted: () => void;
  materials: Material[];
  workOrders: WorkOrder[];
  initialOperation?: MovementType;
  initialMaterialId?: string;
}

export default function StockOperationModal({
  isOpen,
  onClose,
  onOperationCompleted,
  materials,
  workOrders,
  initialOperation = "RECEIPT",
  initialMaterialId = "",
}: StockOperationModalProps) {
  const [operationType, setOperationType] = useState<MovementType>(initialOperation);
  const [materialId, setMaterialId] = useState(initialMaterialId);
  const [workOrderId, setWorkOrderId] = useState("");
  const [quantity, setQuantity] = useState<number>(10);
  const [location, setLocation] = useState("MAIN-WAREHOUSE");
  const [reference, setReference] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setOperationType(initialOperation);
    if (initialMaterialId) setMaterialId(initialMaterialId);
    setError(null);
  }, [initialOperation, initialMaterialId, isOpen]);

  if (!isOpen) return null;

  const selectedMaterial = materials.find((m) => m.id === materialId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!materialId) {
      setError("Please select a target material.");
      return;
    }

    if (operationType === "ADJUSTMENT" && !reference.trim()) {
      setError("Please state the reason/reference for stock audit adjustment.");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      let endpoint = "";
      let payload: any = {};

      switch (operationType) {
        case "RECEIPT":
          endpoint = "http://localhost:8000/api/v1/inventory/stock/receipt";
          payload = {
            material_id: materialId,
            quantity: Number(quantity),
            location: location.trim() || "MAIN-WAREHOUSE",
            reference: reference.trim() || undefined,
          };
          break;
        case "RESERVATION":
          endpoint = "http://localhost:8000/api/v1/inventory/stock/reserve";
          payload = {
            material_id: materialId,
            work_order_id: workOrderId || undefined,
            quantity: Number(quantity),
            reference: reference.trim() || undefined,
          };
          break;
        case "RELEASE":
          endpoint = "http://localhost:8000/api/v1/inventory/stock/release";
          payload = {
            material_id: materialId,
            work_order_id: workOrderId || undefined,
            quantity: Number(quantity),
            reference: reference.trim() || undefined,
          };
          break;
        case "CONSUMPTION":
          endpoint = "http://localhost:8000/api/v1/inventory/stock/consume";
          payload = {
            material_id: materialId,
            work_order_id: workOrderId || undefined,
            quantity: Number(quantity),
            reference: reference.trim() || undefined,
          };
          break;
        case "ADJUSTMENT":
          endpoint = "http://localhost:8000/api/v1/inventory/stock/adjust";
          payload = {
            material_id: materialId,
            new_quantity: Number(quantity),
            reference: reference.trim(),
          };
          break;
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || data.detail || "Stock operation failed");
      }

      onOperationCompleted();
      onClose();
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold">
            <ArrowRightLeft className="h-5 w-5 text-cyan-400" />
            <span className="text-slate-100 text-lg">Record Stock Transaction</span>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Operation Selector Tabs */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Operation Type</label>
            <div className="grid grid-cols-5 gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
              {(["RECEIPT", "RESERVATION", "RELEASE", "CONSUMPTION", "ADJUSTMENT"] as MovementType[]).map((op) => (
                <button
                  key={op}
                  type="button"
                  onClick={() => setOperationType(op)}
                  className={`px-2 py-1.5 rounded-lg text-[10px] font-bold transition-all text-center ${
                    operationType === op
                      ? op === "RECEIPT"
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        : op === "RESERVATION"
                        ? "bg-blue-950 text-blue-300 border border-blue-800"
                        : op === "RELEASE"
                        ? "bg-slate-800 text-slate-200 border border-slate-700"
                        : op === "CONSUMPTION"
                        ? "bg-rose-950 text-rose-300 border border-rose-800"
                        : "bg-amber-950 text-amber-300 border border-amber-800"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {op === "RESERVATION" ? "RESERVE" : op === "ADJUSTMENT" ? "ADJUST" : op}
                </button>
              ))}
            </div>
          </div>

          {/* Material Select */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Select Material <span className="text-cyan-400">*</span>
            </label>
            <select
              value={materialId}
              onChange={(e) => setMaterialId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            >
              <option value="">-- Choose Material --</option>
              {materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.material_code} - {m.name} (Stock: {m.stock?.quantity ?? 0} {m.unit}, Available: {m.stock?.available_quantity ?? 0})
                </option>
              ))}
            </select>
          </div>

          {/* Work Order Select (for Reservation, Release, Consumption) */}
          {["RESERVATION", "RELEASE", "CONSUMPTION"].includes(operationType) && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Associated Work Order (Optional)</label>
              <select
                value={workOrderId}
                onChange={(e) => setWorkOrderId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">-- None / General Allocation --</option>
                {workOrders.map((wo) => (
                  <option key={wo.id} value={wo.id}>
                    {wo.work_order_number} ({wo.product?.name || "Product"}) [{wo.status}]
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Quantity Input */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                {operationType === "ADJUSTMENT" ? "New Total Stock Qty" : "Transaction Quantity"}
              </label>
              <input
                type="number"
                min={operationType === "ADJUSTMENT" ? "0" : "1"}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono font-bold"
                required
              />
            </div>

            {operationType === "RECEIPT" && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Storage Bin / Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="MAIN-WAREHOUSE"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            )}
          </div>

          {/* Reference / Remarks */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Reference / Remarks {operationType === "ADJUSTMENT" && <span className="text-cyan-400">*</span>}
            </label>
            <input
              type="text"
              placeholder="e.g. PO delivery number, physical audit count..."
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              required={operationType === "ADJUSTMENT"}
            />
          </div>

          {/* Current Stock Context Display */}
          {selectedMaterial && (
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-xs flex justify-between text-slate-400 font-mono">
              <span>Total: <strong className="text-slate-100">{selectedMaterial.stock?.quantity ?? 0}</strong></span>
              <span>Reserved: <strong className="text-amber-400">{selectedMaterial.stock?.reserved_quantity ?? 0}</strong></span>
              <span>Available: <strong className="text-emerald-400">{selectedMaterial.stock?.available_quantity ?? 0}</strong></span>
            </div>
          )}

          {/* Actions */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all flex items-center space-x-1.5"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>{loading ? "Processing..." : `Confirm ${operationType}`}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
