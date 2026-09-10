import React, { useState } from 'react';
import {
  ResponsiveContainer, AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend, ReferenceLine
} from 'recharts';
import {
  TrendingUp, MapPin, IndianRupee, PieChart,
  Calendar, ArrowUpRight, ArrowDownRight, Layers
} from 'lucide-react';

export default function OverviewDashboard({
  dailyIndex,
  heatmap,
  leadTime,
  components,
  onSelectRoute
}) {
  const [timeRange, setTimeRange] = useState('30D');

  const filteredDaily = (dailyIndex?.points || []).slice(
    timeRange === '7D' ? -7 : timeRange === '15D' ? -15 : -30
  );

  return (
    <div className="space-y-6">
      {/* 1. Main Time Series Row: APIx Index & Average Fare */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* APIx Real-time Index Chart (2 cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-slate-900">
                  Real-time APIx Time Series
                </h3>
                <span className="text-xs px-2 py-0.5 rounded font-mono font-medium bg-blue-50 text-blue-700 border border-blue-200">
                  Base 100.0 Benchmark
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Weighted composite price relative across 20 domestic city-pairs
              </p>
            </div>

            {/* Time Filter Pills */}
            <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-semibold">
              {['7D', '15D', '30D'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    timeRange === range
                      ? 'bg-white text-blue-700 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredDaily}>
                <defs>
                  <linearGradient id="apixGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(val) => val.slice(5)}
                  stroke="#94a3b8"
                  fontSize={11}
                />
                <YAxis
                  domain={['auto', 'auto']}
                  stroke="#94a3b8"
                  fontSize={11}
                  tickFormatter={(v) => v.toFixed(1)}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-slate-900 text-white p-3 rounded-xl shadow-xl text-xs font-mono border border-slate-800">
                          <div className="font-semibold text-slate-300 mb-1">{label}</div>
                          <div className="text-blue-400 font-bold text-sm">
                            APIx: {payload[0].value.toFixed(2)}
                          </div>
                          <div className="text-slate-400">
                            Avg Fare: ₹{Math.round(payload[0].payload.average_fare).toLocaleString('en-IN')}
                          </div>
                          <div className="text-slate-400">
                            Observations: {payload[0].payload.observation_count}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <ReferenceLine y={100} stroke="#dc2626" strokeDasharray="3 3" label={{ value: 'Base 100', fill: '#dc2626', fontSize: 10 }} />
                <Area
                  type="monotone"
                  dataKey="apix_value"
                  stroke="#2563eb"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#apixGradient)"
                  name="APIx Index"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fare Component Breakdown (1 col) */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <PieChart className="w-4 h-4 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">
                Airfare Component Share
              </h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Disaggregated cost elements of Indian domestic tickets
            </p>

            {/* Component Progress Bars */}
            <div className="space-y-3.5">
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm bg-blue-600"></span>
                    Base Fare
                  </span>
                  <span className="font-mono font-bold">{components?.base_fare_pct || 68.2}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-600 h-full rounded-full" style={{ width: `${components?.base_fare_pct || 68.2}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm bg-amber-500"></span>
                    Aviation Fuel Surcharge
                  </span>
                  <span className="font-mono font-bold">{components?.fuel_surcharge_pct || 15.8}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: `${components?.fuel_surcharge_pct || 15.8}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span>
                    User Dev. Fee (UDF/ADF)
                  </span>
                  <span className="font-mono font-bold">{components?.udf_pct || 7.5}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-purple-500 h-full rounded-full" style={{ width: `${components?.udf_pct || 7.5}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                    Taxes (GST 5%) & Fees
                  </span>
                  <span className="font-mono font-bold">{components?.taxes_pct || 4.5}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${components?.taxes_pct || 4.5}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm bg-slate-400"></span>
                    OTA Convenience Fee
                  </span>
                  <span className="font-mono font-bold">{components?.convenience_fee_pct || 4.0}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-slate-400 h-full rounded-full" style={{ width: `${components?.convenience_fee_pct || 4.0}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-600">
            <div className="font-semibold text-slate-800 mb-0.5">Macroeconomic Insight:</div>
            Jet fuel pass-through and airport UDF adjustments account for <strong>23.3%</strong> of consumer airfare volatility.
          </div>
        </div>
      </div>

      {/* 2. Middle Row: Lead-Time Elasticity & Route Heatmap Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lead-Time Elasticity Curve */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Lead-Time Elasticity Curve
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Dynamic pricing escalation across advance purchase windows (T+45 to T+1)
              </p>
            </div>
            <span className="text-xs px-2 py-1 rounded bg-amber-50 text-amber-800 font-semibold border border-amber-200">
              Yield Management Curve
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={leadTime} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="window_label" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `₹${val.toLocaleString('en-IN')} (${item.payload.price_multiplier}x vs T+45)`,
                    'Average Fare'
                  ]}
                />
                <Bar
                  dataKey="average_fare"
                  fill="#4f46e5"
                  radius={[6, 6, 0, 0]}
                  name="Average Fare"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-5 gap-2 mt-4 text-center">
            {(leadTime || []).map((item) => (
              <div key={item.window_label} className="bg-slate-50 border border-slate-200/60 rounded-lg p-2">
                <div className="text-[11px] font-bold text-slate-700">{item.window_label}</div>
                <div className="text-xs font-mono font-bold text-indigo-700 mt-0.5">
                  ₹{Math.round(item.average_fare).toLocaleString('en-IN')}
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">{item.price_multiplier}x</div>
              </div>
            ))}
          </div>
        </div>

        {/* Route Basket Top Movers Heatmap Preview */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Top Domestic City-Pairs (By DGCA Weight)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Current weighted fare, APIx contribution, and volatility
              </p>
            </div>
            <span className="text-xs text-blue-600 font-semibold hover:underline cursor-pointer" onClick={() => onSelectRoute('DEL-BOM')}>
              View All 20 Routes →
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Route</th>
                  <th className="py-2.5 px-2">Weight</th>
                  <th className="py-2.5 px-3">Current Fare</th>
                  <th className="py-2.5 px-2">Relative</th>
                  <th className="py-2.5 px-2">APIx Contrib.</th>
                  <th className="py-2.5 px-2">Volatility</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(heatmap || []).slice(0, 6).map((r) => (
                  <tr
                    key={r.route_code}
                    onClick={() => onSelectRoute(r.route_code)}
                    className="hover:bg-blue-50/50 cursor-pointer transition-colors"
                  >
                    <td className="py-2 px-3 font-bold text-slate-900 flex items-center gap-1.5">
                      <MapPin className="w-3 h-3 text-blue-600" />
                      {r.route_code}
                    </td>
                    <td className="py-2 px-2 font-mono text-slate-600">{r.weight_pct}%</td>
                    <td className="py-2 px-3 font-mono font-bold text-slate-800">
                      ₹{Math.round(r.current_fare).toLocaleString('en-IN')}
                    </td>
                    <td className="py-2 px-2 font-mono text-blue-600">{r.price_relative}</td>
                    <td className="py-2 px-2 font-mono font-bold text-indigo-700">{r.apix_contribution}</td>
                    <td className="py-2 px-2 font-mono text-slate-500">{r.volatility_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
