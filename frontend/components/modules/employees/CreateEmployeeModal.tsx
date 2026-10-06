"use client";

import React, { useState } from "react";
import { api } from "@/lib/api/client";

interface CreateEmployeeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateEmployeeModal({ isOpen, onClose, onSuccess }: CreateEmployeeModalProps) {
  const [employeeCode, setEmployeeCode] = useState<string>("");
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [roleTitle, setRoleTitle] = useState<string>("CNC Operator");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!employeeCode.trim() || !firstName.trim() || !lastName.trim()) {
      setError("Employee code, first name, and last name are required.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/employees", {
        employee_code: employeeCode.trim(),
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        role_title: roleTitle.trim() || undefined,
        is_active: true,
      });

      setEmployeeCode("");
      setFirstName("");
      setLastName("");
      setRoleTitle("CNC Operator");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Failed to create employee.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-cyan-500 animate-pulse" />
            Add Shop Floor Operator / Employee
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
              Employee ID Code *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. EMP-003"
              value={employeeCode}
              onChange={(e) => setEmployeeCode(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                First Name *
              </label>
              <input
                type="text"
                required
                placeholder="Marcus"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Last Name *
              </label>
              <input
                type="text"
                required
                placeholder="Vance"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Role Title / Specialty
            </label>
            <input
              type="text"
              placeholder="e.g. Lead CNC Operator, Assembly Tech"
              value={roleTitle}
              onChange={(e) => setRoleTitle(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:outline-none focus:border-cyan-500"
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
              {loading ? "Adding..." : "Add Operator"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
