"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Machine } from "@/types";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";
import { CreateMachineModal } from "@/components/modules/machines/CreateMachineModal";
import { EditMachineModal } from "@/components/modules/machines/EditMachineModal";

export default function MachinesPage() {
  const { user } = useAuth();
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showInactive, setShowInactive] = useState<boolean>(false);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);

  const fetchMachines = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const activeOnly = !showInactive;
      const res = await api.get<Machine[]>(`/machines?active_only=${activeOnly}`);
      setMachines(res || []);
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to load machines.");
    } finally {
      setLoading(false);
    }
  }, [showInactive]);

  useEffect(() => {
    fetchMachines();
  }, [fetchMachines]);

  const userRoles = user?.roles?.map((r) => r.name) || [];
  const canManage = userRoles.some((r) => ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"].includes(r));

  const filteredMachines = machines.filter((m) => {
    const matchesSearch =
      !search.trim() ||
      m.machine_code.toLowerCase().includes(search.toLowerCase()) ||
      m.name.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = !statusFilter || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statusBadge = (status: string) => {
    const styles: Record<string, string> = {
      OPERATIONAL: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
      AVAILABLE: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
      IN_USE: "bg-cyan-950/80 text-cyan-300 border-cyan-800 animate-pulse",
      MAINTENANCE: "bg-amber-950/80 text-amber-300 border-amber-800 font-semibold",
      INACTIVE: "bg-rose-950/80 text-rose-300 border-rose-800",
    };
    return (
      <span className={`px-2.5 py-1 text-xs rounded-full border font-medium ${styles[status] || styles.OPERATIONAL}`}>
        {status}
      </span>
    );
  };

  const handleDeactivate = async (machine: Machine) => {
    if (!confirm(`Are you sure you want to deactivate machine ${machine.machine_code}?`)) return;
    try {
      await api.delete(`/machines/${machine.id}`);
      fetchMachines();
    } catch (err: any) {
      alert(err?.error?.message || err?.message || "Failed to deactivate machine.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Machine Management</h1>
            <span className="px-2 py-0.5 text-xs bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-md font-mono">
              SPRINT 4 MODULE
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Manage manufacturing machinery catalog, status monitoring, availability, and shop-floor allocations.
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsCreateOpen(true)}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-cyan-950/50 transition flex items-center gap-2 self-start md:self-auto"
          >
            <span className="text-lg font-bold">+</span> Add Machine
          </button>
        )}
      </div>

      {/* Filter Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Search Machine Code / Name
          </label>
          <input
            type="text"
            placeholder="Search MAC-CNC or milling..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Status Filter
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="OPERATIONAL">OPERATIONAL</option>
            <option value="AVAILABLE">AVAILABLE</option>
            <option value="IN_USE">IN_USE</option>
            <option value="MAINTENANCE">MAINTENANCE</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
        </div>

        <div className="flex items-center gap-2 pt-6">
          <input
            type="checkbox"
            id="show_inactive"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="rounded bg-slate-800 border-slate-700 text-cyan-600 focus:ring-cyan-500 h-4 w-4"
          />
          <label htmlFor="show_inactive" className="text-sm font-medium text-slate-300">
            Show Inactive Machines
          </label>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => {
              setSearch("");
              setStatusFilter("");
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
            <p className="text-sm">Loading machinery catalog...</p>
          </div>
        ) : filteredMachines.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <p className="text-lg font-semibold text-white">No Machines Found</p>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              No manufacturing machines match your search or filter parameters.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4 font-semibold">Machine Code</th>
                  <th className="px-6 py-4 font-semibold">Name / Specification</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Active State</th>
                  <th className="px-6 py-4 font-semibold">Registered</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredMachines.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{m.machine_code}</td>
                    <td className="px-6 py-4 font-medium text-slate-100">{m.name}</td>
                    <td className="px-6 py-4">{statusBadge(m.status)}</td>
                    <td className="px-6 py-4">
                      {m.is_active ? (
                        <span className="text-emerald-400 text-xs font-semibold">ACTIVE</span>
                      ) : (
                        <span className="text-slate-500 text-xs">INACTIVE</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(m.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {canManage && (
                        <>
                          <button
                            onClick={() => setSelectedMachine(m)}
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs rounded-md border border-slate-700 font-medium transition"
                          >
                            Edit
                          </button>
                          {m.is_active && (
                            <button
                              onClick={() => handleDeactivate(m)}
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
      <CreateMachineModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSuccess={() => fetchMachines()}
      />

      <EditMachineModal
        machine={selectedMachine}
        isOpen={!!selectedMachine}
        onClose={() => setSelectedMachine(null)}
        onSuccess={() => fetchMachines()}
      />
    </div>
  );
}
