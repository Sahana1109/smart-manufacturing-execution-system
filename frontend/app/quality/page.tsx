"use client";

import React, { useState, useEffect, useCallback } from "react";
import AppHeaderNav from "@/components/layout/AppHeaderNav";
import CreateInspectionModal from "@/components/modules/quality/CreateInspectionModal";
import InspectionDetailModal from "@/components/modules/quality/InspectionDetailModal";
import { QualityInspection, QualitySummary, WorkOrder, QualityStatus } from "@/types";
import { ShieldCheck, Plus, AlertCircle, RefreshCw, CheckCircle2, AlertTriangle, XCircle, Search, Eye } from "lucide-react";

export default function QualityDashboardPage() {
  const [summary, setSummary] = useState<QualitySummary | null>(null);
  const [inspections, setInspections] = useState<QualityInspection[]>([]);
  const [completedWorkOrders, setCompletedWorkOrders] = useState<WorkOrder[]>([]);

  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState<QualityInspection | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const fetchQualityData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      // 1. Fetch Summary Metrics
      const sumRes = await fetch("http://localhost:8000/api/v1/quality/summary", { headers });
      if (sumRes.ok) {
        const sumData = await sumRes.json();
        setSummary(sumData);
      }

      // 2. Fetch Inspections List
      let inspectUrl = "http://localhost:8000/api/v1/quality/inspections";
      if (filterStatus !== "ALL") {
        inspectUrl += `?status=${filterStatus}`;
      }
      const inspRes = await fetch(inspectUrl, { headers });
      if (inspRes.ok) {
        const inspData = await inspRes.json();
        setInspections(inspData);
      }

      // 3. Fetch Completed Work Orders for Inspection Creation
      const woRes = await fetch("http://localhost:8000/api/v1/work-orders?status=COMPLETED&limit=100", { headers });
      if (woRes.ok) {
        const woData = await woRes.json();
        setCompletedWorkOrders(woData.items || []);
      }
    } catch (err: any) {
      setError("Failed to load quality assurance data. Ensure backend API is active.");
    } finally {
      setLoading(false);
    }
  }, [filterStatus]);

  useEffect(() => {
    fetchQualityData();
  }, [fetchQualityData]);

  const handleOpenDetailModal = (inspection: QualityInspection) => {
    setSelectedInspection(inspection);
    setIsDetailModalOpen(true);
  };

  const handleRefreshDetail = async () => {
    if (selectedInspection) {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8000/api/v1/quality/inspections/${selectedInspection.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const updated = await res.json();
        setSelectedInspection(updated);
      }
    }
    fetchQualityData();
  };

  const filteredInspections = inspections.filter((ins) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      (ins.work_order_number && ins.work_order_number.toLowerCase().includes(term)) ||
      (ins.product_name && ins.product_name.toLowerCase().includes(term)) ||
      (ins.inspector_name && ins.inspector_name.toLowerCase().includes(term))
    );
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <AppHeaderNav />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <ShieldCheck className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-100">Quality Inspection & Control</h1>
              <p className="text-xs text-slate-400">
                Post-production quality verification, defect management, and compliance auditing
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={fetchQualityData}
              className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            </button>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 transition-all flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Log Quality Inspection</span>
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Summary Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">Pending</span>
              <AlertTriangle className="h-4 w-4 text-slate-400" />
            </div>
            <span className="text-2xl font-bold text-slate-200">{summary?.pending ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-emerald-900/40 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-emerald-400 mb-1">
              <span className="text-[11px] font-medium">Passed</span>
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            </div>
            <span className="text-2xl font-bold text-emerald-300">{summary?.passed ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-rose-900/40 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-rose-400 mb-1">
              <span className="text-[11px] font-medium">Failed</span>
              <XCircle className="h-4 w-4 text-rose-400" />
            </div>
            <span className="text-2xl font-bold text-rose-300">{summary?.failed ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-amber-900/40 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-amber-400 mb-1">
              <span className="text-[11px] font-medium">Rework Req.</span>
              <RefreshCw className="h-4 w-4 text-amber-400" />
            </div>
            <span className="text-2xl font-bold text-amber-300">{summary?.rework_required ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">Rejected Qty</span>
              <span className="text-[10px] font-mono font-bold text-rose-400">SCRAP</span>
            </div>
            <span className="text-2xl font-bold text-rose-400">{summary?.total_rejected_quantity ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">Total Defects</span>
              <span className="text-[10px] font-mono font-bold text-amber-400">ITEMS</span>
            </div>
            <span className="text-2xl font-bold text-amber-400">{summary?.total_defects ?? 0}</span>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80">
          <div className="flex items-center space-x-2 overflow-x-auto w-full sm:w-auto">
            {["ALL", "PENDING", "PASSED", "FAILED", "REWORK_REQUIRED"].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  filterStatus === st
                    ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20"
                    : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {st.replace("_", " ")}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search WO or Product..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Inspection Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-5 py-3.5">Inspection ID</th>
                  <th className="px-5 py-3.5">Work Order</th>
                  <th className="px-5 py-3.5">Product</th>
                  <th className="px-5 py-3.5">Inspector</th>
                  <th className="px-5 py-3.5">Inspected</th>
                  <th className="px-5 py-3.5">Accepted</th>
                  <th className="px-5 py-3.5">Rejected</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Date</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-500 font-sans">
                      Loading quality inspection log...
                    </td>
                  </tr>
                ) : filteredInspections.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-500 font-sans">
                      No quality inspections recorded yet.
                    </td>
                  </tr>
                ) : (
                  filteredInspections.map((ins) => (
                    <tr key={ins.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-5 py-4 font-mono text-[11px] text-slate-400">
                        #{ins.id.substring(0, 8)}
                      </td>
                      <td className="px-5 py-4 font-sans font-bold text-slate-100">
                        {ins.work_order_number || "WO-N/A"}
                      </td>
                      <td className="px-5 py-4 font-sans text-slate-300">
                        {ins.product_name || "Product"}
                      </td>
                      <td className="px-5 py-4 font-sans text-slate-300">
                        {ins.inspector_name || "Quality Team"}
                      </td>
                      <td className="px-5 py-4 font-bold text-slate-200">{ins.inspected_quantity}</td>
                      <td className="px-5 py-4 font-bold text-emerald-400">{ins.accepted_quantity}</td>
                      <td className="px-5 py-4 font-bold text-rose-400">{ins.rejected_quantity}</td>
                      <td className="px-5 py-4 font-sans">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                            ins.status === "PASSED"
                              ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                              : ins.status === "FAILED"
                              ? "bg-rose-950 text-rose-400 border-rose-800"
                              : ins.status === "REWORK_REQUIRED"
                              ? "bg-amber-950 text-amber-400 border-amber-800"
                              : "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          {ins.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-slate-400 text-[11px]">
                        {new Date(ins.inspection_date).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <button
                          onClick={() => handleOpenDetailModal(ins)}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 hover:text-cyan-300 text-slate-300 font-sans font-medium text-xs transition-colors inline-flex items-center space-x-1"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          <span>Details</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Modals */}
      <CreateInspectionModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onInspectionCreated={fetchQualityData}
        completedWorkOrders={completedWorkOrders}
      />

      <InspectionDetailModal
        inspection={selectedInspection}
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        onRefresh={handleRefreshDetail}
      />
    </div>
  );
}
