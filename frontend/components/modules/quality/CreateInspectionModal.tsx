"use client";

import React, { useState } from "react";
import { X, CheckCircle2, AlertCircle, ShieldCheck } from "lucide-react";
import { WorkOrder, QualityStatus } from "@/types";

interface CreateInspectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInspectionCreated: () => void;
  completedWorkOrders: WorkOrder[];
}

export default function CreateInspectionModal({
  isOpen,
  onClose,
  onInspectionCreated,
  completedWorkOrders,
}: CreateInspectionModalProps) {
  const [workOrderId, setWorkOrderId] = useState("");
  const [inspectedQty, setInspectedQty] = useState<number>(0);
  const [acceptedQty, setAcceptedQty] = useState<number>(0);
  const [rejectedQty, setRejectedQty] = useState<number>(0);
  const [status, setStatus] = useState<QualityStatus>("PASSED");
  const [remarks, setRemarks] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleWorkOrderSelect = (woId: string) => {
    setWorkOrderId(woId);
    const selectedWO = completedWorkOrders.find((w) => w.id === woId);
    if (selectedWO) {
      const produced = selectedWO.produced_quantity || selectedWO.planned_quantity;
      setInspectedQty(produced);
      setAcceptedQty(produced);
      setRejectedQty(0);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!workOrderId) {
      setError("Please select a completed work order.");
      return;
    }
    if (inspectedQty < 0 || acceptedQty < 0 || rejectedQty < 0) {
      setError("Quantities cannot be negative.");
      return;
    }
    if (acceptedQty + rejectedQty > inspectedQty) {
      setError(`Accepted (${acceptedQty}) + Rejected (${rejectedQty}) cannot exceed Inspected Quantity (${inspectedQty}).`);
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/api/v1/quality/inspections", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          work_order_id: workOrderId,
          inspected_quantity: Number(inspectedQty),
          accepted_quantity: Number(acceptedQty),
          rejected_quantity: Number(rejectedQty),
          status,
          remarks: remarks.trim() || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || data.detail || "Failed to create quality inspection");
      }

      onInspectionCreated();
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
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold">
            <ShieldCheck className="h-5 w-5 text-cyan-400" />
            <span className="text-slate-100 text-lg">New Quality Inspection</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Select Work Order */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Select Completed Work Order <span className="text-cyan-400">*</span>
            </label>
            <select
              value={workOrderId}
              onChange={(e) => handleWorkOrderSelect(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              required
            >
              <option value="">-- Choose Work Order --</option>
              {completedWorkOrders.map((wo) => (
                <option key={wo.id} value={wo.id}>
                  {wo.work_order_number} ({wo.product?.name || "Product"}) - Produced: {wo.produced_quantity || wo.planned_quantity}
                </option>
              ))}
            </select>
          </div>

          {/* Quantities Row */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Inspected Qty</label>
              <input
                type="number"
                min="0"
                value={inspectedQty}
                onChange={(e) => setInspectedQty(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Accepted Qty</label>
              <input
                type="number"
                min="0"
                value={acceptedQty}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setAcceptedQty(val);
                  if (val <= inspectedQty) setRejectedQty(inspectedQty - val);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Rejected Qty</label>
              <input
                type="number"
                min="0"
                value={rejectedQty}
                onChange={(e) => setRejectedQty(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                required
              />
            </div>
          </div>

          {/* Quality Status */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Quality Verdict Status</label>
            <div className="grid grid-cols-2 gap-2">
              {(["PASSED", "FAILED", "REWORK_REQUIRED", "PENDING"] as QualityStatus[]).map((st) => (
                <button
                  key={st}
                  type="button"
                  onClick={() => setStatus(st)}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all text-center ${
                    status === st
                      ? st === "PASSED"
                        ? "bg-emerald-950 border-emerald-500 text-emerald-300"
                        : st === "FAILED"
                        ? "bg-rose-950 border-rose-500 text-rose-300"
                        : st === "REWORK_REQUIRED"
                        ? "bg-amber-950 border-amber-500 text-amber-300"
                        : "bg-slate-800 border-cyan-500 text-cyan-300"
                      : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  {st.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Remarks */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Inspection Remarks</label>
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="e.g. Dimensions verified within ±0.02mm tolerance..."
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Modal Actions */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all disabled:opacity-50 flex items-center space-x-1.5"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>{loading ? "Recording..." : "Submit Inspection"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
