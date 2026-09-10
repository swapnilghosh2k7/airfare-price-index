import React, { useState, useEffect } from 'react';
import {
  Download, Search, Filter, Database, RefreshCw,
  FileSpreadsheet, ArrowUpDown, ChevronLeft, ChevronRight
} from 'lucide-react';
import { fetchFares } from '../api';

export default function DataExplorerView({ routes }) {
  const [fares, setFares] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [routeFilter, setRouteFilter] = useState('');
  const [airlineFilter, setAirlineFilter] = useState('');
  const [windowFilter, setWindowFilter] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const loadFares = async () => {
    try {
      setLoading(true);
      const params = {
        limit: pageSize,
        offset: page * pageSize
      };
      if (routeFilter) params.route = routeFilter;
      if (airlineFilter) params.airline = airlineFilter;
      if (windowFilter) params.advance_purchase_days = parseInt(windowFilter);

      const res = await fetchFares(params);
      setFares(res.fares || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFares();
  }, [page, routeFilter, airlineFilter, windowFilter]);

  const handleExportFares = () => {
    let url = 'http://127.0.0.1:8000/api/fares/export';
    const params = [];
    if (routeFilter) params.push(`route=${routeFilter}`);
    if (airlineFilter) params.push(`airline=${airlineFilter}`);
    if (params.length) url += `?${params.join('&')}`;
    window.open(url, '_blank');
  };

  const handleExportBacktest = () => {
    window.open('http://127.0.0.1:8000/api/backtest/export', '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Banner & Global Export Controls */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-900">
                Airfare Observations Data Explorer & Export Hub
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Browse, filter, and export clean, normalized flight quotes formatted for NSO / RBI microdata analytics.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleExportBacktest}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors border border-slate-300"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-slate-600" />
              <span>Export Backtest CSV</span>
            </button>

            <button
              onClick={handleExportFares}
              className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Clean Fares CSV</span>
            </button>
          </div>
        </div>

        {/* Filter Controls Bar */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center gap-3">
          {/* Route Filter */}
          <div className="flex items-center space-x-1 text-xs">
            <span className="text-slate-500 font-medium">Route:</span>
            <select
              value={routeFilter}
              onChange={(e) => { setRouteFilter(e.target.value); setPage(0); }}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All 20 Routes</option>
              {(routes || []).map((r) => (
                <option key={r.route_code} value={r.route_code}>{r.route_code}</option>
              ))}
            </select>
          </div>

          {/* Airline Filter */}
          <div className="flex items-center space-x-1 text-xs">
            <span className="text-slate-500 font-medium">Airline:</span>
            <select
              value={airlineFilter}
              onChange={(e) => { setAirlineFilter(e.target.value); setPage(0); }}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Airlines</option>
              <option value="IndiGo">IndiGo (6E)</option>
              <option value="Air India">Air India (AI)</option>
              <option value="Air India Express">Air India Express (IX)</option>
              <option value="Akasa Air">Akasa Air (QP)</option>
              <option value="SpiceJet">SpiceJet (SG)</option>
            </select>
          </div>

          {/* Window Filter */}
          <div className="flex items-center space-x-1 text-xs">
            <span className="text-slate-500 font-medium">Window:</span>
            <select
              value={windowFilter}
              onChange={(e) => { setWindowFilter(e.target.value); setPage(0); }}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Windows</option>
              <option value="1">T+1 (1 Day)</option>
              <option value="7">T+7 (7 Days)</option>
              <option value="15">T+15 (15 Days)</option>
              <option value="30">T+30 (30 Days)</option>
              <option value="45">T+45 (45 Days)</option>
            </select>
          </div>

          {(routeFilter || airlineFilter || windowFilter) && (
            <button
              onClick={() => {
                setRouteFilter('');
                setAirlineFilter('');
                setWindowFilter('');
                setPage(0);
              }}
              className="text-xs text-rose-600 hover:underline font-semibold ml-2"
            >
              Reset Filters
            </button>
          )}

          <div className="ml-auto text-xs text-slate-500 font-mono">
            Showing {fares.length} of {total.toLocaleString('en-IN')} quotes
          </div>
        </div>
      </div>

      {/* Observations Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 text-slate-600 font-sans font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Search Date</th>
                <th className="py-3 px-3">Travel Date</th>
                <th className="py-3 px-3">Route</th>
                <th className="py-3 px-3">Airline</th>
                <th className="py-3 px-3">Flight No</th>
                <th className="py-3 px-2">Horizon</th>
                <th className="py-3 px-3">Base (₹)</th>
                <th className="py-3 px-2">Fuel (₹)</th>
                <th className="py-3 px-2">UDF (₹)</th>
                <th className="py-3 px-2">Taxes</th>
                <th className="py-3 px-3">Total (₹)</th>
                <th className="py-3 px-2">Z-Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {fares.map((f) => (
                <tr key={f.observation_id} className="hover:bg-slate-50/80">
                  <td className="py-2.5 px-3 text-slate-500">{f.search_date}</td>
                  <td className="py-2.5 px-3 text-slate-500">{f.travel_date}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-900">{f.route}</td>
                  <td className="py-2.5 px-3 font-sans text-slate-800">{f.airline}</td>
                  <td className="py-2.5 px-3 text-blue-600">{f.flight_number}</td>
                  <td className="py-2.5 px-2 font-bold text-indigo-700">T+{f.advance_purchase_days}</td>
                  <td className="py-2.5 px-3 text-slate-700">₹{Math.round(f.base_fare).toLocaleString('en-IN')}</td>
                  <td className="py-2.5 px-2 text-amber-600">₹{Math.round(f.fuel_surcharge)}</td>
                  <td className="py-2.5 px-2 text-purple-600">₹{Math.round(f.user_development_fee)}</td>
                  <td className="py-2.5 px-2 text-emerald-600">₹{Math.round(f.taxes)}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-900 text-sm">
                    ₹{Math.round(f.total_fare).toLocaleString('en-IN')}
                  </td>
                  <td className="py-2.5 px-2 text-slate-400">{f.z_score ? f.z_score.toFixed(2) : '0.00'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs">
          <span className="text-slate-500">
            Page {page + 1} of {Math.ceil(total / pageSize) || 1}
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 flex items-center space-x-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="px-3 py-1.5 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 flex items-center space-x-1"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
