import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { LeadTimeAnalytics } from '../types';
import { Clock } from 'lucide-react';

interface LeadTimeCurveProps {
  data: LeadTimeAnalytics[];
}

export const LeadTimeCurve: React.FC<LeadTimeCurveProps> = ({ data }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Lead-Time Price Elasticity Curve
          </h3>
          <p className="text-xs text-slate-400">Median fare dynamics as departure date approaches ($T+45$ to $T+1$)</p>
        </div>
      </div>

      <div className="h-64 w-full">
        {data && data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="leadTimeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="lead_time_label" stroke="#64748b" tick={{ fontSize: 11 }} />
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
              <Area type="monotone" dataKey="median_fare" stroke="#06b6d4" strokeWidth={3} fillOpacity={1} fill="url(#leadTimeGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Loading lead-time elasticity data...
          </div>
        )}
      </div>
    </div>
  );
};
