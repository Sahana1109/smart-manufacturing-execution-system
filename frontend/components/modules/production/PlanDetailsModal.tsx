"use client";

import React, { useState } from "react";
import { ProductionPlan, ProductionPlanStatus } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";

interface PlanDetailsModalProps {
  plan: ProductionPlan | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
}

export function PlanDetailsModal({ plan, isOpen, onClose, onRefresh }: PlanDetailsModalProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !plan) return null;

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canModify = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"].includes(r));
  const canCancel = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER"].includes(r));

  const handleStatusTransition = async (targetStatus: ProductionPlanStatus) => {
    setLoading(true);
    setError(null);
    try {
      await api.patch(`/production-plans/${plan.id}/status`, { status: targetStatus });
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to update plan status.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelPlan = async () => {
    if (!confirm("Are you sure you want to cancel this production plan?")) return;
    setLoading(true);
    setError(null);
    try {
      await api.post(`/production-plans/${plan.id}/cancel`);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to cancel production plan.");
    } finally {
      setLoading(false);
    }
  };

  const statusColors: Record<string, string> = {
    DRAFT: "bg-slate-700 text-slate-200 border-slate-600",
    PLANNED: "bg-amber-950/80 text-amber-300 border-amber-800",
    IN_PROGRESS: "bg-cyan-950/80 text-cyan-300 border-cyan-800 animate-pulse",
    COMPLETED: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
    CANCELLED: "bg-rose-950/80 text-rose-300 border-rose-800",
  };

  const priorityColors: Record<string, string> = {
    LOW: "bg-slate-800 text-slate-400 border-slate-700",
    MEDIUM: "bg-blue-950 text-blue-400 border-blue-800",
    HIGH: "bg-purple-950 text-purple-300 border-purple-800",
    URGENT: "bg-rose-950 text-rose-400 border-rose-800 font-bold",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-white tracking-tight">{plan.plan_number}</h2>
              <span className={`px-2.5 py-0.5 text-xs rounded-full border ${statusColors[plan.status]}`}>
                {plan.status}
              </span>
              <span className={`px-2.5 py-0.5 text-xs rounded-full border ${priorityColors[plan.priority]}`}>
                {plan.priority} PRIORITY
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Product: <span className="text-white font-medium">{plan.product?.product_code} — {plan.product?.name}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl font-semibold"
          >
            &times;
          </button>
        </div>

        {error && (
          <div className="bg-rose-950/80 border border-rose-800 text-rose-300 p-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Planned Quantity</span>
            <span className="text-lg font-semibold text-cyan-400">
              {plan.planned_quantity.toLocaleString()} {plan.product?.unit_of_measure || "PCS"}
            </span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Start Date</span>
            <span className="text-sm font-medium text-slate-200">{plan.start_date}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Due Date</span>
            <span className="text-sm font-medium text-slate-200">{plan.due_date}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Created By</span>
            <span className="text-sm font-medium text-slate-200">
              {plan.created_by?.username || "System"}
            </span>
          </div>
        </div>

        {plan.notes && (
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Operational Notes
            </span>
            <p className="text-sm text-slate-300 bg-slate-800/60 p-3 rounded-lg border border-slate-800">
              {plan.notes}
            </p>
          </div>
        )}

        {canModify && plan.status !== "COMPLETED" && plan.status !== "CANCELLED" && (
          <div className="border-t border-slate-800 pt-4 space-y-3">
            <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Status Lifecycle Action
            </span>
            <div className="flex flex-wrap items-center gap-3">
              {plan.status === "DRAFT" && (
                <button
                  onClick={() => handleStatusTransition("PLANNED")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Release to PLANNED Schedule
                </button>
              )}

              {plan.status === "PLANNED" && (
                <button
                  onClick={() => handleStatusTransition("IN_PROGRESS")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Start Execution (IN_PROGRESS)
                </button>
              )}

              {plan.status === "IN_PROGRESS" && (
                <button
                  onClick={() => handleStatusTransition("COMPLETED")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Mark Execution COMPLETED
                </button>
              )}

              {canCancel && (
                <button
                  onClick={handleCancelPlan}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-rose-900/60 hover:bg-rose-800 text-rose-200 border border-rose-700 rounded-lg transition disabled:opacity-50"
                >
                  Cancel Plan
                </button>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-800">
          <span>Created: {new Date(plan.created_at).toLocaleString()}</span>
          <span>Last Updated: {new Date(plan.updated_at).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
