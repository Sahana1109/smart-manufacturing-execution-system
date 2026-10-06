"use client";

import React, { useState, useEffect, useCallback } from "react";
import { WorkOrder, PaginatedWorkOrders } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";
import { CreateWorkOrderModal } from "@/components/modules/work-orders/CreateWorkOrderModal";
import { WorkOrderDetailsModal } from "@/components/modules/work-orders/WorkOrderDetailsModal";
import { AssignWorkOrderModal } from "@/components/modules/work-orders/AssignWorkOrderModal";

export default function WorkOrdersPage() {
  const { user } = useAuth();
  const [data, setData] = useState<PaginatedWorkOrders | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter States
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState<number>(1);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [selectedOrder, setSelectedOrder] = useState<WorkOrder | null>(null);
  const [assignOrder, setAssignOrder] = useState<WorkOrder | null>(null);

  const fetchWorkOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      if (priorityFilter) params.append("priority", priorityFilter);
      if (search.trim()) params.append("search", search.trim());
      params.append("page", page.toString());
      params.append("limit", "10");

      const res = await api.get<PaginatedWorkOrders>(`/work-orders?${params.toString()}`);
      setData(res);
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to load work orders.");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter, search, page]);

  useEffect(() => {
    fetchWorkOrders();
  }, [fetchWorkOrders]);

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canCreate = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER"].includes(r));
  const canAssign = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"].includes(r));

  const statusBadge = (status: string) => {
    const styles: Record<string, string> = {
      DRAFT: "bg-slate-800 text-slate-300 border-slate-700",
      RELEASED: "bg-amber-950/80 text-amber-300 border-amber-800",
      IN_PROGRESS: "bg-cyan-950/80 text-cyan-300 border-cyan-800 animate-pulse",
      PAUSED: "bg-orange-950/80 text-orange-300 border-orange-800",
      COMPLETED: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
      CLOSED: "bg-slate-800 text-slate-400 border-slate-700",
      CANCELLED: "bg-rose-950/80 text-rose-300 border-rose-800",
    };
    return (
      <span className={`px-2.5 py-1 text-xs rounded-full border font-medium ${styles[status] || styles.DRAFT}`}>
        {status}
      </span>
    );
  };

  const qualityBadge = (qStatus?: string) => {
    const status = qStatus || "PENDING";
    const styles: Record<string, string> = {
      PENDING: "bg-slate-800 text-slate-300 border-slate-700",
      PASSED: "bg-emerald-950 text-emerald-400 border-emerald-800",
      FAILED: "bg-rose-950 text-rose-400 border-rose-800",
      REWORK_REQUIRED: "bg-amber-950 text-amber-400 border-amber-800",
    };
    return (
      <span className={`px-2 py-0.5 text-[10px] rounded-md border font-semibold ${styles[status] || styles.PENDING}`}>
        QA: {status.replace("_", " ")}
      </span>
    );
  };

  const priorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      LOW: "text-slate-400",
      MEDIUM: "text-blue-400 font-medium",
      HIGH: "text-purple-400 font-semibold",
      URGENT: "text-rose-400 font-bold tracking-wide",
    };
    return <span className={styles[priority] || "text-slate-400"}>{priority}</span>;
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Work Order Management</h1>
            <span className="px-2 py-0.5 text-xs bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-md font-mono">
              SPRINT 3 MODULE
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Dispatch, assign machinery/operators, monitor execution, and control work order lifecycles.
          </p>
        </div>

        {canCreate && (
          <button
            onClick={() => setIsCreateOpen(true)}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-cyan-950/50 transition flex items-center gap-2 self-start md:self-auto"
          >
            <span className="text-lg font-bold">+</span> Create Work Order
          </button>
        )}
      </div>

      {/* Filter Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Search Work Order / Product
          </label>
          <input
            type="text"
            placeholder="Search WO-2026 or SKU..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Status Filter
          </label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="RELEASED">RELEASED</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="PAUSED">PAUSED</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="CLOSED">CLOSED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>

        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Priority Filter
          </label>
          <select
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Priorities</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="URGENT">URGENT</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => {
              setSearch("");
              setStatusFilter("");
              setPriorityFilter("");
              setPage(1);
            }}
            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm py-2 px-4 rounded-lg border border-slate-700 transition"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {error && (
          <div className="p-4 bg-rose-950/80 border-b border-rose-800 text-rose-300 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
            <p className="text-sm">Loading work orders...</p>
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <p className="text-lg font-semibold text-white">No Work Orders Found</p>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              No manufacturing work orders match your active filters or search parameters.
            </p>
            {canCreate && (
              <button
                onClick={() => setIsCreateOpen(true)}
                className="mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm rounded-lg font-semibold transition"
              >
                + Create First Work Order
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4 font-semibold">Work Order #</th>
                  <th className="px-6 py-4 font-semibold">Plan & Product SKU</th>
                  <th className="px-6 py-4 font-semibold">Planned Qty</th>
                  <th className="px-6 py-4 font-semibold">Machine / Operator</th>
                  <th className="px-6 py-4 font-semibold">Target Dates</th>
                  <th className="px-6 py-4 font-semibold">Priority</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data.items.map((order) => (
                  <tr
                    key={order.id}
                    className="hover:bg-slate-800/40 transition cursor-pointer"
                    onClick={() => setSelectedOrder(order)}
                  >
                    <td className="px-6 py-4 font-mono font-bold text-white">
                      {order.work_order_number}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{order.product?.name || "N/A"}</div>
                      <div className="text-xs text-slate-500 font-mono">
                        Plan: {order.production_plan?.plan_number || "Plan"} | {order.product?.product_code}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-cyan-400">
                      {order.planned_quantity.toLocaleString()} {order.product?.unit_of_measure || "PCS"}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <div>
                        Mac: <span className="text-slate-200 font-medium">{order.assigned_machine?.machine_code || "Unassigned"}</span>
                      </div>
                      <div>
                        Op: <span className="text-slate-200 font-medium">{order.assigned_employee ? `${order.assigned_employee.first_name} ${order.assigned_employee.last_name}` : "Unassigned"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-300">
                      <div>Start: {order.start_date}</div>
                      <div>Due: {order.due_date}</div>
                    </td>
                    <td className="px-6 py-4">{priorityBadge(order.priority)}</td>
                    <td className="px-6 py-4 space-y-1">
                      <div>{statusBadge(order.status)}</div>
                      {order.status === "COMPLETED" && (
                        <div>{qualityBadge(order.quality_status)}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                      {canAssign && order.status !== "CLOSED" && order.status !== "CANCELLED" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setAssignOrder(order);
                          }}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-md border border-slate-700 font-medium transition"
                        >
                          Assign
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedOrder(order);
                        }}
                        className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs rounded-md border border-slate-700 font-medium transition"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {data && data.pages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-slate-800 text-xs text-slate-400">
            <div>
              Showing page <span className="text-white font-medium">{data.page}</span> of{" "}
              <span className="text-white font-medium">{data.pages}</span> ({data.total} total orders)
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-white rounded-md transition"
              >
                Previous
              </button>
              <button
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-white rounded-md transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      <CreateWorkOrderModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSuccess={() => fetchWorkOrders()}
      />

      <WorkOrderDetailsModal
        workOrder={selectedOrder}
        isOpen={!!selectedOrder}
        onClose={() => setSelectedOrder(null)}
        onRefresh={() => fetchWorkOrders()}
        onOpenAssign={() => {
          if (selectedOrder) setAssignOrder(selectedOrder);
        }}
      />

      <AssignWorkOrderModal
        workOrder={assignOrder}
        isOpen={!!assignOrder}
        onClose={() => setAssignOrder(null)}
        onSuccess={() => fetchWorkOrders()}
      />
    </div>
  );
}
