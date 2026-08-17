"use client";

import React, { useState, useEffect } from "react";
import { Product } from "@/types";
import { api } from "@/lib/api/client";

interface CreatePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreatePlanModal({ isOpen, onClose, onSuccess }: CreatePlanModalProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState<string>("");
  const [planNumber, setPlanNumber] = useState<string>("");
  const [plannedQuantity, setPlannedQuantity] = useState<number>(100);
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState<string>(
    new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
  );
  const [priority, setPriority] = useState<string>("MEDIUM");
  const [notes, setNotes] = useState<string>("");

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchProducts();
    }
  }, [isOpen]);

  const fetchProducts = async () => {
    try {
      const data = await api.get<Product[]>("/products?active_only=true");
      setProducts(data);
      if (data.length > 0 && !productId) {
        setProductId(data[0].id);
      }
    } catch (err: any) {
      console.error("Failed to load products:", err);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (plannedQuantity <= 0) {
      setError("Planned quantity must be greater than 0.");
      return;
    }

    if (new Date(startDate) > new Date(dueDate)) {
      setError("Due date cannot be earlier than start date.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/production-plans", {
        plan_number: planNumber.trim() || undefined,
        product_id: productId,
        planned_quantity: Number(plannedQuantity),
        start_date: startDate,
        due_date: dueDate,
        priority,
        notes: notes.trim() || undefined,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to create production plan.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-cyan-500 animate-pulse" />
            Create Production Plan
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-xl font-semibold"
          >
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
              Target Product SKU *
            </label>
            <select
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.product_code} — {p.name} ({p.unit_of_measure})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Custom Plan Number
              </label>
              <input
                type="text"
                placeholder="Auto-generated if empty"
                value={planNumber}
                onChange={(e) => setPlanNumber(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Planned Quantity *
              </label>
              <input
                type="number"
                min="1"
                required
                value={plannedQuantity}
                onChange={(e) => setPlannedQuantity(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Start Date *
              </label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Due Date *
              </label>
              <input
                type="date"
                required
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Schedule Priority *
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            >
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="URGENT">URGENT</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Operational Notes
            </label>
            <textarea
              rows={3}
              placeholder="Add schedule notes or client requirements..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-sm font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg shadow-lg shadow-cyan-900/30 transition disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Plan"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
