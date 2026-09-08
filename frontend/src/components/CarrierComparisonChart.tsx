import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import { CarrierAnalytics } from '../types';
import { Building2 } from 'lucide-react';

interface CarrierComparisonChartProps {
  data: CarrierAnalytics[];
}

const CARRIER_COLORS: Record<string, string> = {
  'IndiGo': '#06b6d4',
  'Air India': '#f43f5e',
  'Vistara': '#a855f7',
  'Akasa Air': '#f59e0b',
  'SpiceJet': '#10b981'
};

export const CarrierComparisonChart: React.FC<CarrierComparisonChartProps> = ({ data }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Building2 className="w-4 h-4 text-cyan-400" />
            Carrier Median Fare Comparison
          </h3>
          <p className="text-xs text-slate-400">Median total fare by airline across all active routes</p>
        </div>
      </div>

      <div className="h-64 w-full">
        {data && data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="carrier" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={val => `₹${val/1000}k`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '12px',
                  fontSize: '12px',
                  color: '#f8fafc'
                }}
                formatter={(val: number) => [`₹${val.toLocaleString('en-IN')}`, 'Median Fare']}
              />
              <Bar dataKey="median_total_fare" radius={[8, 8, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CARRIER_COLORS[entry.carrier] || '#06b6d4'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Loading carrier comparison data...
          </div>
        )}
      </div>
    </div>
  );
};
