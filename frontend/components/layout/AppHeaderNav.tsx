"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { LogOut, User as UserIcon, Shield } from "lucide-react";

export default function AppHeaderNav() {
  const { user, logout } = useAuth();

  const primaryRole = user?.roles?.[0]?.name || "USER";

  return (
    <header id="main-header" className="border-b border-slate-800/80 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="font-mono font-bold text-white text-lg">M</span>
            </div>
            <div>
              <span className="font-bold text-lg text-slate-100 tracking-tight">
                SMART<span className="text-cyan-400">MES</span>
              </span>
              <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                v0.1.0
              </span>
            </div>
          </Link>
        </div>

        <nav id="header-nav" className="flex items-center space-x-6 text-sm font-medium">
          <Link href="/" className="text-cyan-400 transition-colors hover:text-cyan-300">
            Overview
          </Link>
          <Link href="/health" className="text-slate-400 hover:text-slate-200 transition-colors">
            Diagnostics
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            API Docs
          </a>

          {user ? (
            <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
              <div className="flex items-center space-x-2 bg-slate-950/80 border border-slate-800 px-3 py-1 rounded-full text-xs">
                <UserIcon className="h-3.5 w-3.5 text-cyan-400" />
                <span className="font-medium text-slate-200">{user.username}</span>
                <span className="px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-mono text-[10px] uppercase">
                  {primaryRole}
                </span>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 hover:text-rose-400 text-slate-400 transition-all border border-slate-700"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-all shadow-md shadow-cyan-600/20"
            >
              Sign In
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
