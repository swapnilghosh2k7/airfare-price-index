import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  changePct?: number;
  changePeriod?: string;
  icon: React.ReactNode;
  highlightColor?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  changePct,
  changePeriod = '30D',
  icon,
  highlightColor = 'cyan'
}) => {
  const isPositive = changePct !== undefined && changePct > 0;
  const isNegative = changePct !== undefined && changePct < 0;

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800/80 relative overflow-hidden group hover:border-slate-700 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
          <div className="text-2xl font-bold text-white mt-1 font-heading tracking-tight flex items-baseline gap-2">
            {value}
          </div>
        </div>
        <div className={`p-2.5 rounded-xl bg-slate-900/90 text-${highlightColor}-400 border border-slate-800`}>
          {icon}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-xs">
        {changePct !== undefined ? (
          <div className="flex items-center gap-1.5">
            <span
              className={`px-2 py-0.5 rounded-full font-semibold flex items-center gap-1 ${
                isPositive
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : isNegative
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  : 'bg-slate-800 text-slate-400'
              }`}
            >
              {isPositive && <TrendingUp className="w-3 h-3" />}
              {isNegative && <TrendingDown className="w-3 h-3" />}
              {!isPositive && !isNegative && <Minus className="w-3 h-3" />}
              {changePct > 0 ? `+${changePct.toFixed(2)}%` : `${changePct.toFixed(2)}%`}
            </span>
            <span className="text-slate-500">{changePeriod} change</span>
          </div>
        ) : (
          <span className="text-slate-400">{subtitle || 'Active dataset'}</span>
        )}
        <span className="text-[10px] text-slate-500 uppercase font-mono">APIX_v1</span>
      </div>
    </div>
  );
};
