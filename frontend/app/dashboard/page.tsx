"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import {
  DashboardSummary,
  ProductionReport,
  QualityReport,
  InventoryReport,
  MachineReport,
  OperatorReport,
} from "@/types";
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Boxes,
  Clock,
  Cpu,
  Download,
  Filter,
  Layers,
  RefreshCw,
  ShieldAlert,
  Users,
  Wrench,
  TrendingUp,
  Activity,
  Calendar,
} from "lucide-react";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "production" | "quality" | "inventory" | "machines" | "operators"
  >("overview");

  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");

  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      let query = "";
      const params = new URLSearchParams();
      if (fromDate) params.append("from_date", fromDate);
      if (toDate) params.append("to_date", toDate);
      if (params.toString()) query = `?${params.toString()}`;

      const data = await api.get<DashboardSummary>(`/reports/dashboard${query}`);
      setSummary(data);
    } catch (err: any) {
      console.error("Failed to load dashboard metrics:", err);
      setError(err?.message || "Failed to load management dashboard metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [fromDate, toDate]);

  // --- CSV Export Helper ---
  const exportToCSV = (filename: string, rows: (string | number)[][], headers: string[]) => {
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.map((val) => `"${val}"`).join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportProductionCSV = () => {
    if (!summary) return;
    const p = summary.production;
    const headers = ["Metric", "Value"];
    const rows = [
      ["Total Work Orders", p.total_work_orders],
      ["Pending (Draft/Released)", p.pending],
      ["In Progress", p.in_progress],
      ["Paused", p.paused],
      ["Completed", p.completed],
      ["Closed", p.closed],
      ["Cancelled", p.cancelled],
      ["Completion Percentage (%)", `${p.completion_percentage}%`],
      ["Total Planned Quantity", p.total_planned_quantity],
      ["Total Produced Quantity", p.total_produced_quantity],
    ];
    exportToCSV(`SmartMES_Production_Report_${new Date().toISOString().split("T")[0]}.csv`, rows, headers);
  };

  const handleExportQualityCSV = () => {
    if (!summary) return;
    const q = summary.quality;
    const headers = ["Metric", "Value"];
    const rows = [
      ["Total Quality Inspections", q.total_inspections],
      ["Pending Inspections", q.pending],
      ["Passed Inspections", q.passed],
      ["Failed Inspections", q.failed],
      ["Rework Required", q.rework_required],
      ["Total Inspected Quantity", q.total_inspected_quantity],
      ["Total Accepted Quantity", q.total_accepted_quantity],
      ["Total Rejected Quantity", q.total_rejected_quantity],
      ["Total Defects Logged", q.total_defects],
    ];
    exportToCSV(`SmartMES_Quality_Report_${new Date().toISOString().split("T")[0]}.csv`, rows, headers);
  };

  const handleExportInventoryCSV = () => {
    if (!summary) return;
    const inv = summary.inventory;
    const headers = ["Material Code", "Name", "Unit", "Available Qty", "Reorder Level", "Status"];
    const rows = inv.low_stock_materials.map((m) => [
      m.material_code,
      m.name,
      m.unit,
      m.stock?.available_quantity ?? 0,
      m.reorder_level,
      "LOW STOCK",
    ]);
    exportToCSV(`SmartMES_Low_Stock_Report_${new Date().toISOString().split("T")[0]}.csv`, rows, headers);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/50">
              <BarChart3 className="h-5 w-5" />
            </span>
            <h1 className="text-2xl font-bold tracking-tight text-white">Management Reports & Analytics</h1>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Consolidated KPIs across Production Execution, Quality Control, Inventory Stocks, Machines, and Operators.
          </p>
        </div>

        {/* Date Filter & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Calendar className="h-3.5 w-3.5 text-slate-400" />
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="bg-transparent text-slate-200 outline-none"
              placeholder="From"
            />
            <span className="text-slate-600">to</span>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="bg-transparent text-slate-200 outline-none"
              placeholder="To"
            />
          </div>

          {(fromDate || toDate) && (
            <button
              onClick={() => {
                setFromDate("");
                setToDate("");
              }}
              className="text-xs text-rose-400 hover:text-rose-300 font-medium px-2 py-1 bg-rose-950/40 border border-rose-800/40 rounded"
            >
              Reset
            </button>
          )}

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-cyan-400 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-800 overflow-x-auto text-sm font-medium">
        {[
          { id: "overview", label: "Overview", icon: BarChart3 },
          { id: "production", label: "Production Report", icon: Wrench },
          { id: "quality", label: "Quality Report", icon: CheckCircle2 },
          { id: "inventory", label: "Inventory Report", icon: Boxes },
          { id: "machines", label: "Machines Report", icon: Cpu },
          { id: "operators", label: "Operators Summary", icon: Users },
        ].map((tab) => {
          const IconComp = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium whitespace-nowrap transition-all text-xs sm:text-sm ${
                isActive
                  ? "border-cyan-400 text-cyan-400 bg-cyan-950/30"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700"
              }`}
            >
              <IconComp className={`h-4 w-4 ${isActive ? "text-cyan-400" : "text-slate-500"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-800 text-rose-300 text-sm flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-rose-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && !summary && (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
          <RefreshCw className="h-8 w-8 text-cyan-400 animate-spin mx-auto" />
          <p className="text-sm">Calculating SmartMES KPI metrics across operational domains...</p>
        </div>
      )}

      {/* Dashboard Contents */}
      {summary && (
        <div className="space-y-8">
          {/* TAB 1: OVERVIEW */}
          {(activeTab === "overview" || activeTab === "production") && (
            <div className="space-y-6">
              {/* Row 1 — Overall KPIs */}
              <div>
                <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                  Row 1 — Overall Key Performance Indicators
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Card 1: Work Orders */}
                  <div className="glass-card p-5 space-y-2 border-l-4 border-l-blue-500">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 font-mono">TOTAL WORK ORDERS</span>
                      <Wrench className="h-5 w-5 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{summary.production.total_work_orders}</div>
                    <p className="text-[11px] text-slate-400">
                      {summary.production.in_progress} In Progress | {summary.production.pending} Pending
                    </p>
                  </div>

                  {/* Card 2: Completed */}
                  <div className="glass-card p-5 space-y-2 border-l-4 border-l-emerald-500">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 font-mono">COMPLETED ORDERS</span>
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{summary.production.completed}</div>
                    <p className="text-[11px] text-emerald-400 font-medium">
                      {summary.production.completion_percentage}% Completion Rate
                    </p>
                  </div>

                  {/* Card 3: Production Quantity */}
                  <div className="glass-card p-5 space-y-2 border-l-4 border-l-cyan-500">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 font-mono">PRODUCED QUANTITY</span>
                      <TrendingUp className="h-5 w-5 text-cyan-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{summary.production.total_produced_quantity}</div>
                    <p className="text-[11px] text-slate-400">
                      Target Planned: {summary.production.total_planned_quantity} PCS
                    </p>
                  </div>

                  {/* Card 4: Low Stock */}
                  <div className="glass-card p-5 space-y-2 border-l-4 border-l-amber-500">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 font-mono">LOW STOCK ITEMS</span>
                      <AlertTriangle className="h-5 w-5 text-amber-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{summary.inventory.low_stock_count}</div>
                    <p className="text-[11px] text-amber-400 font-medium">
                      Out of {summary.inventory.total_materials} Total Materials
                    </p>
                  </div>
                </div>
              </div>

              {/* Row 2 — Production Execution Breakdown */}
              <div className="glass-panel p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                    <Wrench className="h-4 w-4 text-cyan-400" />
                    <span>Row 2 — Production Execution & Status Breakdown</span>
                  </h3>
                  <button
                    onClick={handleExportProductionCSV}
                    className="flex items-center space-x-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700"
                  >
                    <Download className="h-3.5 w-3.5 text-cyan-400" />
                    <span>Export CSV</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">Pending</span>
                    <span className="text-lg font-bold text-amber-400">{summary.production.pending}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">In Progress</span>
                    <span className="text-lg font-bold text-blue-400">{summary.production.in_progress}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">Paused</span>
                    <span className="text-lg font-bold text-orange-400">{summary.production.paused}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">Completed</span>
                    <span className="text-lg font-bold text-emerald-400">{summary.production.completed}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">Closed</span>
                    <span className="text-lg font-bold text-slate-400">{summary.production.closed}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 block">Cancelled</span>
                    <span className="text-lg font-bold text-rose-400">{summary.production.cancelled}</span>
                  </div>
                </div>

                {/* Progress Visual Meter */}
                <div className="space-y-1.5 pt-2">
                  <div className="flex justify-between text-xs text-slate-400 font-mono">
                    <span>Overall Planned Output Progress</span>
                    <span>
                      {summary.production.total_produced_quantity} / {summary.production.total_planned_quantity} PCS (
                      {summary.production.completion_percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-emerald-400 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(
                          100,
                          summary.production.total_planned_quantity > 0
                            ? (summary.production.total_produced_quantity / summary.production.total_planned_quantity) *
                                100
                            : 0
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Row 3 — Quality Control */}
          {(activeTab === "overview" || activeTab === "quality") && (
            <div className="glass-panel p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>Row 3 — Quality Inspection & Control Summary</span>
                </h3>
                <button
                  onClick={handleExportQualityCSV}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700"
                >
                  <Download className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Export CSV</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block font-mono">PASSED INSPECTIONS</span>
                    <span className="text-xl font-bold text-emerald-400">{summary.quality.passed}</span>
                  </div>
                  <CheckCircle2 className="h-6 w-6 text-emerald-500/40" />
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block font-mono">FAILED INSPECTIONS</span>
                    <span className="text-xl font-bold text-rose-400">{summary.quality.failed}</span>
                  </div>
                  <ShieldAlert className="h-6 w-6 text-rose-500/40" />
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block font-mono">REWORK REQUIRED</span>
                    <span className="text-xl font-bold text-amber-400">{summary.quality.rework_required}</span>
                  </div>
                  <AlertTriangle className="h-6 w-6 text-amber-500/40" />
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block font-mono">TOTAL DEFECTS LOGGED</span>
                    <span className="text-xl font-bold text-purple-400">{summary.quality.total_defects}</span>
                  </div>
                  <Activity className="h-6 w-6 text-purple-500/40" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-1">
                  <span className="text-slate-400">Total Quantity Inspected</span>
                  <p className="text-sm font-bold text-white">{summary.quality.total_inspected_quantity} PCS</p>
                </div>
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-1">
                  <span className="text-slate-400">Total Quantity Accepted</span>
                  <p className="text-sm font-bold text-emerald-400">{summary.quality.total_accepted_quantity} PCS</p>
                </div>
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-1">
                  <span className="text-slate-400">Total Quantity Rejected</span>
                  <p className="text-sm font-bold text-rose-400">{summary.quality.total_rejected_quantity} PCS</p>
                </div>
              </div>
            </div>
          )}

          {/* Row 4 — Machines Breakdown */}
          {(activeTab === "overview" || activeTab === "machines") && (
            <div className="glass-panel p-6 space-y-4">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                <Cpu className="h-4 w-4 text-cyan-400" />
                <span>Row 4 — Machine Status Distribution</span>
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Operational / Ready</span>
                  <span className="text-2xl font-bold text-emerald-400">{summary.machines.operational}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">In Use / Active</span>
                  <span className="text-2xl font-bold text-cyan-400">{summary.machines.in_use}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">In Maintenance</span>
                  <span className="text-2xl font-bold text-amber-400">{summary.machines.maintenance}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Inactive / Off</span>
                  <span className="text-2xl font-bold text-slate-400">{summary.machines.inactive}</span>
                </div>
              </div>
            </div>
          )}

          {/* Row 5 — Inventory Stock & Low Stock */}
          {(activeTab === "overview" || activeTab === "inventory") && (
            <div className="space-y-6">
              <div className="glass-panel p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                    <Boxes className="h-4 w-4 text-cyan-400" />
                    <span>Row 5 — Inventory Stock Levels & Low-Stock Alerts</span>
                  </h3>
                  <button
                    onClick={handleExportInventoryCSV}
                    className="flex items-center space-x-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700"
                  >
                    <Download className="h-3.5 w-3.5 text-cyan-400" />
                    <span>Export Low Stock CSV</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-xs text-slate-400 block">Total Materials</span>
                    <span className="text-lg font-bold text-slate-100">{summary.inventory.total_materials}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-xs text-slate-400 block">Total Physical Stock</span>
                    <span className="text-lg font-bold text-cyan-400">{summary.inventory.total_quantity}</span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-xs text-slate-400 block">Reserved Stock</span>
                    <span className="text-lg font-bold text-amber-400">
                      {summary.inventory.total_reserved_quantity}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-xs text-slate-400 block">Available Stock</span>
                    <span className="text-lg font-bold text-emerald-400">
                      {summary.inventory.total_available_quantity}
                    </span>
                  </div>
                </div>

                {/* Low Stock Table */}
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-semibold text-amber-400 flex items-center space-x-1">
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                    <span>Low Stock Action Required ({summary.inventory.low_stock_count})</span>
                  </h4>
                  {summary.inventory.low_stock_materials.length === 0 ? (
                    <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-900/40 text-emerald-400 text-xs">
                      All inventory materials are currently above reorder levels.
                    </div>
                  ) : (
                    <div className="overflow-x-auto border border-slate-800 rounded-lg">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                          <tr>
                            <th className="px-4 py-2">Code</th>
                            <th className="px-4 py-2">Material</th>
                            <th className="px-4 py-2">Unit</th>
                            <th className="px-4 py-2">Available</th>
                            <th className="px-4 py-2">Reorder Level</th>
                            <th className="px-4 py-2">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 text-slate-300">
                          {summary.inventory.low_stock_materials.map((m) => (
                            <tr key={m.id} className="hover:bg-slate-900/50">
                              <td className="px-4 py-2.5 font-mono text-cyan-400">{m.material_code}</td>
                              <td className="px-4 py-2.5 font-medium">{m.name}</td>
                              <td className="px-4 py-2.5 font-mono">{m.unit}</td>
                              <td className="px-4 py-2.5 text-amber-400 font-bold">
                                {m.stock?.available_quantity ?? 0}
                              </td>
                              <td className="px-4 py-2.5 text-slate-400">{m.reorder_level}</td>
                              <td className="px-4 py-2.5">
                                <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60 font-mono text-[10px]">
                                  LOW STOCK
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* Recent Movements Audit */}
                {summary.inventory.recent_movements.length > 0 && (
                  <div className="space-y-3 pt-4 border-t border-slate-800">
                    <h4 className="text-xs font-semibold text-slate-300">Recent Stock Movements</h4>
                    <div className="overflow-x-auto border border-slate-800 rounded-lg">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                          <tr>
                            <th className="px-4 py-2">Timestamp</th>
                            <th className="px-4 py-2">Material</th>
                            <th className="px-4 py-2">Type</th>
                            <th className="px-4 py-2">Quantity</th>
                            <th className="px-4 py-2">Work Order</th>
                            <th className="px-4 py-2">User</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 text-slate-300">
                          {summary.inventory.recent_movements.map((mov) => (
                            <tr key={mov.id} className="hover:bg-slate-900/50">
                              <td className="px-4 py-2 text-slate-400 font-mono text-[11px]">
                                {new Date(mov.created_at).toLocaleString()}
                              </td>
                              <td className="px-4 py-2 font-medium">
                                {mov.material_name || mov.material_code || "Material"}
                              </td>
                              <td className="px-4 py-2">
                                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 font-mono text-[10px]">
                                  {mov.movement_type}
                                </span>
                              </td>
                              <td className="px-4 py-2 font-bold font-mono">{mov.quantity}</td>
                              <td className="px-4 py-2 text-slate-400 font-mono">
                                {mov.work_order_number || "-"}
                              </td>
                              <td className="px-4 py-2 text-slate-400">{mov.performed_by_name || "System"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 6: OPERATORS */}
          {(activeTab === "overview" || activeTab === "operators") && (
            <div className="glass-panel p-6 space-y-4">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                <Users className="h-4 w-4 text-cyan-400" />
                <span>Operator & Workforce Operational Summary</span>
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Total Operators</span>
                  <span className="text-2xl font-bold text-white">{summary.operators.total_operators}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Active Operators</span>
                  <span className="text-2xl font-bold text-emerald-400">{summary.operators.active_operators}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Assigned Operators</span>
                  <span className="text-2xl font-bold text-cyan-400">{summary.operators.assigned_operators}</span>
                </div>
                <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-center space-y-1">
                  <span className="text-xs text-slate-400 block">Available Operators</span>
                  <span className="text-2xl font-bold text-purple-400">{summary.operators.unassigned_operators}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
