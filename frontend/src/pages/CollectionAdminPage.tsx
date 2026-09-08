import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import { CollectionRunItem } from '../types';
import { Play, RefreshCw, Server, ShieldCheck, Database, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

export const CollectionAdminPage: React.FC = () => {
  const [runs, setRuns] = useState<CollectionRunItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const fetchRuns = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getCollectionRuns();
      setRuns(data);
    } catch (err) {
      console.error("Failed to fetch collection runs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleRunDemo = async () => {
    setActionMsg("Triggering 30-day synthetic demo data generator...");
    try {
      const res = await ApiService.triggerRunDemo();
      setActionMsg(`Success: ${res.message}`);
      setTimeout(fetchRuns, 2000);
    } catch (err) {
      setActionMsg(`Error triggering collection: ${err}`);
    }
  };

  const handleRebuildIndex = async () => {
    setActionMsg("Triggering Laspeyres Price Index (APIX_v1) rebuild...");
    try {
      const res = await ApiService.triggerRebuildIndex();
      setActionMsg(`Success: ${res.message}`);
      setTimeout(fetchRuns, 2000);
    } catch (err) {
      setActionMsg(`Error rebuilding index: ${err}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-heading">Data Collection & Pipeline Admin</h2>
          <p className="text-xs text-slate-400">Monitor collector runs, provider status, and trigger synthetic pipeline executions</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRebuildIndex}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs rounded-xl border border-slate-700 transition-all"
          >
            <RefreshCw className="w-4 h-4 text-cyan-400" />
            <span>Rebuild Index</span>
          </button>
          <button
            onClick={handleRunDemo}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-lg shadow-cyan-500/20"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Run Demo Collection</span>
          </button>
        </div>
      </div>

      {/* Action Notification */}
      {actionMsg && (
        <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded-xl text-xs flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400 animate-spin" />
          <span>{actionMsg}</span>
        </div>
      )}

      {/* Provider Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">MockFareProvider</span>
            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-[10px] font-bold">Active</span>
          </div>
          <p className="text-xs text-slate-400">Synthetic airfare generator based on economic price curves and advance purchase windows</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">DatasetFareProvider</span>
            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-[10px] font-bold">Active</span>
          </div>
          <p className="text-xs text-slate-400">Loads pre-collected or officially supplied historical CSV airfare datasets</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Permitted Scrapers</span>
            <span className="px-2 py-0.5 bg-slate-800 text-slate-400 border border-slate-700 rounded-full text-[10px] font-bold">Standby</span>
          </div>
          <p className="text-xs text-slate-400">Robots.txt compliant live adapters (rate limited 5.0s, no CAPTCHA bypass)</p>
        </div>
      </div>

      {/* Collection Runs Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white font-heading flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            Historical Collection Execution Log
          </h3>
          <button onClick={fetchRuns} className="p-1 text-slate-400 hover:text-white">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400">
                <th className="py-3 px-4 font-semibold">Run ID</th>
                <th className="py-3 px-4 font-semibold">Started At</th>
                <th className="py-3 px-4 font-semibold">Source Adapter</th>
                <th className="py-3 px-4 font-semibold text-center">Routes Requested</th>
                <th className="py-3 px-4 font-semibold text-center">Collected</th>
                <th className="py-3 px-4 font-semibold text-center">Valid</th>
                <th className="py-3 px-4 font-semibold text-center">Rejected</th>
                <th className="py-3 px-4 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">Loading collection logs...</td>
                </tr>
              ) : runs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">No collection runs recorded yet.</td>
                </tr>
              ) : (
                runs.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3 px-4 text-slate-400">#{r.id}</td>
                    <td className="py-3 px-4 text-slate-300">{r.started_at.slice(0, 19).replace('T', ' ')}</td>
                    <td className="py-3 px-4 text-cyan-400 font-sans">{r.source}</td>
                    <td className="py-3 px-4 text-center">{r.routes_requested}</td>
                    <td className="py-3 px-4 text-center font-bold text-white">{r.quotes_collected.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center text-emerald-400">{r.quotes_valid.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center text-rose-400">{r.quotes_rejected.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center font-sans">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle className="w-3 h-3" /> {r.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
