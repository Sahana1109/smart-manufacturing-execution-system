import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SmartMES | Smart Manufacturing Execution System",
  description: "Enterprise-grade Smart Manufacturing Execution and Work Order Orchestration Platform",
  keywords: "MES, Manufacturing, Work Orders, Industrial IoT, Quality Inspection, Downtime Tracking, OEE",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-slate-950 font-sans text-slate-100 flex flex-col antialiased">
        <header id="main-header" className="border-b border-slate-800/80 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <span className="font-mono font-bold text-white text-lg">M</span>
              </div>
              <div>
                <span className="font-bold text-lg text-slate-100 tracking-tight">SMART<span className="text-cyan-400">MES</span></span>
                <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">v0.1.0</span>
              </div>
            </div>
            <nav id="header-nav" className="flex items-center space-x-6 text-sm font-medium">
              <a href="/" className="text-cyan-400 transition-colors">Overview</a>
              <a href="/health" className="text-slate-400 hover:text-slate-200 transition-colors">System Diagnostics</a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-slate-400 hover:text-slate-200 transition-colors">API Docs (Swagger)</a>
            </nav>
          </div>
        </header>

        <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer id="main-footer" className="border-t border-slate-800/60 bg-slate-950 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
            <p>© 2026 SmartMES Manufacturing Execution Platform. All rights reserved.</p>
            <div className="flex items-center space-x-4 mt-2 sm:mt-0">
              <span className="inline-flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                System Ready (Phase 0 & 1)
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
