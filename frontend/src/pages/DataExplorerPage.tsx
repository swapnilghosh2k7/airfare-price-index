import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import { FareQuoteItem, RouteItem, CarrierItem } from '../types';
import { Search, Download, Filter, ChevronLeft, ChevronRight, CheckCircle, AlertTriangle } from 'lucide-react';

interface DataExplorerPageProps {
  routes: RouteItem[];
  carriers: CarrierItem[];
}

export const DataExplorerPage: React.FC<DataExplorerPageProps> = ({ routes, carriers }) => {
  const [fares, setFares] = useState<FareQuoteItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(false);

  // Filters
  const [selectedRoute, setSelectedRoute] = useState('');
  const [selectedCarrier, setSelectedCarrier] = useState('');
  const [selectedLeadTime, setSelectedLeadTime] = useState('');

  const fetchFares = async () => {
    setLoading(true);
    try {
      const filters: Record<string, string> = {};
      if (selectedRoute) filters.route = selectedRoute;
      if (selectedCarrier) filters.carrier = selectedCarrier;
      if (selectedLeadTime) filters.lead_time = selectedLeadTime;

      const res = await ApiService.getFares(page, 20, filters);
      setFares(res.data);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      console.error("Failed to fetch fares", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFares();
  }, [page, selectedRoute, selectedCarrier, selectedLeadTime]);

  const handleExportCsv = () => {
    if (fares.length === 0) return;
    const headers = ["ID", "ObservedAt", "Route", "Carrier", "Flight", "Departure", "LeadTime", "BaseFare", "Taxes", "TotalFare", "Source", "Status"];
    const rows = fares.map(f => [
      f.id,
      f.observation_timestamp,
      `${f.origin}-${f.destination}`,
      f.carrier,
      f.flight_number,
      f.departure_date,
      `T+${f.lead_time_days}`,
      f.base_fare,
      f.taxes,
      f.total_fare,
      f.source,
      f.collection_status
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `airfarex_quotes_page_${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-heading">Fare Observation Data Explorer</h2>
          <p className="text-xs text-slate-400">Search, filter, inspect, and export normalized raw & cleaned fare observations</p>
        </div>
        <button
          onClick={handleExportCsv}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-lg shadow-cyan-500/20"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 flex-1 min-w-[200px]">
          <Filter className="w-3.5 h-3.5 text-cyan-400" />
          <select
            value={selectedRoute}
            onChange={e => { setSelectedRoute(e.target.value); setPage(1); }}
            className="bg-transparent text-white focus:outline-none w-full cursor-pointer"
          >
            <option value="" className="bg-slate-900">All Core Routes</option>
            {routes.map(r => (
              <option key={r.route_code} value={r.route_code} className="bg-slate-900">{r.route_code}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 flex-1 min-w-[180px]">
          <select
            value={selectedCarrier}
            onChange={e => { setSelectedCarrier(e.target.value); setPage(1); }}
            className="bg-transparent text-white focus:outline-none w-full cursor-pointer"
          >
            <option value="" className="bg-slate-900">All Carriers / Airlines</option>
            {carriers.map(c => (
              <option key={c.iata_code} value={c.name} className="bg-slate-900">{c.name}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 flex-1 min-w-[160px]">
          <select
            value={selectedLeadTime}
            onChange={e => { setSelectedLeadTime(e.target.value); setPage(1); }}
            className="bg-transparent text-white focus:outline-none w-full cursor-pointer"
          >
            <option value="" className="bg-slate-900">All Lead Times (T+1 to T+45)</option>
            <option value="1" className="bg-slate-900">T+1 (1 Day Prior)</option>
            <option value="7" className="bg-slate-900">T+7 (1 Week Prior)</option>
            <option value="15" className="bg-slate-900">T+15 (2 Weeks Prior)</option>
            <option value="30" className="bg-slate-900">T+30 (1 Month Prior)</option>
            <option value="45" className="bg-slate-900">T+45 (1.5 Months Prior)</option>
          </select>
        </div>
      </div>

      {/* Table Panel */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400">
                <th className="py-3 px-4 font-semibold">Observation</th>
                <th className="py-3 px-4 font-semibold">Route</th>
                <th className="py-3 px-4 font-semibold">Carrier</th>
                <th className="py-3 px-4 font-semibold">Flight</th>
                <th className="py-3 px-4 font-semibold">Departure</th>
                <th className="py-3 px-4 font-semibold">Lead Time</th>
                <th className="py-3 px-4 font-semibold">Base Fare</th>
                <th className="py-3 px-4 font-semibold">Taxes & Fees</th>
                <th className="py-3 px-4 font-semibold">Total Fare</th>
                <th className="py-3 px-4 font-semibold">Source</th>
                <th className="py-3 px-4 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={11} className="py-8 text-center text-slate-500">Loading observations...</td>
                </tr>
              ) : fares.length === 0 ? (
                <tr>
                  <td colSpan={11} className="py-8 text-center text-slate-500">No fare quotes match the specified filters.</td>
                </tr>
              ) : (
                fares.map(f => (
                  <tr key={f.id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3 px-4 text-slate-400">{f.observation_timestamp.slice(0, 10)}</td>
                    <td className="py-3 px-4 text-cyan-400 font-bold font-sans">{f.origin}-{f.destination}</td>
                    <td className="py-3 px-4 text-white font-sans">{f.carrier}</td>
                    <td className="py-3 px-4 text-slate-300">{f.flight_number}</td>
                    <td className="py-3 px-4 text-slate-400">{f.departure_date}</td>
                    <td className="py-3 px-4 font-sans">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-medium">T+{f.lead_time_days}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">₹{f.base_fare.toLocaleString('en-IN')}</td>
                    <td className="py-3 px-4 text-slate-400">₹{(f.taxes + f.airport_fee + f.fuel_surcharge).toLocaleString('en-IN')}</td>
                    <td className="py-3 px-4 text-emerald-400 font-bold">₹{f.total_fare.toLocaleString('en-IN')}</td>
                    <td className="py-3 px-4 text-slate-400 font-sans text-[11px]">{f.source}</td>
                    <td className="py-3 px-4 text-center font-sans">
                      {f.collection_status === 'VALID' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle className="w-3 h-3" /> Valid
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <AlertTriangle className="w-3 h-3" /> Flagged
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-6 py-4 bg-slate-900/60 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <strong className="text-white font-mono">{fares.length}</strong> of <strong className="text-white font-mono">{total}</strong> total observations (Page {page} of {pages})
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-white font-mono">{page}</span>
            <button
              disabled={page >= pages}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
