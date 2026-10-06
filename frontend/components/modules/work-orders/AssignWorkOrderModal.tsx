"use client";

import React, { useState, useEffect } from "react";
import { WorkOrder, Machine, Employee } from "@/types";
import { api } from "@/lib/api/client";

interface AssignWorkOrderModalProps {
  workOrder: WorkOrder | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AssignWorkOrderModal({ workOrder, isOpen, onClose, onSuccess }: AssignWorkOrderModalProps) {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);

  const [assignedMachineId, setAssignedMachineId] = useState<string>("");
  const [assignedEmployeeId, setAssignedEmployeeId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && workOrder) {
      setAssignedMachineId(workOrder.assigned_machine_id || "");
      setAssignedEmployeeId(workOrder.assigned_employee_id || "");
      fetchAssignOptions();
    }
  }, [isOpen, workOrder]);

  const fetchAssignOptions = async () => {
    try {
      const [macsRes, empsRes] = await Promise.all([
        api.get<Machine[]>("/machines?active_only=true"),
        api.get<Employee[]>("/employees?active_only=true"),
      ]);
      setMachines(macsRes || []);
      setEmployees(empsRes || []);
    } catch (err: any) {
      console.error("Failed to load assignment options:", err);
    }
  };

  if (!isOpen || !workOrder) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await api.patch(`/work-orders/${workOrder.id}/assign`, {
        assigned_machine_id: assignedMachineId || undefined,
        assigned_employee_id: assignedEmployeeId || undefined,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to assign work order resources.");
    } finally {
      setLoading(false);
    }
  };

  const handleUnassignMachine = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/work-orders/${workOrder.id}/assign/machine`);
      setAssignedMachineId("");
      onSuccess();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to unassign machine.");
    } finally {
      setLoading(false);
    }
  };

  const handleUnassignEmployee = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/work-orders/${workOrder.id}/assign/employee`);
      setAssignedEmployeeId("");
      onSuccess();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to unassign operator.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Resource Allocation — {workOrder.work_order_number}
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
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Select Shop Floor Machine
              </label>
              {workOrder.assigned_machine_id && (
                <button
                  type="button"
                  onClick={handleUnassignMachine}
                  disabled={loading}
                  className="text-xs text-rose-400 hover:text-rose-300 underline font-medium"
                >
                  Unassign Machine
                </button>
              )}
            </div>
            <select
              value={assignedMachineId}
              onChange={(e) => setAssignedMachineId(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            >
              <option value="">-- No Machine Assigned --</option>
              {machines.map((m) => (
                <option
                  key={m.id}
                  value={m.id}
                  disabled={m.status === "MAINTENANCE" || m.status === "INACTIVE"}
                >
                  {m.machine_code} — {m.name} [{m.status}]
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Select Assigned Operator / Employee
              </label>
              {workOrder.assigned_employee_id && (
                <button
                  type="button"
                  onClick={handleUnassignEmployee}
                  disabled={loading}
                  className="text-xs text-rose-400 hover:text-rose-300 underline font-medium"
                >
                  Unassign Operator
                </button>
              )}
            </div>
            <select
              value={assignedEmployeeId}
              onChange={(e) => setAssignedEmployeeId(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            >
              <option value="">-- No Operator Assigned --</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.first_name} {emp.last_name} ({emp.employee_code}) — {emp.role_title || "Operator"}
                </option>
              ))}
            </select>
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
              {loading ? "Saving..." : "Save Resource Assignment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
