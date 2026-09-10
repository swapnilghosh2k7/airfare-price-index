import React from 'react';
import {
  TrendingUp, TrendingDown, IndianRupee, MapPin,
  Layers, Database, Calendar, BarChart3
} from 'lucide-react';

export default function KPIRibbon({ kpis }) {
  const isDailyUp = (kpis?.daily_change_pct || 0) >= 0;
  const isWeeklyUp = (kpis?.weekly_change_pct || 0) >= 0;
  const isMonthlyUp = (kpis?.monthly_change_pct || 0) >= 0;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {/* 1. Current APIx */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>Current APIx</span>
          <BarChart3 className="w-3.5 h-3.5 text-blue-600" />
        </div>
        <div className="mt-1 font-mono text-xl font-bold text-slate-900">
          {kpis?.apix_value ? kpis.apix_value.toFixed(2) : '100.00'}
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">Base = 100.0</div>
      </div>

      {/* 2. Daily Change */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>24h Change</span>
          {isDailyUp ? (
            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
          ) : (
            <TrendingDown className="w-3.5 h-3.5 text-rose-600" />
          )}
        </div>
        <div className={`mt-1 font-mono text-xl font-bold ${isDailyUp ? 'text-emerald-600' : 'text-rose-600'}`}>
          {isDailyUp ? '+' : ''}{kpis?.daily_change_pct || 0}%
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">vs Previous Day</div>
      </div>

      {/* 3. Weekly Change */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>7-Day Change</span>
          {isWeeklyUp ? (
            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
          ) : (
            <TrendingDown className="w-3.5 h-3.5 text-rose-600" />
          )}
        </div>
        <div className={`mt-1 font-mono text-xl font-bold ${isWeeklyUp ? 'text-emerald-600' : 'text-rose-600'}`}>
          {isWeeklyUp ? '+' : ''}{kpis?.weekly_change_pct || 0}%
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">Weekly Rolling</div>
      </div>

      {/* 4. Monthly Change */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>30-Day Change</span>
          {isMonthlyUp ? (
            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
          ) : (
            <TrendingDown className="w-3.5 h-3.5 text-rose-600" />
          )}
        </div>
        <div className={`mt-1 font-mono text-xl font-bold ${isMonthlyUp ? 'text-emerald-600' : 'text-rose-600'}`}>
          {isMonthlyUp ? '+' : ''}{kpis?.monthly_change_pct || 0}%
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">Monthly Yield</div>
      </div>

      {/* 5. Average Domestic Fare */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>Average Fare</span>
          <IndianRupee className="w-3.5 h-3.5 text-indigo-600" />
        </div>
        <div className="mt-1 font-mono text-xl font-bold text-slate-900">
          ₹{kpis?.average_domestic_fare ? Math.round(kpis.average_domestic_fare).toLocaleString('en-IN') : '5,850'}
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">Weighted Economy</div>
      </div>

      {/* 6. Basket Routes Tracked */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>Routes Tracked</span>
          <MapPin className="w-3.5 h-3.5 text-purple-600" />
        </div>
        <div className="mt-1 font-mono text-xl font-bold text-slate-900">
          {kpis?.active_routes_count || 20}
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">DGCA Top Pairs</div>
      </div>

      {/* 7. Airlines Tracked */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>Airlines</span>
          <Layers className="w-3.5 h-3.5 text-cyan-600" />
        </div>
        <div className="mt-1 font-mono text-xl font-bold text-slate-900">
          {kpis?.active_airlines_count || 5}
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">6E, AI, IX, QP, SG</div>
      </div>

      {/* 8. Total Observations */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
          <span>Clean Observations</span>
          <Database className="w-3.5 h-3.5 text-emerald-600" />
        </div>
        <div className="mt-1 font-mono text-xl font-bold text-slate-900">
          {kpis?.total_observations ? kpis.total_observations.toLocaleString('en-IN') : '14,788'}
        </div>
        <div className="text-[11px] text-emerald-600 font-medium mt-0.5">95.4% Clean Rate</div>
      </div>
    </div>
  );
}
