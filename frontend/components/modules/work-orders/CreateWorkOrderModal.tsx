"use client";

import React, { useState, useEffect } from "react";
import { ProductionPlan, Product, Machine, Employee, PaginatedProductionPlans } from "@/types";
import { api } from "@/lib/api/client";

interface CreateWorkOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateWorkOrderModal({ isOpen, onClose, onSuccess }: CreateWorkOrderModalProps) {
  const [plans, setPlans] = useState<ProductionPlan[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);

  const [productionPlanId, setProductionPlanId] = useState<string>("");
  const [productId, setProductId] = useState<string>("");
  const [workOrderNumber, setWorkOrderNumber] = useState<string>("");
  const [plannedQuantity, setPlannedQuantity] = useState<number>(100);
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState<string>(
    new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
  );
  const [priority, setPriority] = useState<string>("MEDIUM");
  const [assignedMachineId, setAssignedMachineId] = useState<string>("");
  const [assignedEmployeeId, setAssignedEmployeeId] = useState<string>("");
  const [notes, setNotes] = useState<string>("");

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchDropdownData();
    }
  }, [isOpen]);

  const fetchDropdownData = async () => {
    try {
      const [plansRes, prodsRes, macsRes, empsRes] = await Promise.all([
        api.get<PaginatedProductionPlans>("/production-plans?limit=100"),
        api.get<Product[]>("/products?active_only=true"),
        api.get<Machine[]>("/machines?active_only=true"),
        api.get<Employee[]>("/employees?active_only=true"),
      ]);

      setPlans(plansRes.items || []);
      setProducts(prodsRes || []);
      setMachines(macsRes || []);
      setEmployees(empsRes || []);

      if (plansRes.items && plansRes.items.length > 0) {
        const firstPlan = plansRes.items[0];
        setProductionPlanId(firstPlan.id);
        setProductId(firstPlan.product_id);
        setPlannedQuantity(firstPlan.planned_quantity);
      }
    } catch (err: any) {
      console.error("Failed to load work order form dropdown data:", err);
    }
  };

  const handlePlanChange = (planId: string) => {
    setProductionPlanId(planId);
    const selected = plans.find((p) => p.id === planId);
    if (selected) {
      setProductId(selected.product_id);
      setPlannedQuantity(selected.planned_quantity);
      setStartDate(selected.start_date);
      setDueDate(selected.due_date);
      setPriority(selected.priority);
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
      await api.post("/work-orders", {
        work_order_number: workOrderNumber.trim() || undefined,
        production_plan_id: productionPlanId,
        product_id: productId,
        planned_quantity: Number(plannedQuantity),
        start_date: startDate,
        due_date: dueDate,
        priority,
        notes: notes.trim() || undefined,
        assigned_machine_id: assignedMachineId || undefined,
        assigned_employee_id: assignedEmployeeId || undefined,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to create work order.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-cyan-500 animate-pulse" />
            Create Work Order
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl font-semibold">
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
              Source Production Plan *
            </label>
            <select
              value={productionPlanId}
              onChange={(e) => handlePlanChange(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            >
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.plan_number} — {p.product?.name || p.product_id} ({p.planned_quantity} {p.product?.unit_of_measure})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Custom Work Order #
              </label>
              <input
                type="text"
                placeholder="Auto-generated if empty"
                value={workOrderNumber}
                onChange={(e) => setWorkOrderNumber(e.target.value)}
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

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Priority *
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="URGENT">URGENT</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Assign Machine
              </label>
              <select
                value={assignedMachineId}
                onChange={(e) => setAssignedMachineId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="">Unassigned</option>
                {machines.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.machine_code} ({m.name})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Assign Operator
              </label>
              <select
                value={assignedEmployeeId}
                onChange={(e) => setAssignedEmployeeId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="">Unassigned</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.first_name} {emp.last_name} ({emp.employee_code})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Shop Floor Execution Notes
            </label>
            <textarea
              rows={3}
              placeholder="Special manufacturing instructions, tooling setup requirements..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-400 hover:text-white transition">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-sm font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg shadow-lg shadow-cyan-900/30 transition disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Work Order"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
