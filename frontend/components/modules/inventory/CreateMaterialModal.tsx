"use client";

import React, { useState, useEffect } from "react";
import { X, Package, CheckCircle, AlertCircle } from "lucide-react";
import { Material, MaterialUnit } from "@/types";

interface CreateMaterialModalProps {
  isOpen: boolean;
  onClose: () => void;
  onMaterialSaved: () => void;
  editingMaterial?: Material | null;
}

export default function CreateMaterialModal({
  isOpen,
  onClose,
  onMaterialSaved,
  editingMaterial,
}: CreateMaterialModalProps) {
  const [materialCode, setMaterialCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [unit, setUnit] = useState<MaterialUnit>("PCS");
  const [reorderLevel, setReorderLevel] = useState<number>(10);
  const [initialQuantity, setInitialQuantity] = useState<number>(0);
  const [location, setLocation] = useState("MAIN-WAREHOUSE");
  const [isActive, setIsActive] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (editingMaterial) {
      setMaterialCode(editingMaterial.material_code);
      setName(editingMaterial.name);
      setDescription(editingMaterial.description || "");
      setUnit(editingMaterial.unit);
      setReorderLevel(editingMaterial.reorder_level);
      setIsActive(editingMaterial.is_active);
    } else {
      setMaterialCode("");
      setName("");
      setDescription("");
      setUnit("PCS");
      setReorderLevel(10);
      setInitialQuantity(0);
      setLocation("MAIN-WAREHOUSE");
      setIsActive(true);
    }
    setError(null);
  }, [editingMaterial, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!materialCode.trim() || !name.trim()) {
      setError("Material code and name are required.");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const url = editingMaterial
        ? `http://localhost:8000/api/v1/inventory/materials/${editingMaterial.id}`
        : "http://localhost:8000/api/v1/inventory/materials";

      const method = editingMaterial ? "PATCH" : "POST";

      const bodyData = editingMaterial
        ? {
            name: name.trim(),
            description: description.trim() || undefined,
            unit,
            reorder_level: Number(reorderLevel),
            is_active: isActive,
          }
        : {
            material_code: materialCode.trim().toUpperCase(),
            name: name.trim(),
            description: description.trim() || undefined,
            unit,
            reorder_level: Number(reorderLevel),
            initial_quantity: Number(initialQuantity),
            location: location.trim() || "MAIN-WAREHOUSE",
            is_active: isActive,
          };

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(bodyData),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || data.detail || "Failed to save material");
      }

      onMaterialSaved();
      onClose();
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold">
            <Package className="h-5 w-5 text-cyan-400" />
            <span className="text-slate-100 text-lg">
              {editingMaterial ? "Edit Material Entity" : "New Material Master"}
            </span>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Material Code & Name */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Material Code <span className="text-cyan-400">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. MAT-STEEL-001"
                value={materialCode}
                onChange={(e) => setMaterialCode(e.target.value)}
                disabled={!!editingMaterial}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 disabled:opacity-50"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Material Name <span className="text-cyan-400">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. High Carbon Steel Rod"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
          </div>

          {/* Unit & Reorder Level */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Unit of Measure</label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value as MaterialUnit)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                {["PCS", "KG", "L", "M", "OTHER"].map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Reorder Level Threshold</label>
              <input
                type="number"
                min="0"
                value={reorderLevel}
                onChange={(e) => setReorderLevel(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
          </div>

          {/* Initial Quantity & Location (only for new materials) */}
          {!editingMaterial && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Initial Stock Quantity</label>
                <input
                  type="number"
                  min="0"
                  value={initialQuantity}
                  onChange={(e) => setInitialQuantity(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Storage Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. MAIN-WAREHOUSE"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Description / Notes</label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Material specifications or supplier details..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Active Status */}
          {editingMaterial && (
            <div className="flex items-center space-x-2 pt-1">
              <input
                type="checkbox"
                id="is_active"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="rounded border-slate-800 text-cyan-500 focus:ring-cyan-500"
              />
              <label htmlFor="is_active" className="text-xs text-slate-300">
                Material active for stock transactions
              </label>
            </div>
          )}

          {/* Footer Actions */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all flex items-center space-x-1.5"
            >
              <CheckCircle className="h-4 w-4" />
              <span>{loading ? "Saving..." : editingMaterial ? "Update Material" : "Create Material"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
