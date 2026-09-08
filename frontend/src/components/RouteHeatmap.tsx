import React from 'react';
import { RouteItem } from '../types';
import { Layers } from 'lucide-react';

interface RouteHeatmapProps {
  routes: RouteItem[];
}

export const RouteHeatmap: React.FC<RouteHeatmapProps> = ({ routes }) => {
  // Representative simulated prices matrix per route & advance purchase window
  const leadTimes = [1, 7, 15, 30, 45];

  const getFareEstimate = (weight: number, lead: number) => {
    const base = 3000 + weight * 12000;
    const mult = 1.0 + 1.25 * Math.exp(-0.065 * lead);
    return Math.round(base * mult);
  };

  const getHeatColor = (fare: number) => {
    if (fare > 12000) return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
    if (fare > 9000) return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
    if (fare > 6500) return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
    return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            Advance Purchase Route Fare Matrix
          </h3>
          <p className="text-xs text-slate-400">Median Total Fare (INR) across advance booking windows</p>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-emerald-500"></span> &lt; ₹6.5k</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-cyan-500"></span> ₹6.5k-9k</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-amber-500"></span> ₹9k-12k</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-rose-500"></span> &gt; ₹12k</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">Route</th>
              {leadTimes.map(lt => (
                <th key={lt} className="py-2.5 px-3 font-semibold text-center">T+{lt}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {routes.map(r => (
              <tr key={r.route_code} className="hover:bg-slate-900/50 transition-colors">
                <td className="py-2.5 px-3 font-medium text-white flex items-center gap-2">
                  <span className="font-mono text-cyan-400 font-bold">{r.route_code}</span>
                  <span className="text-[11px] text-slate-500">({r.origin_city}-{r.destination_city})</span>
                </td>
                {leadTimes.map(lt => {
                  const fare = getFareEstimate(r.weight, lt);
                  const colorClass = getHeatColor(fare);
                  return (
                    <td key={lt} className="py-2.5 px-2 text-center">
                      <span className={`inline-block px-2.5 py-1 rounded-lg border font-mono font-semibold text-xs ${colorClass}`}>
                        ₹{fare.toLocaleString('en-IN')}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
