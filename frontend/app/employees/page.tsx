"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Employee } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";
import { CreateEmployeeModal } from "@/components/modules/employees/CreateEmployeeModal";
import { EditEmployeeModal } from "@/components/modules/employees/EditEmployeeModal";

export default function EmployeesPage() {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState<string>("");
  const [showInactive, setShowInactive] = useState<boolean>(false);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  const fetchEmployees = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const activeOnly = !showInactive;
      const res = await api.get<Employee[]>(`/employees?active_only=${activeOnly}`);
      setEmployees(res || []);
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to load employees.");
    } finally {
      setLoading(false);
    }
  }, [showInactive]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canManage = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER"].includes(r));

  const filteredEmployees = employees.filter((e) => {
    return (
      !search.trim() ||
      e.employee_code.toLowerCase().includes(search.toLowerCase()) ||
      `${e.first_name} ${e.last_name}`.toLowerCase().includes(search.toLowerCase()) ||
      (e.role_title && e.role_title.toLowerCase().includes(search.toLowerCase()))
    );
  });

  const handleDeactivate = async (employee: Employee) => {
    if (!confirm(`Are you sure you want to deactivate operator ${employee.employee_code}?`)) return;
    try {
      await api.delete(`/employees/${employee.id}`);
      fetchEmployees();
    } catch (err: any) {
      alert(err?.error?.message || err?.message || "Failed to deactivate employee.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Operator & Employee Directory</h1>
            <span className="px-2 py-0.5 text-xs bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-md font-mono">
              SPRINT 4 MODULE
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Shop-floor operator registry, specialties, roles, and work-order assignment eligibility.
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsCreateOpen(true)}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-cyan-950/50 transition flex items-center gap-2 self-start md:self-auto"
          >
            <span className="text-lg font-bold">+</span> Add Operator
          </button>
        )}
      </div>

      {/* Filter Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Search Code / Name / Specialty
          </label>
          <input
            type="text"
            placeholder="Search EMP-001 or Vance..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2 pt-6">
          <input
            type="checkbox"
            id="show_inactive_emp"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="rounded bg-slate-800 border-slate-700 text-cyan-600 focus:ring-cyan-500 h-4 w-4"
          />
          <label htmlFor="show_inactive_emp" className="text-sm font-medium text-slate-300">
            Show Inactive Personnel
          </label>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => {
              setSearch("");
              setShowInactive(false);
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
            <p className="text-sm">Loading operator directory...</p>
          </div>
        ) : filteredEmployees.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <p className="text-lg font-semibold text-white">No Operators Found</p>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              No shop-floor personnel match your search or filter parameters.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4 font-semibold">Employee ID</th>
                  <th className="px-6 py-4 font-semibold">Full Name</th>
                  <th className="px-6 py-4 font-semibold">Role / Specialty</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Registered</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredEmployees.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{e.employee_code}</td>
                    <td className="px-6 py-4 font-medium text-slate-100">
                      {e.first_name} {e.last_name}
                    </td>
                    <td className="px-6 py-4 text-cyan-400 font-medium">
                      {e.role_title || "Shop Floor Operator"}
                    </td>
                    <td className="px-6 py-4">
                      {e.is_active ? (
                        <span className="px-2.5 py-1 text-xs rounded-full border bg-emerald-950/80 text-emerald-300 border-emerald-800 font-medium">
                          ACTIVE
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 text-xs rounded-full border bg-rose-950/80 text-rose-300 border-rose-800 font-medium">
                          INACTIVE
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(e.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {canManage && (
                        <>
                          <button
                            onClick={() => setSelectedEmployee(e)}
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs rounded-md border border-slate-700 font-medium transition"
                          >
                            Edit
                          </button>
                          {e.is_active && (
                            <button
                              onClick={() => handleDeactivate(e)}
                              className="px-3 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-300 text-xs rounded-md border border-rose-800 font-medium transition"
                            >
                              Deactivate
                            </button>
                          )}
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modals */}
      <CreateEmployeeModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSuccess={() => fetchEmployees()}
      />

      <EditEmployeeModal
        employee={selectedEmployee}
        isOpen={!!selectedEmployee}
        onClose={() => setSelectedEmployee(null)}
        onSuccess={() => fetchEmployees()}
      />
    </div>
  );
}
