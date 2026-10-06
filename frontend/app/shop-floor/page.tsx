"use client";

import React, { useState, useEffect, useCallback } from "react";
import { WorkOrder, PaginatedWorkOrders } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";
import { CompleteExecutionModal } from "@/components/modules/shop-floor/CompleteExecutionModal";
import { RecordDowntimeModal } from "@/components/modules/shop-floor/RecordDowntimeModal";

export default function ShopFloorPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [search, setSearch] = useState<string>("");

  // Action Modals
  const [completeOrder, setCompleteOrder] = useState<WorkOrder | null>(null);
  const [downtimeOrder, setDowntimeOrder] = useState<WorkOrder | null>(null);

  const fetchActiveExecutionOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (statusFilter) {
        params.append("status", statusFilter);
      }
      if (search.trim()) {
        params.append("search", search.trim());
      }
      params.append("limit", "50");

      const res = await api.get<PaginatedWorkOrders>(`/work-orders?${params.toString()}`);
      setOrders(res.items || []);
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to load shop floor execution orders.");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

  useEffect(() => {
    fetchActiveExecutionOrders();
  }, [fetchActiveExecutionOrders]);

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canExecute = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "OPERATOR"].includes(r));

  const handleStart = async (order: WorkOrder) => {
    try {
      await api.post(`/work-orders/${order.id}/start`);
      fetchActiveExecutionOrders();
    } catch (err: any) {
      alert(err?.error?.message || err?.message || "Failed to start production execution.");
    }
  };

  const handlePause = async (order: WorkOrder) => {
    const reason = prompt("Enter reason for pausing execution (optional):");
    try {
      await api.post(`/work-orders/${order.id}/pause`, { reason });
      fetchActiveExecutionOrders();
    } catch (err: any) {
      alert(err?.error?.message || err?.message || "Failed to pause production execution.");
    }
  };

  const handleResume = async (order: WorkOrder) => {
    try {
      await api.post(`/work-orders/${order.id}/resume`);
      fetchActiveExecutionOrders();
    } catch (err: any) {
      alert(err?.error?.message || err?.message || "Failed to resume production execution.");
    }
  };

  const statusBadge = (status: string) => {
    const styles: Record<string, string> = {
      DRAFT: "bg-slate-800 text-slate-300 border-slate-700",
      RELEASED: "bg-amber-950/80 text-amber-300 border-amber-800 font-semibold",
      IN_PROGRESS: "bg-cyan-950/80 text-cyan-300 border-cyan-800 animate-pulse font-bold",
      PAUSED: "bg-orange-950/80 text-orange-300 border-orange-800 font-semibold",
      COMPLETED: "bg-emerald-950/80 text-emerald-300 border-emerald-800 font-semibold",
      CLOSED: "bg-slate-800 text-slate-400 border-slate-700",
      CANCELLED: "bg-rose-950/80 text-rose-300 border-rose-800",
    };
    return (
      <span className={`px-2.5 py-1 text-xs rounded-full border ${styles[status] || styles.DRAFT}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Shop Floor Execution Terminal</h1>
            <span className="px-2 py-0.5 text-xs bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-md font-mono">
              SPRINT 5 MODULE
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time execution dashboard for operators to start, pause, complete work orders, and record downtime.
          </p>
        </div>
      </div>

      {/* Filter Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Search WO # / Product
          </label>
          <input
            type="text"
            placeholder="Search WO-2026 or SKU..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Execution Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Execution Statuses</option>
            <option value="RELEASED">RELEASED (Ready to Start)</option>
            <option value="IN_PROGRESS">IN_PROGRESS (Currently Running)</option>
            <option value="PAUSED">PAUSED</option>
            <option value="COMPLETED">COMPLETED</option>
          </select>
        </div>

        <div className="flex items-end col-span-2">
          <button
            onClick={() => {
              setSearch("");
              setStatusFilter("");
            }}
            className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm py-2 px-4 rounded-lg border border-slate-700 transition"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Main Execution Cards Container */}
      <div className="space-y-4">
        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-800 text-rose-300 rounded-xl text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3 bg-slate-900 border border-slate-800 rounded-2xl">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
            <p className="text-sm">Loading active execution orders...</p>
          </div>
        ) : orders.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-3 bg-slate-900 border border-slate-800 rounded-2xl">
            <p className="text-lg font-semibold text-white">No Execution Work Orders Found</p>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              No active work orders match your search or status filters.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {orders.map((order) => {
              const produced = order.produced_quantity || 0;
              const planned = order.planned_quantity || 1;
              const progressPct = order.progress_percentage !== undefined
                ? order.progress_percentage
                : Math.min(100, Math.round((produced / planned) * 100));

              return (
                <div
                  key={order.id}
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-lg text-white">{order.work_order_number}</span>
                        {statusBadge(order.status)}
                        {order.status === "COMPLETED" && (
                          <span
                            className={`px-2.5 py-1 text-xs rounded-full border font-semibold ${
                              order.quality_status === "PASSED"
                                ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                : order.quality_status === "FAILED"
                                ? "bg-rose-950 text-rose-400 border-rose-800"
                                : order.quality_status === "REWORK_REQUIRED"
                                ? "bg-amber-950 text-amber-400 border-amber-800"
                                : "bg-slate-800 text-slate-300 border-slate-700"
                            }`}
                          >
                            QA: {(order.quality_status || "PENDING").replace("_", " ")}
                          </span>
                        )}
                      </div>
                      <span className="text-xs font-semibold uppercase text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800">
                        {order.priority}
                      </span>
                    </div>

                    <div className="text-sm text-slate-300">
                      <div className="font-bold text-white text-base">{order.product?.name || "N/A"}</div>
                      <div className="text-xs text-slate-500 font-mono">
                        SKU: {order.product?.product_code} | Plan: {order.production_plan?.plan_number || "Plan"}
                      </div>
                    </div>

                    {/* Quantity & Progress Bar */}
                    <div className="space-y-1.5 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400 font-medium uppercase tracking-wider">Production Progress</span>
                        <span className="font-mono font-bold text-cyan-400 text-sm">
                          {produced.toLocaleString()} / {planned.toLocaleString()} {order.product?.unit_of_measure || "PCS"} ({progressPct}%)
                        </span>
                      </div>

                      <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 ${
                            order.status === "COMPLETED"
                              ? "bg-emerald-500"
                              : order.status === "IN_PROGRESS"
                              ? "bg-gradient-to-r from-cyan-500 to-blue-500"
                              : "bg-amber-500"
                          }`}
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>
                    </div>

                    {/* Resources & Timestamps */}
                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-800/40 p-3 rounded-xl border border-slate-800">
                      <div>
                        <span className="text-slate-500 block uppercase font-semibold">Assigned Machine</span>
                        <span className="font-medium text-slate-200">
                          {order.assigned_machine ? `${order.assigned_machine.machine_code} [${order.assigned_machine.status}]` : "Unassigned"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 block uppercase font-semibold">Assigned Operator</span>
                        <span className="font-medium text-slate-200">
                          {order.assigned_employee ? `${order.assigned_employee.first_name} ${order.assigned_employee.last_name}` : "Unassigned"}
                        </span>
                      </div>

                      {order.actual_start_time && (
                        <div>
                          <span className="text-slate-500 block uppercase font-semibold">Execution Started</span>
                          <span className="font-mono text-cyan-400">{new Date(order.actual_start_time).toLocaleTimeString()}</span>
                        </div>
                      )}

                      {order.actual_completion_time && (
                        <div>
                          <span className="text-slate-500 block uppercase font-semibold">Completed At</span>
                          <span className="font-mono text-emerald-400">{new Date(order.actual_completion_time).toLocaleTimeString()}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Execution Control Action Buttons */}
                  {canExecute && (
                    <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center gap-2">
                      {order.status === "RELEASED" && (
                        <button
                          onClick={() => handleStart(order)}
                          className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs rounded-lg shadow-md transition"
                        >
                          ▶ Start Execution
                        </button>
                      )}

                      {order.status === "IN_PROGRESS" && (
                        <>
                          <button
                            onClick={() => handlePause(order)}
                            className="px-3 py-1.5 bg-orange-950/80 hover:bg-orange-900 text-orange-300 text-xs font-semibold rounded-lg border border-orange-800 transition"
                          >
                            ⏸ Pause
                          </button>
                          <button
                            onClick={() => setCompleteOrder(order)}
                            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-md transition"
                          >
                            ✓ Complete Execution
                          </button>
                          <button
                            onClick={() => setDowntimeOrder(order)}
                            className="px-3 py-1.5 bg-amber-950/80 hover:bg-amber-900 text-amber-300 text-xs font-semibold rounded-lg border border-amber-800 transition"
                          >
                            ⚠️ Record Downtime
                          </button>
                        </>
                      )}

                      {order.status === "PAUSED" && (
                        <>
                          <button
                            onClick={() => handleResume(order)}
                            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg shadow-md transition"
                          >
                            ▶ Resume Execution
                          </button>
                          <button
                            onClick={() => setCompleteOrder(order)}
                            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-md transition"
                          >
                            ✓ Complete Execution
                          </button>
                          <button
                            onClick={() => setDowntimeOrder(order)}
                            className="px-3 py-1.5 bg-amber-950/80 hover:bg-amber-900 text-amber-300 text-xs font-semibold rounded-lg border border-amber-800 transition"
                          >
                            ⚠️ Record Downtime
                          </button>
                        </>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modals */}
      <CompleteExecutionModal
        workOrder={completeOrder}
        isOpen={!!completeOrder}
        onClose={() => setCompleteOrder(null)}
        onSuccess={() => fetchActiveExecutionOrders()}
      />

      <RecordDowntimeModal
        workOrder={downtimeOrder}
        isOpen={!!downtimeOrder}
        onClose={() => setDowntimeOrder(null)}
        onSuccess={() => fetchActiveExecutionOrders()}
      />
    </div>
  );
}
