"use client";

import React, { useState, useEffect } from "react";
import { Activity, Database, Server, RefreshCw, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";

interface HealthDetails {
  app?: {
    name: string;
    environment: string;
  };
  database?: {
    connected: boolean;
    details: string;
  };
  redis?: {
    connected: boolean;
    details: string;
  };
  error?: string;
}

interface HealthStatus {
  appStatus: "loading" | "healthy" | "error";
  dbStatus: "loading" | "healthy" | "unhealthy" | "error";
  redisStatus: "loading" | "healthy" | "unhealthy" | "error";
  details: HealthDetails | null;
}

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus>({
    appStatus: "loading",
    dbStatus: "loading",
    redisStatus: "loading",
    details: null,
  });

  const fetchHealth = async () => {
    setHealth({
      appStatus: "loading",
      dbStatus: "loading",
      redisStatus: "loading",
      details: null,
    });

    try {
      const res = await fetch("/api/v1/health/full");
      if (!res.ok) throw new Error("HTTP error " + res.status);
      const json = await res.json();
      setHealth({
        appStatus: json.data?.app ? "healthy" : "error",
        dbStatus: json.data?.database?.connected ? "healthy" : "unhealthy",
        redisStatus: json.data?.redis?.connected ? "healthy" : "unhealthy",
        details: json.data,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to reach backend API endpoint";
      setHealth({
        appStatus: "error",
        dbStatus: "error",
        redisStatus: "error",
        details: { error: errorMessage },
      });
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const renderBadge = (status: string) => {
    if (status === "loading") {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 text-xs font-mono">
          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
          Checking...
        </span>
      );
    }
    if (status === "healthy") {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 text-xs font-mono">
          <CheckCircle2 className="h-3.5 w-3.5" />
          ONLINE / HEALTHY
        </span>
      );
    }
    if (status === "unhealthy") {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-950/80 text-amber-400 border border-amber-800/60 text-xs font-mono">
          <AlertTriangle className="h-3.5 w-3.5" />
          SERVICE OFFLINE / UNREACHABLE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-950/80 text-rose-400 border border-rose-800/60 text-xs font-mono">
        <XCircle className="h-3.5 w-3.5" />
        ERROR
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="h-6 w-6 text-cyan-400" />
            System Health & Diagnostic Monitor
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time status of FastAPI Backend, PostgreSQL Database, and Redis Cache.
          </p>
        </div>
        <button
          onClick={fetchHealth}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition-all"
        >
          <RefreshCw className="h-4 w-4" />
          Re-Check Status
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Backend API Health Card */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/50">
                <Server className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-200 text-sm">FastAPI Backend</h3>
                <span className="text-xs text-slate-400 font-mono">Port 8000</span>
              </div>
            </div>
            {renderBadge(health.appStatus)}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            REST API application layer running on Python 3.11 & FastAPI.
          </p>
        </div>

        {/* PostgreSQL Health Card */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-950 text-blue-400 border border-blue-800/50">
                <Database className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-200 text-sm">PostgreSQL 16</h3>
                <span className="text-xs text-slate-400 font-mono">Port 5432</span>
              </div>
            </div>
            {renderBadge(health.dbStatus)}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Relational storage managed with Async SQLAlchemy & Alembic.
          </p>
        </div>

        {/* Redis Health Card */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-950 text-indigo-400 border border-indigo-800/50">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-200 text-sm">Redis 7</h3>
                <span className="text-xs text-slate-400 font-mono">Port 6379</span>
              </div>
            </div>
            {renderBadge(health.redisStatus)}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            In-memory data store for caching and pub/sub message routing.
          </p>
        </div>
      </div>

      {/* Raw Diagnostic Output */}
      {health.details && (
        <div className="glass-panel p-6 space-y-3">
          <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">
            Diagnostic Response Payload
          </h3>
          <pre className="p-4 rounded-lg bg-slate-950 font-mono text-xs text-cyan-300 border border-slate-800 overflow-x-auto">
            {JSON.stringify(health.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
