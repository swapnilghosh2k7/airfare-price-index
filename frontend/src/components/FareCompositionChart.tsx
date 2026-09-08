import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { CarrierAnalytics } from '../types';
import { PieChart } from 'lucide-react';

interface FareCompositionChartProps {
  data: CarrierAnalytics[];
}

export const FareCompositionChart: React.FC<FareCompositionChartProps> = ({ data }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <PieChart className="w-4 h-4 text-cyan-400" />
            Fare Component Breakdown by Carrier
          </h3>
          <p className="text-xs text-slate-400">Base fare, taxes, fees, and surcharges composition</p>
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
                formatter={(val: number, name: string) => [`₹${val.toLocaleString('en-IN')}`, name]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="mean_base_fare" name="Base Fare" stackId="a" fill="#06b6d4" />
              <Bar dataKey="mean_taxes" name="Taxes (GST)" stackId="a" fill="#3b82f6" />
              <Bar dataKey="mean_fuel_surcharge" name="Fuel Surcharge" stackId="a" fill="#f59e0b" />
              <Bar dataKey="mean_airport_fee" name="Airport Fee" stackId="a" fill="#8b5cf6" />
              <Bar dataKey="mean_convenience_fee" name="Convenience Fee" stackId="a" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Loading fare composition data...
          </div>
        )}
      </div>
    </div>
  );
};
