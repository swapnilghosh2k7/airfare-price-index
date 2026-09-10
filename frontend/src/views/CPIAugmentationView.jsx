import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, CheckCircle, ArrowRight, BookOpen,
  TrendingUp, Scale, Zap, FileText, Building2
} from 'lucide-react';
import { fetchCPIAugmentation } from '../api';

export default function CPIAugmentationView() {
  const [cpiData, setCpiData] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchCPIAugmentation();
        setCpiData(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Mandatory Regulatory & Official Notice Banner */}
      <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-amber-500 bg-white p-5 rounded-r-2xl shadow-sm">
        <div className="flex items-start space-x-3">
          <ShieldAlert className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
              Experimental Airfare Price Index for CPI Augmentation
              <span className="text-xs px-2 py-0.5 rounded font-mono font-medium bg-amber-100 text-amber-800 border border-amber-300">
                STATISTICAL RESEARCH PROTOTYPE
              </span>
            </h2>
            <p className="text-xs text-slate-600 mt-1 leading-relaxed">
              {cpiData?.official_disclaimer ||
                'This module represents an experimental academic/policy prototype for augmenting the Transport and Communication subgroup of the Indian Consumer Price Index (CPI). It is not an official release of the National Statistical Office (NSO) or Ministry of Statistics and Programme Implementation (MoSPI).'}
            </p>
          </div>
        </div>
      </div>

      {/* Comparative Matrix: Existing Manual Survey vs High-Frequency APIx */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Methodological Comparison Matrix
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Traditional NSO physical price collection vs High-Frequency automated web scraping
            </p>
          </div>
          <span className="text-xs font-mono font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md border border-blue-200">
            MoSPI Modernization Framework
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 w-1/5">Evaluation Dimension</th>
                <th className="py-3 px-4 w-2/5 bg-slate-100/70 text-slate-700">
                  Existing MoSPI Manual Survey
                </th>
                <th className="py-3 px-4 w-2/5 bg-blue-50/70 text-blue-900">
                  High-Frequency APIx System
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(cpiData?.comparison_matrix || []).map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-1.5">
                    <Scale className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                    {row.dimension}
                  </td>
                  <td className="py-3 px-4 text-slate-600 bg-slate-50/30">
                    <div className="font-medium text-rose-700">{row.existing_manual_method}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-800 bg-blue-50/20">
                    <div className="font-bold text-blue-800">{row.apix_high_frequency_method}</div>
                    <div className="text-[11px] text-emerald-600 font-medium mt-0.5 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3 flex-shrink-0" />
                      {row.improvement}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* RBI Monetary Policy Relevance & Macroeconomic Implications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card 1: Inflation Transmission */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-2 text-indigo-700 mb-2">
            <Building2 className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900">
              Reserve Bank of India (RBI) Monetary Policy Input
            </h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed mb-4">
            Under India's Flexible Inflation Targeting (FIT) framework, the RBI MPC targets headline CPI at 4% (+/- 2%).
            Airfare shocks from international crude oil and aviation turbine fuel (ATF) pass through rapidly to consumers.
          </p>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
              <span className="font-bold text-slate-800 block mb-1">Early-Warning Indicator:</span>
              APIx delivers real-time T+0 daily price signals, giving policymakers up to 14 days of advance visibility before official monthly CPI publication.
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
              <span className="font-bold text-slate-800 block mb-1">Fuel Pass-Through Disaggregation:</span>
              By isolating the fuel surcharge from base fare, APIx allows econometric decomposition into domestic demand shocks vs global commodity cost-push shocks.
            </div>
          </div>
        </div>

        {/* Card 2: Consumer Basket Shift */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-2 text-blue-700 mb-2">
            <TrendingUp className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900">
              Digital Transformation of Indian Air Travel
            </h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed mb-4">
            Over 90% of domestic Indian air passengers book tickets digitally via airline websites and Online Travel Aggregators (OTAs) subject to dynamic yield pricing.
          </p>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
              <span className="font-bold text-slate-800 block mb-1">Algorithmic Surge Capture:</span>
              Manual surveys miss weekend surcharges and festival spikes (Diwali, Chhath, Durga Puja). High-frequency APIx continuously samples all 5 advance booking windows.
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
              <span className="font-bold text-slate-800 block mb-1">Fiscal Auditability & Data Provenance:</span>
              Every observation preserves its cryptographic UUID, timestamp, airline, flight number, raw/clean status, and outlier diagnostic log.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
