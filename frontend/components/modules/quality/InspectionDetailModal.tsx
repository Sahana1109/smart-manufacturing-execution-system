"use client";

import React, { useState } from "react";
import { X, Plus, Trash2, Edit3, ShieldAlert, CheckCircle, AlertTriangle, Info } from "lucide-react";
import { QualityInspection, QualityDefect, DefectType, DefectSeverity } from "@/types";

interface InspectionDetailModalProps {
  inspection: QualityInspection | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
}

export default function InspectionDetailModal({
  inspection,
  isOpen,
  onClose,
  onRefresh,
}: InspectionDetailModalProps) {
  const [showAddDefect, setShowAddDefect] = useState(false);
  const [editingDefectId, setEditingDefectId] = useState<string | null>(null);

  // Defect Form State
  const [defectType, setDefectType] = useState<DefectType>("SURFACE");
  const [severity, setSeverity] = useState<DefectSeverity>("MEDIUM");
  const [description, setDescription] = useState("");
  const [quantity, setQuantity] = useState<number>(1);
  const [defectRemarks, setDefectRemarks] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !inspection) return null;

  const resetDefectForm = () => {
    setDefectType("SURFACE");
    setSeverity("MEDIUM");
    setDescription("");
    setQuantity(1);
    setDefectRemarks("");
    setShowAddDefect(false);
    setEditingDefectId(null);
    setError(null);
  };

  const handleStartEditDefect = (d: QualityDefect) => {
    setEditingDefectId(d.id);
    setDefectType(d.defect_type);
    setSeverity(d.severity);
    setDescription(d.description || "");
    setQuantity(d.quantity);
    setDefectRemarks(d.remarks || "");
    setShowAddDefect(true);
  };

  const handleSaveDefect = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const url = editingDefectId
        ? `http://localhost:8000/api/v1/quality/defects/${editingDefectId}`
        : `http://localhost:8000/api/v1/quality/inspections/${inspection.id}/defects`;

      const method = editingDefectId ? "PATCH" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          defect_type: defectType,
          severity,
          description: description.trim() || undefined,
          quantity: Number(quantity),
          remarks: defectRemarks.trim() || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || data.detail || "Failed to save defect entry");
      }

      resetDefectForm();
      onRefresh();
    } catch (err: any) {
      setError(err.message || "An error occurred while saving defect");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDefect = async (defectId: string) => {
    if (!confirm("Are you sure you want to delete this defect record?")) return;
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8000/api/v1/quality/defects/${defectId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error?.message || data.detail || "Failed to delete defect");
      }

      onRefresh();
    } catch (err: any) {
      alert(err.message || "Error deleting defect");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Inspection Details — {inspection.work_order_number || "Work Order"}
              </h3>
              <p className="text-xs text-slate-400">
                Product: <span className="text-slate-200">{inspection.product_name || "N/A"}</span> | Inspected:{" "}
                {new Date(inspection.inspection_date).toLocaleDateString()}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Summary Metric Strip */}
          <div className="grid grid-cols-4 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <div>
              <span className="block text-[11px] text-slate-400">Inspected Qty</span>
              <span className="text-lg font-bold text-slate-100">{inspection.inspected_quantity}</span>
            </div>
            <div>
              <span className="block text-[11px] text-emerald-400 font-medium">Accepted Qty</span>
              <span className="text-lg font-bold text-emerald-300">{inspection.accepted_quantity}</span>
            </div>
            <div>
              <span className="block text-[11px] text-rose-400 font-medium">Rejected Qty</span>
              <span className="text-lg font-bold text-rose-300">{inspection.rejected_quantity}</span>
            </div>
            <div>
              <span className="block text-[11px] text-slate-400">Verdict</span>
              <span
                className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold border mt-1 ${
                  inspection.status === "PASSED"
                    ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                    : inspection.status === "FAILED"
                    ? "bg-rose-950 text-rose-400 border-rose-800"
                    : inspection.status === "REWORK_REQUIRED"
                    ? "bg-amber-950 text-amber-400 border-amber-800"
                    : "bg-slate-800 text-slate-300 border-slate-700"
                }`}
              >
                {inspection.status.replace("_", " ")}
              </span>
            </div>
          </div>

          {/* Inspector Remarks */}
          {inspection.remarks && (
            <div className="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-300">
              <span className="font-semibold text-slate-400 block mb-1">Remarks:</span>
              <p>{inspection.remarks}</p>
            </div>
          )}

          {/* Defect Management Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h4 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                <span>Recorded Quality Defects ({inspection.defects?.length || 0})</span>
              </h4>
              {!showAddDefect && (
                <button
                  onClick={() => {
                    resetDefectForm();
                    setShowAddDefect(true);
                  }}
                  className="px-3 py-1.5 rounded-xl bg-cyan-950 border border-cyan-800/80 hover:bg-cyan-900 text-cyan-300 text-xs font-semibold flex items-center space-x-1 transition-all"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Defect</span>
                </button>
              )}
            </div>

            {/* Add / Edit Defect Form */}
            {showAddDefect && (
              <form onSubmit={handleSaveDefect} className="bg-slate-950 p-4 rounded-xl border border-cyan-900/60 space-y-3">
                <h5 className="text-xs font-bold text-cyan-400">
                  {editingDefectId ? "Edit Defect Record" : "Record New Defect"}
                </h5>

                {error && (
                  <p className="text-xs text-rose-400 bg-rose-950/50 p-2 rounded border border-rose-800">{error}</p>
                )}

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Defect Category</label>
                    <select
                      value={defectType}
                      onChange={(e) => setDefectType(e.target.value as DefectType)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                    >
                      {["DIMENSIONAL", "SURFACE", "MATERIAL", "ASSEMBLY", "FUNCTIONAL", "COSMETIC", "OTHER"].map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Severity Level</label>
                    <select
                      value={severity}
                      onChange={(e) => setSeverity(e.target.value as DefectSeverity)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                    >
                      {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Defect Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={quantity}
                      onChange={(e) => setQuantity(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Description</label>
                  <input
                    type="text"
                    placeholder="e.g. Scratched surface near mounting hole"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200"
                  />
                </div>

                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    type="button"
                    onClick={resetDefectForm}
                    className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold"
                  >
                    {loading ? "Saving..." : "Save Defect"}
                  </button>
                </div>
              </form>
            )}

            {/* Defect Table / List */}
            {(!inspection.defects || inspection.defects.length === 0) ? (
              <div className="text-center py-6 border border-dashed border-slate-800 rounded-xl">
                <CheckCircle className="h-8 w-8 text-slate-600 mx-auto mb-2" />
                <p className="text-xs text-slate-400">No defects recorded for this inspection.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {inspection.defects.map((def) => (
                  <div
                    key={def.id}
                    className="flex items-center justify-between bg-slate-950/80 border border-slate-800 p-3 rounded-xl hover:border-slate-700 transition-all"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px] text-slate-300 font-bold">
                          {def.defect_type}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            def.severity === "CRITICAL"
                              ? "bg-rose-950 text-rose-300 border-rose-800"
                              : def.severity === "HIGH"
                              ? "bg-amber-950 text-amber-300 border-amber-800"
                              : "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          {def.severity}
                        </span>
                        <span className="text-xs text-slate-200 font-semibold">Qty: {def.quantity}</span>
                      </div>
                      {def.description && <p className="text-xs text-slate-300">{def.description}</p>}
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleStartEditDefect(def)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 hover:text-cyan-400 text-slate-400"
                        title="Edit Defect"
                      >
                        <Edit3 className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteDefect(def.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 hover:text-rose-400 text-slate-400"
                        title="Delete Defect"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
