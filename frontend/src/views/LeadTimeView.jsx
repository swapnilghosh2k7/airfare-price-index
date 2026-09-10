import React, { useState } from 'react';
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine
} from 'recharts';
import { Clock, TrendingUp, AlertTriangle, ArrowRight, Zap } from 'lucide-react';

export default function LeadTimeView({ leadTime }) {
  const [selectedRoute, setSelectedRoute] = useState('ALL');

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Advance-Purchase Window Elasticity Analysis
            </h2>
          </div>
          <span className="text-xs px-2.5 py-1 bg-amber-50 text-amber-800 rounded-md font-semibold border border-amber-200">
            Yield Management Curve
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Demonstrating non-linear dynamic airline pricing across five mandatory statistical booking horizons: <strong>T+1, T+7, T+15, T+30, T+45</strong>.
        </p>
      </div>

      {/* Main Elasticity Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dynamic Pricing Escalation Chart (2 cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Fare Escalation Curve (Advance Days vs Average Fare)
              </h3>
              <p className="text-xs text-slate-500">
                Observe the steep non-linear surge within the 7-day distress/business travel window
              </p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={leadTime} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <defs>
                  <linearGradient id="leadTimeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="window_label" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `₹${val.toLocaleString('en-IN')} (${item.payload.price_multiplier}x multiplier)`,
                    'Average Airfare'
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey="average_fare"
                  stroke="#4f46e5"
                  strokeWidth={3}
                  fill="url(#leadTimeGrad)"
                  name="Airfare"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dynamic Multiplier Step Cards (1 col) */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              Step-Price Multipliers
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Relative to T+45 early-purchase baseline
            </p>

            <div className="space-y-2.5 font-mono text-xs">
              {(leadTime || []).map((lt) => {
                const isUrgent = lt.advance_days <= 7;
                return (
                  <div
                    key={lt.window_label}
                    className={`p-2.5 rounded-xl border flex items-center justify-between ${
                      isUrgent
                        ? 'bg-rose-50/70 border-rose-200 text-rose-900'
                        : 'bg-slate-50 border-slate-200 text-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-bold font-sans">{lt.window_label}</span>
                      <span className="text-[10px] text-slate-500 font-sans">
                        ({lt.advance_days}d lead)
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">₹{Math.round(lt.average_fare).toLocaleString('en-IN')}</div>
                      <div className={`text-[10px] font-sans ${isUrgent ? 'text-rose-600 font-bold' : 'text-slate-500'}`}>
                        {lt.price_multiplier}x Base
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 p-3 bg-amber-50 border border-amber-200/80 rounded-xl text-xs text-amber-900 flex items-start space-x-2">
            <Zap className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">NSO Index Relevance: </span>
              Capturing all 5 windows prevents systemic downward bias from tracking only early-bird tickets or upward bias from last-minute quotes.
            </div>
          </div>
        </div>
      </div>

      {/* Step-by-Step Percentage Change Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1">
          Window Transition Delta Matrix
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Quantifying the consumer price penalty of delayed ticket purchase
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 text-slate-600 font-sans font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Advance Horizon</th>
                <th className="py-2.5 px-3">Days to Travel</th>
                <th className="py-2.5 px-3">Average Fare (₹)</th>
                <th className="py-2.5 px-3">Index Multiplier</th>
                <th className="py-2.5 px-3">% Premium vs Prior Window</th>
                <th className="py-2.5 px-3">Sampled Observations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(leadTime || []).map((lt) => (
                <tr key={lt.window_label} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-bold font-sans text-slate-900">{lt.window_label}</td>
                  <td className="py-2.5 px-3 text-slate-600">{lt.advance_days} Days</td>
                  <td className="py-2.5 px-3 font-bold text-indigo-700">₹{Math.round(lt.average_fare).toLocaleString('en-IN')}</td>
                  <td className="py-2.5 px-3 text-blue-600 font-bold">{lt.price_multiplier}x</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded font-sans text-[11px] font-semibold ${
                      lt.pct_change_from_prior > 0 ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {lt.pct_change_from_prior > 0 ? `+${lt.pct_change_from_prior}%` : 'Baseline'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-sans text-slate-500">{lt.observation_count.toLocaleString('en-IN')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
