import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine
} from 'recharts';
import { IndexObservationItem, RouteItem } from '../types';
import { Calendar, Filter } from 'lucide-react';

interface IndexChartProps {
  data: IndexObservationItem[];
  routes: RouteItem[];
  selectedRoute: string;
  onSelectRoute: (route: string) => void;
}

export const IndexChart: React.FC<IndexChartProps> = ({
  data,
  routes,
  selectedRoute,
  onSelectRoute
}) => {
  const [timeframe, setTimeframe] = useState<'7D' | '30D' | 'ALL'>('30D');

  const filteredData = React.useMemo(() => {
    if (!data || data.length === 0) return [];
    let subset = [...data];

    if (timeframe === '7D') {
      subset = subset.slice(-7);
    } else if (timeframe === '30D') {
      subset = subset.slice(-30);
    }

    return subset.map(item => ({
      date: item.observation_date,
      value: item.route_code === 'NATIONAL' ? item.national_index : item.route_index,
      sampleCount: item.sample_count
    }));
  }, [data, timeframe]);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold text-white font-heading flex items-center gap-2">
            India Airfare Price Index (APIx)
          </h2>
          <p className="text-xs text-slate-400">
            {selectedRoute === 'NATIONAL'
              ? 'National Weighted Aggregate Airfare Price Index (Base = 100)'
              : `Route Specific Index: ${selectedRoute} (Base = 100)`}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Route Filter Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
            <Filter className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={selectedRoute}
              onChange={e => onSelectRoute(e.target.value)}
              className="bg-transparent text-white focus:outline-none cursor-pointer font-medium"
            >
              <option value="NATIONAL" className="bg-slate-900 text-white">
                National Aggregate (APIx)
              </option>
              {routes.map(r => (
                <option key={r.route_code} value={r.route_code} className="bg-slate-900 text-white">
                  {r.route_code} ({r.origin_city} - {r.destination_city})
                </option>
              ))}
            </select>
          </div>

          {/* Timeframe Filter Buttons */}
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1 text-xs">
            {(['7D', '30D', 'ALL'] as const).map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                  timeframe === tf ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 w-full">
        {filteredData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                tickFormatter={val => val.slice(5)}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '12px',
                  fontSize: '12px',
                  color: '#f8fafc'
                }}
                formatter={(val: number) => [`Index: ${val.toFixed(2)}`, 'APIx Index']}
                labelFormatter={label => `Observation Date: ${label}`}
              />
              <ReferenceLine y={100} stroke="#475569" strokeDasharray="4 4" label={{ value: 'Baseline (100)', fill: '#64748b', fontSize: 10 }} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#06b6d4"
                strokeWidth={3}
                dot={{ fill: '#06b6d4', r: 3 }}
                activeDot={{ r: 6, fill: '#38bdf8', stroke: '#0284c7', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            No index observations available for selected route.
          </div>
        )}
      </div>
    </div>
  );
};
