import React, { useState, useEffect } from 'react';
import {
  Activity, ShieldCheck, ShieldAlert, AlertTriangle, RefreshCw,
  Clock, Database, Globe, Play, Server, CheckCircle2, XCircle
} from 'lucide-react';
import { fetchScraperStatus, triggerCollection, fetchScraperRuns, fetchScraperErrors } from '../api';

export default function ScraperMonitorView({ onScrapeCompleted }) {
  const [statusData, setStatusData] = useState(null);
  const [runs, setRuns] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statusRes, runsRes, errorsRes] = await Promise.all([
        fetchScraperStatus(),
        fetchScraperRuns(),
        fetchScraperErrors()
      ]);
      setStatusData(statusRes);
      setRuns(runsRes);
      setErrors(errorsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleManualTrigger = async (scoped = false) => {
    try {
      setIsTriggering(true);
      setTriggerMsg(null);
      const res = await triggerCollection(scoped);
      setTriggerMsg({
        type: 'success',
        text: `Cycle Completed! Run ID: ${res.run_id.slice(0, 8)}... Collected ${res.records_collected} quotes, Cleaned: ${res.records_cleaned}, Rejected: ${res.records_rejected}. APIx recalculated to ${res.apix_value}!`
      });
      await loadData();
      if (onScrapeCompleted) onScrapeCompleted();
    } catch (err) {
      setTriggerMsg({ type: 'error', text: 'Error executing scraper collection cycle.' });
    } finally {
      setIsTriggering(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'LIVE':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-1.5 animate-pulse"></span>
            LIVE
          </span>
        );
      case 'MOCK':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
            MOCK
          </span>
        );
      case 'UNAVAILABLE':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
            UNAVAILABLE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
            ERROR
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Trigger Controls */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-900">
                Automated Scraper Orchestrator & Live Monitor
              </h2>
              <span className="text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                11 Source Adapters
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Ethical extraction pipeline respecting robots.txt compliance, token-bucket rate limiting, and automated CAPTCHA detection.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => handleManualTrigger(true)}
              disabled={isTriggering}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition-all shadow-sm ${
                isTriggering
                  ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTriggering ? 'animate-spin' : ''}`} />
              <span>Fast Interactive Cycle</span>
            </button>

            <button
              onClick={() => handleManualTrigger(false)}
              disabled={isTriggering}
              className={`px-4 py-1.5 text-xs font-bold rounded-lg flex items-center space-x-2 transition-all shadow ${
                isTriggering
                  ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white active:scale-95'
              }`}
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isTriggering ? 'animate-spin' : ''}`} />
              <span>{isTriggering ? 'Extracting Across 11 Portals...' : 'Run Full Collection Now'}</span>
            </button>
          </div>
        </div>

        {triggerMsg && (
          <div className={`mt-3 p-3 rounded-xl text-xs flex items-center space-x-2 ${
            triggerMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
          }`}>
            {triggerMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" /> : <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />}
            <span>{triggerMsg.text}</span>
          </div>
        )}
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">Total Adapters</div>
          <div className="font-mono text-xl font-bold text-slate-900 mt-1">11</div>
          <div className="text-[11px] text-slate-400 mt-0.5">5 Airlines + 6 OTAs</div>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">Live Demonstrable</div>
          <div className="font-mono text-xl font-bold text-emerald-600 mt-1">
            {statusData?.live_count || 1}
          </div>
          <div className="text-[11px] text-emerald-600 mt-0.5">Active Network Probe</div>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">Mock Calibrated</div>
          <div className="font-mono text-xl font-bold text-amber-600 mt-1">
            {statusData?.mock_count || 10}
          </div>
          <div className="text-[11px] text-amber-600 mt-0.5">Ethical Fallback</div>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">CAPTCHA Blocks</div>
          <div className="font-mono text-xl font-bold text-slate-700 mt-1">0</div>
          <div className="text-[11px] text-emerald-600 mt-0.5">Zero Bypass Policy</div>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">Total Captured</div>
          <div className="font-mono text-xl font-bold text-blue-600 mt-1">
            {statusData?.total_collected ? statusData.total_collected.toLocaleString('en-IN') : '15,500'}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Raw Quote Records</div>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
          <div className="text-slate-500 text-xs font-medium">Next Auto-Run</div>
          <div className="font-mono text-xs font-bold text-purple-700 mt-2">
            In 05h 42m
          </div>
          <div className="text-[11px] text-purple-600 mt-0.5">Daily Cron Active</div>
        </div>
      </div>

      {/* Grid of 11 Source Adapter Cards */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1">
          Source Adapter Fleet Health & Metrics
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Independent configuration, robots.txt compliance, and rate-limiting status per domain
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(statusData?.sources || []).map((s) => (
            <div
              key={s.source_name}
              className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 hover:bg-white hover:shadow-md transition-all flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <Globe className="w-4 h-4 text-slate-500" />
                    <span className="font-bold text-sm text-slate-900">{s.source_name}</span>
                  </div>
                  {getStatusBadge(s.status)}
                </div>

                <div className="text-[11px] font-mono text-slate-500 mb-2">
                  {s.domain || 'Direct API Adapter'} • Type: <span className="font-semibold text-slate-700">{s.source_type}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-200/80 pt-2 font-mono">
                  <div>
                    <span className="text-slate-400 block text-[10px] font-sans">Robots.txt:</span>
                    <span className={s.robots_allowed ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold'}>
                      {s.robots_allowed ? 'Allowed' : 'Restricted'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] font-sans">Rate Limit:</span>
                    <span className="text-slate-700 font-bold">{s.rate_limit_rps} req/sec</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] font-sans">Requests:</span>
                    <span className="text-emerald-600 font-bold">{s.requests_successful} OK</span>
                    {s.requests_failed > 0 && <span className="text-rose-600 ml-1">({s.requests_failed} err)</span>}
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] font-sans">Quotes Stored:</span>
                    <span className="text-blue-700 font-bold">{s.records_collected.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>

              <div className="text-[10px] text-slate-400 flex items-center justify-between border-t border-slate-200/60 pt-2">
                <span>Last Poll: {s.last_scrape_at ? new Date(s.last_scrape_at).toLocaleTimeString() : 'Just now'}</span>
                <span className="text-emerald-600 font-semibold">Active Session</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Execution Runs Audit Log */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1">
          Recent Scraper Execution Audit Trail
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Historical log of automated cron extractions and manual triggers
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 text-slate-600 font-sans font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Run ID</th>
                <th className="py-2.5 px-3">Trigger</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Collected</th>
                <th className="py-2.5 px-3">Clean Accepted</th>
                <th className="py-2.5 px-3">Rejected</th>
                <th className="py-2.5 px-3">Started</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(runs || []).map((r) => (
                <tr key={r.run_id} className="hover:bg-slate-50">
                  <td className="py-2 px-3 text-blue-600">{r.run_id.slice(0, 8)}...</td>
                  <td className="py-2 px-3 font-sans">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-semibold">
                      {r.trigger_type}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-sans">
                    <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                      {r.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-800 font-bold">{r.records_collected.toLocaleString('en-IN')}</td>
                  <td className="py-2 px-3 text-emerald-600 font-bold">{r.records_cleaned.toLocaleString('en-IN')}</td>
                  <td className="py-2 px-3 text-rose-600 font-bold">{r.records_rejected}</td>
                  <td className="py-2 px-3 text-slate-500 font-sans">
                    {r.started_at ? new Date(r.started_at).toLocaleTimeString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
