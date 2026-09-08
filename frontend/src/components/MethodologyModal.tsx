import React from 'react';
import { X, HelpCircle, BookOpen, Layers, ShieldCheck } from 'lucide-react';

interface MethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MethodologyModal: React.FC<MethodologyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-700 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-white font-heading">AirFareX Index Methodology (APIX_v1)</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300">
          {/* Section 1: Mathematical Formula */}
          <div>
            <h3 className="text-xs font-semibold uppercase text-cyan-400 tracking-wider mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              1. Laspeyres Price Index Framework
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              AirFareX calculates route-level indices I<sub>i,t</sub> and a national aggregate index APIx<sub>t</sub> using a modified Laspeyres framework:
            </p>
            <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 font-mono text-xs text-cyan-300 my-2 space-y-1">
              <div>I(i,t) = ( P(i,t) / P(i,0) ) &times; 100</div>
              <div>APIx(t) = &Sigma;( w_i &times; I(i,t) ) / &Sigma;( w_i )</div>
            </div>
            <ul className="text-xs text-slate-400 space-y-1 list-disc pl-4">
              <li><strong>P(i,t)</strong>: Representative median total fare for route <i>i</i> on date <i>t</i>.</li>
              <li><strong>P(i,0)</strong>: Baseline median total fare for route <i>i</i> during base period.</li>
              <li><strong>w_i</strong>: Normalized weight for route <i>i</i> based on domestic passenger volume.</li>
            </ul>
          </div>

          {/* Section 2: Skewness Resistance */}
          <div>
            <h3 className="text-xs font-semibold uppercase text-cyan-400 tracking-wider mb-2 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              2. Representative Fare Aggregation
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Airfare distributions exhibit high right-skewness due to last-minute dynamic pricing spikes. To avoid distortion, AirFareX uses the <strong>median total fare</strong> across non-outlier quotes per route and advance purchase window (T+1, T+7, T+15, T+30, T+45).
            </p>
          </div>

          {/* Section 3: Data Quality & Outlier Filtering */}
          <div>
            <h3 className="text-xs font-semibold uppercase text-cyan-400 tracking-wider mb-2">
              3. Data Quality & Outlier Treatment
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Statistical outliers are identified using <strong>Median Absolute Deviation (MAD = 3.0)</strong> and Interquartile Range (IQR = 1.5x). Outliers are flagged with <code className="text-amber-400">outlier_flag = True</code> and preserved in the audit log for reproducibility, but excluded from index calculation.
            </p>
          </div>

          {/* Section 4: Weights Disclaimer */}
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300">
            <strong className="font-semibold">Demo Weights Notice:</strong> Route weights in <code className="font-mono">config/routes.yaml</code> are marked as <code className="font-mono text-amber-200">DEMO_WEIGHTS</code> for evaluation. They can be replaced with official DGCA or NSO passenger volume weights without altering application code.
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Methodology Version: <strong className="text-cyan-400 font-mono">APIX_v1</strong></span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-cyan-500 text-slate-950 font-bold rounded-lg hover:bg-cyan-400 transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
