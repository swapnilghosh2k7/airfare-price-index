import React, { useState } from 'react';
import { Plane, RefreshCw, Database, ShieldCheck, ExternalLink, Activity, Sparkles } from 'lucide-react';

export default function Header({
  kpis,
  demoMode,
  setDemoMode,
  onTriggerScrape,
  isScraping,
  lastUpdated
}) {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      {/* Top Ministry Bar */}
      <div className="bg-slate-950 px-6 py-1.5 border-b border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="font-semibold text-amber-400 tracking-wider">GOVERNMENT OF INDIA</span>
          <span>•</span>
          <span>Ministry of Statistics and Programme Implementation (MoSPI)</span>
          <span>•</span>
          <span className="text-slate-500">National Statistical Office (NSO) • RBI Monetary Policy Input</span>
        </div>
        <div className="flex items-center space-x-4">
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1 hover:text-amber-400 transition-colors"
          >
            <span>FastAPI Swagger Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
          <span className="flex items-center space-x-1 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Live System Online</span>
          </span>
        </div>
      </div>

      {/* Main Header Content */}
      <div className="px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Logo & Brand */}
        <div className="flex items-center space-x-3.5">
          <div className="bg-gradient-to-tr from-blue-700 to-indigo-600 p-2.5 rounded-xl shadow-inner border border-blue-400/30">
            <Plane className="w-6 h-6 text-white transform -rotate-45" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                APIx <span className="text-xs px-2 py-0.5 rounded font-mono font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">v1.0-PROD</span>
              </h1>
              <span className="text-slate-400 text-sm hidden sm:inline">|</span>
              <span className="text-slate-200 text-sm font-semibold tracking-tight hidden sm:inline">
                Real-time Airfare Price Index for India
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Automated High-Frequency Web Scraping & Econometric Index for Consumer Price Index (CPI) Augmentation
            </p>
          </div>
        </div>

        {/* Action Controls & Metrics */}
        <div className="flex items-center flex-wrap gap-3">
          {/* Current APIx Pill */}
          <div className="bg-slate-800/90 border border-slate-700/80 px-3.5 py-1.5 rounded-lg flex items-center space-x-2 shadow-sm">
            <Activity className="w-4 h-4 text-amber-400" />
            <span className="text-xs text-slate-400 font-medium">Current APIx:</span>
            <span className="font-mono text-base font-bold text-white">
              {kpis?.apix_value ? kpis.apix_value.toFixed(2) : '100.00'}
            </span>
            <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
              (kpis?.daily_change_pct || 0) >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
            }`}>
              {(kpis?.daily_change_pct || 0) >= 0 ? '+' : ''}{kpis?.daily_change_pct || 0}%
            </span>
          </div>

          {/* Mode Switch: Demo Mode vs Live Data Mode */}
          <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setDemoMode(true)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all flex items-center space-x-1.5 ${
                demoMode
                  ? 'bg-amber-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>DEMO MODE</span>
            </button>
            <button
              onClick={() => setDemoMode(false)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all flex items-center space-x-1.5 ${
                !demoMode
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>LIVE DATA MODE</span>
            </button>
          </div>

          {/* Manual Scraper Trigger Button */}
          <button
            onClick={() => onTriggerScrape(true)}
            disabled={isScraping}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg flex items-center space-x-2 transition-all shadow ${
              isScraping
                ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white active:scale-95'
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScraping ? 'animate-spin text-amber-400' : ''}`} />
            <span>{isScraping ? 'Collecting Data...' : 'Run Collection Now'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
