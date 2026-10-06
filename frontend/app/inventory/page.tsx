"use client";

import React, { useState, useEffect, useCallback } from "react";
import AppHeaderNav from "@/components/layout/AppHeaderNav";
import CreateMaterialModal from "@/components/modules/inventory/CreateMaterialModal";
import StockOperationModal from "@/components/modules/inventory/StockOperationModal";
import { Material, StockMovement, InventoryDashboardSummary, WorkOrder, MovementType } from "@/types";
import { Boxes, Plus, ArrowRightLeft, AlertTriangle, RefreshCw, Search, Edit3, ShieldAlert, CheckCircle, PackageCheck } from "lucide-react";

export default function InventoryDashboardPage() {
  const [summary, setSummary] = useState<InventoryDashboardSummary | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);

  const [activeTab, setActiveTab] = useState<"MATERIALS" | "LOW_STOCK" | "MOVEMENTS">("MATERIALS");
  const [searchTerm, setSearchTerm] = useState("");
  const [movementTypeFilter, setMovementTypeFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isMaterialModalOpen, setIsMaterialModalOpen] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null);

  const [isStockModalOpen, setIsStockModalOpen] = useState(false);
  const [initialOp, setInitialOp] = useState<MovementType>("RECEIPT");
  const [selectedMatId, setSelectedMatId] = useState<string>("");

  const fetchInventoryData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      // 1. Fetch Dashboard Summary
      const sumRes = await fetch("http://localhost:8000/api/v1/inventory/summary", { headers });
      if (sumRes.ok) {
        const sumData = await sumRes.json();
        setSummary(sumData);
      }

      // 2. Fetch Materials List
      const matRes = await fetch("http://localhost:8000/api/v1/inventory/materials", { headers });
      if (matRes.ok) {
        const matData = await matRes.json();
        setMaterials(matData);
      }

      // 3. Fetch Stock Movements
      let movUrl = "http://localhost:8000/api/v1/inventory/movements?limit=100";
      if (movementTypeFilter !== "ALL") {
        movUrl += `&movement_type=${movementTypeFilter}`;
      }
      const movRes = await fetch(movUrl, { headers });
      if (movRes.ok) {
        const movData = await movRes.json();
        setMovements(movData);
      }

      // 4. Fetch Work Orders for Stock Operations
      const woRes = await fetch("http://localhost:8000/api/v1/work-orders?limit=100", { headers });
      if (woRes.ok) {
        const woData = await woRes.json();
        setWorkOrders(woData.items || []);
      }
    } catch (err: any) {
      setError("Failed to connect to Inventory API service.");
    } finally {
      setLoading(false);
    }
  }, [movementTypeFilter]);

  useEffect(() => {
    fetchInventoryData();
  }, [fetchInventoryData]);

  const handleOpenCreateMaterial = () => {
    setEditingMaterial(null);
    setIsMaterialModalOpen(true);
  };

  const handleOpenEditMaterial = (m: Material) => {
    setEditingMaterial(m);
    setIsMaterialModalOpen(true);
  };

  const handleOpenStockOp = (op: MovementType, matId: string = "") => {
    setInitialOp(op);
    setSelectedMatId(matId);
    setIsStockModalOpen(true);
  };

  const filteredMaterials = materials.filter((m) => {
    if (activeTab === "LOW_STOCK") {
      const avail = m.stock?.available_quantity ?? 0;
      if (avail > m.reorder_level) return false;
    }

    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return m.material_code.toLowerCase().includes(term) || m.name.toLowerCase().includes(term);
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <AppHeaderNav />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Header Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Boxes className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-100">Inventory & Material Tracking</h1>
              <p className="text-xs text-slate-400">
                Material master catalog, real-time stock levels, reservations, receipts, and audit trail logs
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={fetchInventoryData}
              className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            </button>
            <button
              onClick={() => handleOpenStockOp("RECEIPT")}
              className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-2 transition-all"
            >
              <ArrowRightLeft className="h-4 w-4 text-cyan-400" />
              <span>Stock Transaction</span>
            </button>
            <button
              onClick={handleOpenCreateMaterial}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 transition-all flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>New Material</span>
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-center space-x-3">
            <ShieldAlert className="h-5 w-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Summary Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Total Materials</span>
              <Boxes className="h-4 w-4 text-cyan-400" />
            </div>
            <span className="text-2xl font-bold text-slate-100">{summary?.total_materials ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Active Stock Records</span>
              <PackageCheck className="h-4 w-4 text-emerald-400" />
            </div>
            <span className="text-2xl font-bold text-slate-100">{summary?.total_stock_items ?? 0}</span>
          </div>

          <div
            onClick={() => setActiveTab("LOW_STOCK")}
            className="bg-slate-900/80 border border-amber-900/40 p-4 rounded-2xl backdrop-blur-sm cursor-pointer hover:border-amber-600/60 transition-all"
          >
            <div className="flex items-center justify-between text-amber-400 mb-1">
              <span className="text-xs font-medium">Low Stock Warning</span>
              <AlertTriangle className="h-4 w-4 text-amber-400" />
            </div>
            <span className="text-2xl font-bold text-amber-300">{summary?.low_stock_count ?? 0}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Reserved Quantity</span>
              <span className="text-[10px] font-mono font-bold text-blue-400">ALLOCATED</span>
            </div>
            <span className="text-2xl font-bold text-blue-300">{summary?.total_reserved_quantity ?? 0}</span>
          </div>
        </div>

        {/* Tab Controls & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab("MATERIALS")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === "MATERIALS"
                  ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20"
                  : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              All Materials ({materials.length})
            </button>
            <button
              onClick={() => setActiveTab("LOW_STOCK")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                activeTab === "LOW_STOCK"
                  ? "bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20"
                  : "bg-slate-950 text-amber-400/80 hover:text-amber-300 border border-amber-900/40"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Low Stock ({summary?.low_stock_count ?? 0})</span>
            </button>
            <button
              onClick={() => setActiveTab("MOVEMENTS")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === "MOVEMENTS"
                  ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20"
                  : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              Stock Movement Audit Log
            </button>
          </div>

          {/* Search or Movement Filter */}
          {activeTab !== "MOVEMENTS" ? (
            <div className="relative w-full sm:w-64">
              <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search code or material name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Movement Filter:</span>
              <select
                value={movementTypeFilter}
                onChange={(e) => setMovementTypeFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Movement Types</option>
                <option value="RECEIPT">RECEIPT</option>
                <option value="RESERVATION">RESERVATION</option>
                <option value="RELEASE">RELEASE</option>
                <option value="CONSUMPTION">CONSUMPTION</option>
                <option value="ADJUSTMENT">ADJUSTMENT</option>
              </select>
            </div>
          )}
        </div>

        {/* Tab 1 & 2: Materials & Low Stock Tables */}
        {activeTab !== "MOVEMENTS" && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-5 py-3.5">Material Code</th>
                    <th className="px-5 py-3.5">Material Name</th>
                    <th className="px-5 py-3.5">Unit</th>
                    <th className="px-5 py-3.5">Total Qty</th>
                    <th className="px-5 py-3.5">Reserved</th>
                    <th className="px-5 py-3.5">Available</th>
                    <th className="px-5 py-3.5">Reorder Threshold</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {loading ? (
                    <tr>
                      <td colSpan={9} className="text-center py-12 text-slate-500 font-sans">
                        Loading inventory materials...
                      </td>
                    </tr>
                  ) : filteredMaterials.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="text-center py-12 text-slate-500 font-sans">
                        No materials found matching current view filters.
                      </td>
                    </tr>
                  ) : (
                    filteredMaterials.map((m) => {
                      const totalQty = m.stock?.quantity ?? 0;
                      const resQty = m.stock?.reserved_quantity ?? 0;
                      const availQty = m.stock?.available_quantity ?? 0;
                      const isLow = availQty <= m.reorder_level;

                      return (
                        <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-5 py-4 font-bold text-cyan-400 font-mono">{m.material_code}</td>
                          <td className="px-5 py-4 font-sans font-semibold text-slate-100">
                            {m.name}
                            {m.description && (
                              <span className="block text-[11px] text-slate-500 font-normal">{m.description}</span>
                            )}
                          </td>
                          <td className="px-5 py-4 font-bold text-slate-300">{m.unit}</td>
                          <td className="px-5 py-4 font-bold text-slate-100">{totalQty}</td>
                          <td className="px-5 py-4 font-bold text-amber-400">{resQty}</td>
                          <td className="px-5 py-4 font-bold">
                            <span className={isLow ? "text-rose-400 font-extrabold" : "text-emerald-400"}>
                              {availQty}
                            </span>
                          </td>
                          <td className="px-5 py-4 text-slate-400">{m.reorder_level}</td>
                          <td className="px-5 py-4 font-sans">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                m.is_active
                                  ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                  : "bg-slate-800 text-slate-400 border-slate-700"
                              }`}
                            >
                              {m.is_active ? "ACTIVE" : "INACTIVE"}
                            </span>
                          </td>
                          <td className="px-5 py-4 text-right font-sans">
                            <div className="flex items-center justify-end space-x-1.5">
                              <button
                                onClick={() => handleOpenStockOp("RECEIPT", m.id)}
                                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
                                title="Quick Transaction"
                              >
                                Transaction
                              </button>
                              <button
                                onClick={() => handleOpenEditMaterial(m)}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 hover:text-cyan-400 text-slate-400"
                                title="Edit Material"
                              >
                                <Edit3 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Stock Movement Audit Log */}
        {activeTab === "MOVEMENTS" && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-5 py-3.5">Date & Time</th>
                    <th className="px-5 py-3.5">Material</th>
                    <th className="px-5 py-3.5">Movement Type</th>
                    <th className="px-5 py-3.5">Quantity</th>
                    <th className="px-5 py-3.5">Work Order</th>
                    <th className="px-5 py-3.5">Performed By</th>
                    <th className="px-5 py-3.5">Reference / Remarks</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                        Loading stock movement log...
                      </td>
                    </tr>
                  ) : movements.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                        No stock movement audit entries found.
                      </td>
                    </tr>
                  ) : (
                    movements.map((mv) => (
                      <tr key={mv.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-5 py-4 text-slate-400 text-[11px]">
                          {new Date(mv.created_at).toLocaleString()}
                        </td>
                        <td className="px-5 py-4 font-sans font-bold text-slate-100">
                          {mv.material_code || "MAT-N/A"}{" "}
                          <span className="text-slate-400 font-normal">({mv.material_name})</span>
                        </td>
                        <td className="px-5 py-4 font-sans">
                          <span
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                              mv.movement_type === "RECEIPT"
                                ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                : mv.movement_type === "RESERVATION"
                                ? "bg-blue-950 text-blue-400 border-blue-800"
                                : mv.movement_type === "RELEASE"
                                ? "bg-slate-800 text-slate-300 border-slate-700"
                                : mv.movement_type === "CONSUMPTION"
                                ? "bg-rose-950 text-rose-400 border-rose-800"
                                : "bg-amber-950 text-amber-400 border-amber-800"
                            }`}
                          >
                            {mv.movement_type}
                          </span>
                        </td>
                        <td className="px-5 py-4 font-bold text-slate-100">{mv.quantity}</td>
                        <td className="px-5 py-4 text-slate-300 font-sans">{mv.work_order_number || "—"}</td>
                        <td className="px-5 py-4 text-slate-300 font-sans">{mv.performed_by_name || "System"}</td>
                        <td className="px-5 py-4 text-slate-400 font-sans">{mv.reference || "—"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <CreateMaterialModal
        isOpen={isMaterialModalOpen}
        onClose={() => setIsMaterialModalOpen(false)}
        onMaterialSaved={fetchInventoryData}
        editingMaterial={editingMaterial}
      />

      <StockOperationModal
        isOpen={isStockModalOpen}
        onClose={() => setIsStockModalOpen(false)}
        onOperationCompleted={fetchInventoryData}
        materials={materials}
        workOrders={workOrders}
        initialOperation={initialOp}
        initialMaterialId={selectedMatId}
      />
    </div>
  );
}
