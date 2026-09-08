import React from 'react';
import { DataQualitySummary } from '../types';
import { ShieldCheck, AlertCircle, Copy, BarChart2 } from 'lucide-react';

interface DataQualityPanelProps {
  quality: DataQualitySummary | null;
}

export const DataQualityPanel: React.FC<DataQualityPanelProps> = ({ quality }) => {
  if (!quality) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Data Quality & Integrity Monitoring
          </h3>
          <p className="text-xs text-slate-400">Automated multi-factor quality scoring, outlier & duplicate flags</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Mean Quality Score:</span>
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full font-bold font-mono text-xs">
            {quality.average_quality_score.toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Total Collected</span>
          </div>
          <div className="text-lg font-bold text-white font-mono">{quality.total_quotes.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Valid Observations</span>
          </div>
          <div className="text-lg font-bold text-emerald-400 font-mono">{quality.valid_quotes.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
            <span>MAD/IQR Outliers</span>
          </div>
          <div className="text-lg font-bold text-amber-400 font-mono">{quality.outlier_quotes.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Copy className="w-3.5 h-3.5 text-rose-400" />
            <span>Duplicates Flagged</span>
          </div>
          <div className="text-lg font-bold text-rose-400 font-mono">{quality.duplicate_quotes.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
};
