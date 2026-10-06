"use client";

import React, { useState, useEffect } from "react";
import { WorkOrder } from "@/types";
import { api } from "@/lib/api/client";

interface CompleteExecutionModalProps {
  workOrder: WorkOrder | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CompleteExecutionModal({ workOrder, isOpen, onClose, onSuccess }: CompleteExecutionModalProps) {
  const [producedQuantity, setProducedQuantity] = useState<number>(0);
  const [notes, setNotes] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && workOrder) {
      setProducedQuantity(workOrder.planned_quantity);
      setNotes("");
    }
  }, [isOpen, workOrder]);

  if (!isOpen || !workOrder) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (producedQuantity <= 0) {
      setError("Produced quantity must be greater than 0.");
      return;
    }

    setLoading(true);
    try {
      await api.post(`/work-orders/${workOrder.id}/complete`, {
        produced_quantity: Number(producedQuantity),
        notes: notes.trim() || undefined,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to complete production execution.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
            Complete Execution — {workOrder.work_order_number}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl font-semibold">
            &times;
          </button>
        </div>

        {error && (
          <div className="bg-rose-950/80 border border-rose-800 text-rose-300 p-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
            <div>
              Target Planned Qty: <span className="font-bold text-cyan-400">{workOrder.planned_quantity} {workOrder.product?.unit_of_measure || "PCS"}</span>
            </div>
            <div>
              Product: <span className="font-medium text-white">{workOrder.product?.name}</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Final Produced Quantity *
            </label>
            <input
              type="number"
              min="1"
              required
              value={producedQuantity}
              onChange={(e) => setProducedQuantity(Number(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 font-mono text-lg font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Completion Remarks / Quality Notes
            </label>
            <textarea
              rows={3}
              placeholder="Good parts yield, scrap count, batch shift notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-400 hover:text-white transition">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg shadow-lg shadow-emerald-900/30 transition disabled:opacity-50"
            >
              {loading ? "Completing..." : "Complete Production"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
