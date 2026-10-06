"use client";

import React, { useState } from "react";
import { WorkOrder } from "@/types";
import { api } from "@/lib/api/client";

interface RecordDowntimeModalProps {
  workOrder: WorkOrder | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function RecordDowntimeModal({ workOrder, isOpen, onClose, onSuccess }: RecordDowntimeModalProps) {
  const [reason, setReason] = useState<string>("MACHINE_BREAKDOWN");
  const [durationMinutes, setDurationMinutes] = useState<number>(30);
  const [remarks, setRemarks] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !workOrder) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (durationMinutes < 0) {
      setError("Duration minutes cannot be negative.");
      return;
    }

    setLoading(true);
    try {
      const nowDt = new Date().toISOString();
      await api.post(`/work-orders/${workOrder.id}/downtime`, {
        work_order_id: workOrder.id,
        machine_id: workOrder.assigned_machine_id || undefined,
        start_time: nowDt,
        duration_minutes: Number(durationMinutes),
        reason,
        remarks: remarks.trim() || undefined,
      });

      setReason("MACHINE_BREAKDOWN");
      setDurationMinutes(30);
      setRemarks("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to record downtime log.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-amber-500 animate-pulse" />
            Record Downtime / Delay — {workOrder.work_order_number}
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
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Downtime Reason Category *
            </label>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 font-medium"
            >
              <option value="MACHINE_BREAKDOWN">MACHINE_BREAKDOWN — Mechanical/Tooling Failure</option>
              <option value="MATERIAL_UNAVAILABLE">MATERIAL_UNAVAILABLE — Raw Material Supply Delay</option>
              <option value="OPERATOR_UNAVAILABLE">OPERATOR_UNAVAILABLE — Shift Change / Staffing</option>
              <option value="MAINTENANCE">MAINTENANCE — Scheduled Preventive Maintenance</option>
              <option value="POWER_FAILURE">POWER_FAILURE — Facility Electrical Outage</option>
              <option value="OTHER">OTHER — Unspecified Delay</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Duration (Minutes) *
            </label>
            <input
              type="number"
              min="1"
              required
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(Number(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 font-mono text-lg font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Detailed Remarks / Corrective Action
            </label>
            <textarea
              rows={3}
              placeholder="Replaced worn cutter insert, cleared chip conveyor block..."
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
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
              className="px-5 py-2 text-sm font-semibold bg-amber-600 hover:bg-amber-500 text-white rounded-lg shadow-lg shadow-amber-900/30 transition disabled:opacity-50"
            >
              {loading ? "Recording..." : "Record Downtime"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
