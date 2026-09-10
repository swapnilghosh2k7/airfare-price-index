import React, { useState, useEffect } from 'react';
import {
  BookOpen, Code, ExternalLink, Calculator,
  Scale, FileText, CheckCircle2, Shield
} from 'lucide-react';
import { fetchMethodology } from '../api';

export default function MethodologyView() {
  const [specs, setSpecs] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchMethodology();
        setSpecs(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Calculator className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-900">
                Index Methodology & Mathematical Specifications
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Complete, reproducible mathematical formulation of the Airfare Price Index (APIx) for MoSPI/NSO integration.
            </p>
          </div>

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm"
          >
            <span>Open Swagger API Spec</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Mathematical Formulation Card */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-blue-600" />
          Laspeyres-Type Weighted Price Relative Formulation
        </h3>

        <div className="p-4 bg-slate-900 text-amber-300 rounded-xl font-mono text-sm leading-relaxed overflow-x-auto border border-slate-800">
          <div className="text-slate-400 text-xs mb-2">/* APIx Core Formula */</div>
          <div>APIx(t) = ∑ [ W(r) × PR(r, t) ]</div>
          <div className="text-xs text-slate-400 mt-2">where:</div>
          <div className="pl-4 text-xs text-slate-300">
            • PR(r, t) = [ P̄(r, t) / P̄(r, t₀) ] × 100 &nbsp;&nbsp;(Price Relative for route r)<br/>
            • P̄(r, t) = Average clean economy airfare for route r at date t across advance windows<br/>
            • P̄(r, t₀) = Baseline reference airfare at base period (t₀ = {specs?.base_period_date || '2026-08-10'})<br/>
            • W(r) = Official DGCA passenger revenue share weight, normalized such that ∑ W(r) = 1.000
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="font-bold text-slate-900 block mb-1">Base Period Definition:</span>
            Reference date: <span className="font-mono text-blue-700 font-bold">{specs?.base_period_date || '2026-08-10'}</span>.<br/>
            Base Index Value = <strong>100.00</strong>.
          </div>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="font-bold text-slate-900 block mb-1">Route Weight Normalization:</span>
            Total Basket Weight: <span className="font-mono text-emerald-700 font-bold">{specs?.total_weight || '1.0000'} (100.0%)</span> across {specs?.route_basket_count || 20} routes.
          </div>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="font-bold text-slate-900 block mb-1">Stratified Lead-Times:</span>
            Mandatory capture across 5 advance purchase horizons: <strong>T+1, T+7, T+15, T+30, T+45</strong>.
          </div>
        </div>
      </div>

      {/* Route Weights Audit Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-1">
          Active Domestic Basket Route Weights (DGCA Calibrated)
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Route weights derived from domestic passenger traffic volume statistics
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 text-slate-600 font-sans font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">City-Pair</th>
                <th className="py-2.5 px-3">Origin</th>
                <th className="py-2.5 px-3">Destination</th>
                <th className="py-2.5 px-3">Corridor</th>
                <th className="py-2.5 px-3">Weight W(r)</th>
                <th className="py-2.5 px-3">Weight Share (%)</th>
                <th className="py-2.5 px-3">Monthly Traffic Volume</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(specs?.routes || []).map((r) => (
                <tr key={r.route_code} className="hover:bg-slate-50">
                  <td className="py-2 px-3 font-bold text-blue-700">{r.route_code}</td>
                  <td className="py-2 px-3 text-slate-700">{r.origin}</td>
                  <td className="py-2 px-3 text-slate-700">{r.destination}</td>
                  <td className="py-2 px-3 font-sans text-slate-500">{r.region}</td>
                  <td className="py-2 px-3 font-bold text-slate-900">{r.weight.toFixed(3)}</td>
                  <td className="py-2 px-3 text-emerald-600 font-bold">{r.weight_pct}%</td>
                  <td className="py-2 px-3 text-slate-600">{r.traffic_volume.toLocaleString('en-IN')} pax</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Code Snippet for NSO / RBI Econometric Ingestion */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm space-y-3">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Code className="w-4 h-4 text-purple-600" />
          API Consumption Example (Python for NSO / RBI Statistical Analysts)
        </h3>

        <div className="bg-slate-900 text-slate-200 p-4 rounded-xl font-mono text-xs overflow-x-auto border border-slate-800">
          <pre>{`import httpx
import pandas as pd

# Fetch daily APIx index series for CPI Transport Subgroup augmentation
resp = httpx.get("http://localhost:8000/api/index/daily?limit=30")
data = resp.json()

# Convert to pandas DataFrame for econometric regression
df = pd.DataFrame(data["points"])
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

print("Latest APIx Value:", df["apix_value"].iloc[-1])
print("7-Day Moving Average:", df["apix_value"].rolling(7).mean().iloc[-1])`}</pre>
        </div>
      </div>
    </div>
  );
}
