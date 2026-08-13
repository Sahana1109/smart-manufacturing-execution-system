import type { Metadata } from "next";
import "./globals.css";
import AppHeaderNav from "@/components/layout/AppHeaderNav";
import { AuthProvider } from "@/lib/auth-context";

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
        <AuthProvider>
          <AppHeaderNav />
          <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          <footer id="main-footer" className="border-t border-slate-800/60 bg-slate-950 py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
              <p>© 2026 SmartMES Manufacturing Execution Platform. All rights reserved.</p>
              <div className="flex items-center space-x-4 mt-2 sm:mt-0">
                <span className="inline-flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Sprint 1 (Auth & RBAC Active)
                </span>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
