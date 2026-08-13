import React from "react";
import {
  Activity,
  Cpu,
  Database,
  Layers,
  ShieldCheck,
  Server,
  Terminal,
  Boxes,
  ClipboardList,
  Wrench,
  Gauge,
  Barcode
} from "lucide-react";

export default function HomePage() {
  const modules = [
    { title: "Authentication & RBAC", code: "MOD-01", icon: ShieldCheck, status: "Configured (Phase 2 Ready)" },
    { title: "Master Data Management", code: "MOD-02", icon: Boxes, status: "Configured (Phase 3 Ready)" },
    { title: "Inventory & Warehouses", code: "MOD-03", icon: Layers, status: "Configured (Phase 4 Ready)" },
    { title: "Production Planning", code: "MOD-04", icon: ClipboardList, status: "Configured (Phase 5 Ready)" },
    { title: "Work Order Management", code: "MOD-05", icon: Wrench, status: "Configured (Phase 6 Ready)" },
    { title: "Machine & Employee Allocation", code: "MOD-06", icon: Cpu, status: "Configured (Phase 7 Ready)" },
    { title: "Shop-Floor Execution", code: "MOD-07", icon: Activity, status: "Configured (Phase 8 Ready)" },
    { title: "Quality & Downtime Analytics", code: "MOD-08", icon: Gauge, status: "Configured (Phase 9/10 Ready)" },
    { title: "QR/Barcode Identification", code: "MOD-09", icon: Barcode, status: "Configured (Phase 12 Ready)" },
  ];

  const techStack = [
    { name: "Next.js 14 App Router", role: "Frontend UI Engine", badge: "React 18" },
    { name: "FastAPI + Pydantic v2", role: "Backend REST API", badge: "Python 3.11" },
    { name: "PostgreSQL 16", role: "Primary Relational DB", badge: "Async SQLAlchemy" },
    { name: "Redis 7", role: "Caching & Messaging", badge: "pub/sub ready" },
    { name: "Alembic", role: "Database Migration Engine", badge: "Versioned" },
    { name: "Docker Compose", role: "Local Orchestration", badge: "Multi-container" },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Header Banner */}
      <section id="hero-banner" className="glass-panel p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 text-xs font-mono">
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
            <span>PHASE 0 & 1 INITIALIZATION COMPLETE</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            Smart Manufacturing Execution System
          </h1>
          <p className="text-slate-300 max-w-3xl text-sm leading-relaxed">
            SmartMES is an enterprise-oriented, modular digital solution designed to orchestrate shop-floor work order execution, inventory flows, quality control, and machine downtime tracking with high reliability.
          </p>
        </div>
      </section>

      {/* Core Technology Stack Grid */}
      <section id="tech-stack-section" className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <Server className="h-5 w-5 text-cyan-400" />
          Configured Technology Stack Foundations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {techStack.map((item, idx) => (
            <div key={idx} className="glass-card p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-100">{item.name}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono border border-slate-700">
                  {item.badge}
                </span>
              </div>
              <p className="text-xs text-slate-400">{item.role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Planned Domain Modules Architecture Grid */}
      <section id="modules-section" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Layers className="h-5 w-5 text-cyan-400" />
            Domain Modules Architecture Breakdown (18 Domains Prepared)
          </h2>
          <span className="text-xs text-slate-400 font-mono">Clean Architecture Isolation</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map((mod, idx) => {
            const IconComponent = mod.icon;
            return (
              <div key={idx} className="glass-card p-5 space-y-3 group hover:border-cyan-800/60 transition-all">
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-lg bg-slate-800/80 text-cyan-400 group-hover:bg-cyan-950 group-hover:text-cyan-300 transition-colors">
                    <IconComponent className="h-5 w-5" />
                  </div>
                  <span className="text-xs font-mono text-slate-500">{mod.code}</span>
                </div>
                <div>
                  <h3 className="font-medium text-slate-200 text-sm">{mod.title}</h3>
                  <span className="text-xs text-emerald-400 font-mono mt-1 inline-block">{mod.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Interactive Quick Links */}
      <section id="quick-links" className="glass-panel p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Terminal className="h-4 w-4 text-cyan-400" />
          Developer Diagnostic Navigation
        </h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <a
            href="/health"
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition-all shadow-md shadow-cyan-600/20"
          >
            Run Interactive Health Diagnostics
          </a>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium border border-slate-700 transition-all"
          >
            Open FastAPI Swagger Documentation
          </a>
        </div>
      </section>
    </div>
  );
}
