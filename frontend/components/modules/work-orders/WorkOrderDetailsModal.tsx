"use client";

import React, { useState } from "react";
import { WorkOrder, WorkOrderStatus } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";

interface WorkOrderDetailsModalProps {
  workOrder: WorkOrder | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
  onOpenAssign: () => void;
}

export function WorkOrderDetailsModal({ workOrder, isOpen, onClose, onRefresh, onOpenAssign }: WorkOrderDetailsModalProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !workOrder) return null;

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canModify = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "OPERATOR"].includes(r));
  const canAssign = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"].includes(r));
  const canCancel = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER"].includes(r));

  const handleStatusTransition = async (targetStatus: WorkOrderStatus) => {
    setLoading(true);
    setError(null);
    try {
      await api.patch(`/work-orders/${workOrder.id}/status`, { status: targetStatus });
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to update work order status.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async () => {
    if (!confirm("Are you sure you want to cancel this work order?")) return;
    setLoading(true);
    setError(null);
    try {
      await api.post(`/work-orders/${workOrder.id}/cancel`);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to cancel work order.");
    } finally {
      setLoading(false);
    }
  };

  const statusColors: Record<string, string> = {
    DRAFT: "bg-slate-700 text-slate-200 border-slate-600",
    RELEASED: "bg-amber-950/80 text-amber-300 border-amber-800",
    IN_PROGRESS: "bg-cyan-950/80 text-cyan-300 border-cyan-800 animate-pulse",
    PAUSED: "bg-orange-950/80 text-orange-300 border-orange-800",
    COMPLETED: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
    CLOSED: "bg-slate-800 text-slate-400 border-slate-700",
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
              <h2 className="text-2xl font-bold text-white tracking-tight">{workOrder.work_order_number}</h2>
              <span className={`px-2.5 py-0.5 text-xs rounded-full border ${statusColors[workOrder.status]}`}>
                {workOrder.status}
              </span>
              <span className={`px-2.5 py-0.5 text-xs rounded-full border ${priorityColors[workOrder.priority]}`}>
                {workOrder.priority} PRIORITY
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Plan: <span className="text-white font-medium">{workOrder.production_plan?.plan_number || workOrder.production_plan_id}</span> |
              Product: <span className="text-white font-medium">{workOrder.product?.product_code} — {workOrder.product?.name}</span>
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl font-semibold">
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
              {workOrder.planned_quantity.toLocaleString()} {workOrder.product?.unit_of_measure || "PCS"}
            </span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Start Date</span>
            <span className="text-sm font-medium text-slate-200">{workOrder.start_date}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Due Date</span>
            <span className="text-sm font-medium text-slate-200">{workOrder.due_date}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 uppercase tracking-wider">Created By</span>
            <span className="text-sm font-medium text-slate-200">
              {workOrder.created_by?.username || "System"}
            </span>
          </div>
        </div>

        {/* Resources Assignment Card */}
        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-1">
            <span className="block text-xs text-slate-400 uppercase tracking-wider font-semibold">Assigned Shop Floor Resources</span>
            <div className="text-sm text-white flex items-center gap-4">
              <div>
                Machine: <span className="font-semibold text-cyan-400">{workOrder.assigned_machine ? `${workOrder.assigned_machine.machine_code} (${workOrder.assigned_machine.name})` : "Unassigned"}</span>
              </div>
              <div>
                Operator: <span className="font-semibold text-cyan-400">{workOrder.assigned_employee ? `${workOrder.assigned_employee.first_name} ${workOrder.assigned_employee.last_name}` : "Unassigned"}</span>
              </div>
            </div>
          </div>
          {canAssign && workOrder.status !== "CLOSED" && workOrder.status !== "CANCELLED" && (
            <button
              onClick={() => {
                onClose();
                onOpenAssign();
              }}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-medium rounded-lg border border-slate-700 transition"
            >
              Assign Resources
            </button>
          )}
        </div>

        {workOrder.notes && (
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Shop Floor Execution Notes
            </span>
            <p className="text-sm text-slate-300 bg-slate-800/60 p-3 rounded-lg border border-slate-800">
              {workOrder.notes}
            </p>
          </div>
        )}

        {canModify && workOrder.status !== "CLOSED" && workOrder.status !== "CANCELLED" && (
          <div className="border-t border-slate-800 pt-4 space-y-3">
            <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Status Lifecycle Execution Action
            </span>
            <div className="flex flex-wrap items-center gap-3">
              {workOrder.status === "DRAFT" && (
                <button
                  onClick={() => handleStatusTransition("RELEASED")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Release to Shop Floor (RELEASED)
                </button>
              )}

              {workOrder.status === "RELEASED" && (
                <button
                  onClick={() => handleStatusTransition("IN_PROGRESS")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Start Execution (IN_PROGRESS)
                </button>
              )}

              {workOrder.status === "IN_PROGRESS" && (
                <>
                  <button
                    onClick={() => handleStatusTransition("PAUSED")}
                    disabled={loading}
                    className="px-4 py-2 text-xs font-semibold bg-orange-600 hover:bg-orange-500 text-white rounded-lg transition disabled:opacity-50"
                  >
                    Pause Execution (PAUSED)
                  </button>
                  <button
                    onClick={() => handleStatusTransition("COMPLETED")}
                    disabled={loading}
                    className="px-4 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition disabled:opacity-50"
                  >
                    Mark Execution COMPLETED
                  </button>
                </>
              )}

              {workOrder.status === "PAUSED" && (
                <button
                  onClick={() => handleStatusTransition("IN_PROGRESS")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition disabled:opacity-50"
                >
                  Resume Execution (IN_PROGRESS)
                </button>
              )}

              {workOrder.status === "COMPLETED" && (
                <button
                  onClick={() => handleStatusTransition("CLOSED")}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition disabled:opacity-50"
                >
                  Close Work Order (CLOSED)
                </button>
              )}

              {canCancel && (
                <button
                  onClick={handleCancelOrder}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold bg-rose-900/60 hover:bg-rose-800 text-rose-200 border border-rose-700 rounded-lg transition disabled:opacity-50"
                >
                  Cancel Work Order
                </button>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-800">
          <span>Created: {new Date(workOrder.created_at).toLocaleString()}</span>
          <span>Last Updated: {new Date(workOrder.updated_at).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
