import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import {
  MapPin, Plane, Edit3, Save, TrendingUp,
  AlertCircle, CheckCircle2, ChevronRight
} from 'lucide-react';
import { fetchRouteDetails, updateRouteWeight } from '../api';

export default function RouteBasketView({ routes, selectedRouteCode, onSelectRoute, onWeightsChanged }) {
  const [activeCode, setActiveCode] = useState(selectedRouteCode || 'DEL-BOM');
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weightInput, setWeightInput] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (selectedRouteCode) {
      setActiveCode(selectedRouteCode);
    }
  }, [selectedRouteCode]);

  useEffect(() => {
    async function loadDetails() {
      try {
        setLoading(true);
        const data = await fetchRouteDetails(activeCode);
        setDetails(data);
        setWeightInput(data.weight ? data.weight.toString() : '0.05');
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDetails();
  }, [activeCode]);

  const handleSaveWeight = async () => {
    try {
      const parsed = parseFloat(weightInput);
      if (isNaN(parsed) || parsed < 0 || parsed > 1.0) {
        alert('Weight must be between 0.0 and 1.0');
        return;
      }
      await updateRouteWeight(activeCode, parsed);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      if (onWeightsChanged) onWeightsChanged();
    } catch (err) {
      alert('Error updating weight');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Route Selector Grid */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              Representative Domestic Route Basket (20 City-Pairs)
            </h2>
            <p className="text-xs text-slate-500">
              High-density trunk and metro corridors representing &gt;85% of Indian domestic revenue passenger km
            </p>
          </div>
          <span className="text-xs font-mono font-medium px-2.5 py-1 bg-purple-50 text-purple-700 rounded-md border border-purple-200">
            DGCA Weight Calibrated
          </span>
        </div>

        {/* 20 Routes Button Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-10 gap-2">
          {(routes || []).map((r) => {
            const isSelected = r.route_code === activeCode;
            return (
              <button
                key={r.route_code}
                onClick={() => {
                  setActiveCode(r.route_code);
                  if (onSelectRoute) onSelectRoute(r.route_code);
                }}
                className={`px-3 py-2 rounded-xl text-xs font-mono font-bold transition-all border text-center ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-500/20 scale-105'
                    : 'bg-slate-50 text-slate-700 border-slate-200/80 hover:bg-slate-100 hover:border-slate-300'
                }`}
              >
                <div>{r.route_code}</div>
                <div className={`text-[10px] mt-0.5 font-sans ${isSelected ? 'text-blue-100' : 'text-slate-400'}`}>
                  {(r.weight * 100).toFixed(1)}%
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Route Deep Dive Section */}
      {details && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Route Profile & Weight Controls */}
          <div className="space-y-6">
            {/* Route Metadata Card */}
            <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <span className="text-xl font-extrabold text-slate-900 font-mono">
                    {details.route_code}
                  </span>
                </div>
                <span className="text-xs px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md font-semibold">
                  {details.region || 'Domestic Trunk'}
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Origin Airport</span>
                  <span className="font-bold text-slate-800">{details.origin}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Destination Airport</span>
                  <span className="font-bold text-slate-800">{details.destination}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Monthly Traffic Volume</span>
                  <span className="font-mono font-bold text-slate-800">
                    {details.traffic_volume ? details.traffic_volume.toLocaleString('en-IN') : '250,000'} pax
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Current Basket Weight</span>
                  <span className="font-mono font-bold text-blue-700">
                    {details.weight ? (details.weight * 100).toFixed(2) : '5.00'}%
                  </span>
                </div>
              </div>

              {/* Administrative Weight Adjustment */}
              <div className="mt-5 p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-800 mb-1.5">
                  <Edit3 className="w-3.5 h-3.5 text-amber-600" />
                  <span>Configure Statistical Weight</span>
                </div>
                <p className="text-[11px] text-slate-500 mb-3">
                  Calibrate this route's contribution to composite APIx based on latest DGCA traffic filings.
                </p>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    step="0.005"
                    min="0"
                    max="1"
                    value={weightInput}
                    onChange={(e) => setWeightInput(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-mono font-bold focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleSaveWeight}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 transition-colors shadow-sm"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Save</span>
                  </button>
                </div>
                {saveSuccess && (
                  <div className="mt-2 flex items-center space-x-1 text-[11px] text-emerald-600 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Weight saved & APIx normalized!</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Columns: Airline Price Spread & Route 30-Day Trend */}
          <div className="lg:col-span-2 space-y-6">
            {/* 30-Day Fare History on this Route */}
            <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    30-Day Airfare Trajectory ({activeCode})
                  </h3>
                  <p className="text-xs text-slate-500">
                    Daily average fare across all domestic operators
                  </p>
                </div>
              </div>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={details.history || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" tickFormatter={(v) => v.slice(5)} stroke="#94a3b8" fontSize={11} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                    <Tooltip formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Average Fare']} />
                    <Line
                      type="monotone"
                      dataKey="average_fare"
                      stroke="#2563eb"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Airline Breakdown on this Route */}
            <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-1">
                Carrier Price Spread on {activeCode}
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Comparative pricing across competing airlines on this city-pair
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">Airline</th>
                      <th className="py-2.5 px-3">Average Fare</th>
                      <th className="py-2.5 px-3">Lowest Fare</th>
                      <th className="py-2.5 px-3">Peak Fare</th>
                      <th className="py-2.5 px-3">Quotes Sampled</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {(details.airline_breakdown || []).map((ab) => (
                      <tr key={ab.airline} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-bold font-sans text-slate-800 flex items-center gap-1.5">
                          <Plane className="w-3.5 h-3.5 text-blue-600" />
                          {ab.airline}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-blue-700">
                          ₹{Math.round(ab.average_fare).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 text-emerald-600">
                          ₹{Math.round(ab.min_fare).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 text-rose-600">
                          ₹{Math.round(ab.max_fare).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 text-slate-500 font-sans">
                          {ab.observation_count}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
