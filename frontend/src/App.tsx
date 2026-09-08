import React, { useState, useEffect } from 'react';
import { ApiService } from './services/api';
import {
  IndexSummary,
  IndexObservationItem,
  RouteItem,
  CarrierItem,
  LeadTimeAnalytics,
  CarrierAnalytics,
  DataQualitySummary
} from './types';

import { Header } from './components/Header';
import { KpiCard } from './components/KpiCard';
import { IndexChart } from './components/IndexChart';
import { RouteHeatmap } from './components/RouteHeatmap';
import { LeadTimeCurve } from './components/LeadTimeCurve';
import { CarrierComparisonChart } from './components/CarrierComparisonChart';
import { FareCompositionChart } from './components/FareCompositionChart';
import { DataQualityPanel } from './components/DataQualityPanel';
import { MethodologyModal } from './components/MethodologyModal';

import { DataExplorerPage } from './pages/DataExplorerPage';
import { CollectionAdminPage } from './pages/CollectionAdminPage';

import { Plane, TrendingUp, Calendar, Layers, ShieldCheck, Database } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'data' | 'collection'>('dashboard');
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);

  // Core API State
  const [summary, setSummary] = useState<IndexSummary | null>(null);
  const [routes, setRoutes] = useState<RouteItem[]>([]);
  const [carriers, setCarriers] = useState<CarrierItem[]>([]);
  const [selectedRoute, setSelectedRoute] = useState('NATIONAL');
  const [indexHistory, setIndexHistory] = useState<IndexObservationItem[]>([]);
  const [leadTimeData, setLeadTimeData] = useState<LeadTimeAnalytics[]>([]);
  const [carrierData, setCarrierData] = useState<CarrierAnalytics[]>([]);
  const [qualitySummary, setQualitySummary] = useState<DataQualitySummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [sumRes, rRes, cRes, ltRes, crRes, qRes] = await Promise.all([
        ApiService.getIndexSummary(),
        ApiService.getRoutes(),
        ApiService.getCarriers(),
        ApiService.getLeadTimeAnalytics(),
        ApiService.getCarrierAnalytics(),
        ApiService.getDataQualitySummary()
      ]);

      setSummary(sumRes);
      setRoutes(rRes);
      setCarriers(cRes);
      setLeadTimeData(ltRes);
      setCarrierData(crRes);
      setQualitySummary(qRes);

      // Load initial index history
      const idxRes = await ApiService.getIndexHistory('NATIONAL', 0);
      setIndexHistory(idxRes);
    } catch (err) {
      console.error("Failed to load AirFareX application data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Update index history when route changes
  useEffect(() => {
    const fetchRouteIndex = async () => {
      try {
        const res = await ApiService.getIndexHistory(selectedRoute, 0);
        setIndexHistory(res);
      } catch (err) {
        console.error("Failed to fetch route index", err);
      }
    };
    fetchRouteIndex();
  }, [selectedRoute]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navigation Header */}
      <Header
        summary={summary}
        onOpenMethodology={() => setIsMethodologyOpen(true)}
        onRefresh={loadAllData}
        activeTab={activeTab}
        setActiveTab={tab => setActiveTab(tab as any)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {activeTab === 'dashboard' && (
          <>
            {/* KPI Cards Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Airfare Price Index (APIx)"
                value={summary ? summary.national_apix.toFixed(2) : '100.00'}
                changePct={summary ? summary.monthly_change_pct : 0}
                changePeriod="30D"
                icon={<TrendingUp className="w-5 h-5 text-cyan-400" />}
                highlightColor="cyan"
              />

              <KpiCard
                title="Daily Index Shift"
                value={summary ? `${summary.daily_change_pct > 0 ? '+' : ''}${summary.daily_change_pct.toFixed(2)}%` : '0.00%'}
                changePct={summary ? summary.daily_change_pct : 0}
                changePeriod="24H"
                icon={<Calendar className="w-5 h-5 text-indigo-400" />}
                highlightColor="indigo"
              />

              <KpiCard
                title="Observed Fare Quotes"
                value={summary ? summary.total_observations.toLocaleString() : '0'}
                subtitle={`${routes.length} Core Routes • ${carriers.length} Carriers`}
                icon={<Database className="w-5 h-5 text-emerald-400" />}
                highlightColor="emerald"
              />

              <KpiCard
                title="Data Quality Index"
                value={qualitySummary ? `${qualitySummary.average_quality_score.toFixed(1)}%` : '100.0%'}
                subtitle={`${qualitySummary ? qualitySummary.valid_quotes.toLocaleString() : 0} Valid Observations`}
                icon={<ShieldCheck className="w-5 h-5 text-amber-400" />}
                highlightColor="amber"
              />
            </div>

            {/* Primary Main Chart: Airfare Price Index */}
            <IndexChart
              data={indexHistory}
              routes={routes}
              selectedRoute={selectedRoute}
              onSelectRoute={setSelectedRoute}
            />

            {/* Advance Purchase Matrix & Lead Time Elasticity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <RouteHeatmap routes={routes} />
              <LeadTimeCurve data={leadTimeData} />
            </div>

            {/* Carrier Comparison & Composition */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <CarrierComparisonChart data={carrierData} />
              <FareCompositionChart data={carrierData} />
            </div>

            {/* Data Quality & Integrity Panel */}
            <DataQualityPanel quality={qualitySummary} />
          </>
        )}

        {activeTab === 'data' && (
          <DataExplorerPage routes={routes} carriers={carriers} />
        )}

        {activeTab === 'collection' && (
          <CollectionAdminPage />
        )}
      </main>

      {/* Methodology Modal */}
      <MethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <strong>AirFareX Platform v1.0.0</strong> — Developed for NSO / MoSPI / RBI Transport CPI Augmentation Research.
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <button onClick={() => setIsMethodologyOpen(true)} className="hover:text-cyan-400 transition-colors">
              Methodology Specification
            </button>
            <span>•</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-cyan-400 transition-colors">
              OpenAPI REST Docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
