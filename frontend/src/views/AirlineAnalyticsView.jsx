import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, Legend
} from 'recharts';
import { Plane, Layers, Award, Tag, Info } from 'lucide-react';
import { fetchAirlineComparison } from '../api';

export default function AirlineAnalyticsView() {
  const [airlineData, setAirlineData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchAirlineComparison();
        setAirlineData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Domestic Airline Price & Cost Structure Analysis
            </h2>
          </div>
          <span className="text-xs px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-md font-semibold border border-indigo-200">
            Carrier Disaggregation
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Comparing pricing power, fare component structures, and passenger tariff strategies across Low-Cost Carriers (LCC) and Full-Service Carriers (FSC).
        </p>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Average Total Fare by Carrier */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-1">
            Average Total Airfare by Airline
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Weighted domestic average ticket prices across all route pairs
          </p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={airlineData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="airline" stroke="#94a3b8" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                <Tooltip formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Average Fare']} />
                <Bar dataKey="average_total_fare" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Total Fare" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Stacked Fare Components by Airline */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-1">
            Fare Component Disaggregation by Carrier
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Base Fare vs Fuel Surcharge vs UDF vs Taxes
          </p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={airlineData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="airline" stroke="#94a3b8" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                <Tooltip formatter={(v) => `₹${Math.round(v).toLocaleString('en-IN')}`} />
                <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
                <Bar dataKey="average_base_fare" stackId="a" fill="#2563eb" name="Base Fare" />
                <Bar dataKey="average_fuel_surcharge" stackId="a" fill="#f59e0b" name="Fuel Surcharge" />
                <Bar dataKey="average_udf" stackId="a" fill="#8b5cf6" name="UDF / Airport Fee" />
                <Bar dataKey="average_taxes" stackId="a" fill="#10b981" name="Taxes (GST)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Carrier Economics Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1">
          Carrier Pricing Matrix & Observations Audited
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Empirical pricing data collected across the representative domestic network
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Carrier</th>
                <th className="py-2.5 px-3">Business Model</th>
                <th className="py-2.5 px-3">Base Fare</th>
                <th className="py-2.5 px-3">Fuel Surcharge</th>
                <th className="py-2.5 px-3">Taxes & UDF</th>
                <th className="py-2.5 px-3">Total Ticket</th>
                <th className="py-2.5 px-3">Observations Sampled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {airlineData.map((item) => {
                const isFSC = item.airline === 'Air India';
                return (
                  <tr key={item.airline} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-sans font-bold text-slate-900 flex items-center gap-2">
                      <Plane className="w-4 h-4 text-blue-600" />
                      {item.airline}
                    </td>
                    <td className="py-3 px-3 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        isFSC ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {isFSC ? 'Full-Service (FSC)' : 'Low-Cost (LCC)'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-700">₹{Math.round(item.average_base_fare).toLocaleString('en-IN')}</td>
                    <td className="py-3 px-3 text-amber-600">₹{Math.round(item.average_fuel_surcharge).toLocaleString('en-IN')}</td>
                    <td className="py-3 px-3 text-purple-600">₹{Math.round(item.average_taxes + item.average_udf).toLocaleString('en-IN')}</td>
                    <td className="py-3 px-3 font-bold text-blue-700 text-sm">
                      ₹{Math.round(item.average_total_fare).toLocaleString('en-IN')}
                    </td>
                    <td className="py-3 px-3 font-sans text-slate-500">
                      {item.observation_count.toLocaleString('en-IN')}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
