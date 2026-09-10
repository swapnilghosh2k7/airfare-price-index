import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import KPIRibbon from './components/KPIRibbon';
import OverviewDashboard from './views/OverviewDashboard';
import RouteBasketView from './views/RouteBasketView';
import AirlineAnalyticsView from './views/AirlineAnalyticsView';
import LeadTimeView from './views/LeadTimeView';
import CPIAugmentationView from './views/CPIAugmentationView';
import BacktestingView from './views/BacktestingView';
import ScraperMonitorView from './views/ScraperMonitorView';
import DataQualityView from './views/DataQualityView';
import DataExplorerView from './views/DataExplorerView';
import MethodologyView from './views/MethodologyView';

import {
  fetchKPIs, fetchDailyIndex, fetchHeatmap, fetchLeadTime,
  fetchFareComponents, fetchRoutes, triggerCollection
} from './api';

import {
  BarChart3, MapPin, Layers, Clock, ShieldAlert,
  ShieldCheck, Activity, Filter, Database, BookOpen
} from 'lucide-react';

const TABS = [
  { id: 'overview', label: 'Executive Dashboard', icon: BarChart3 },
  { id: 'routes', label: 'Route Basket & Analytics', icon: MapPin },
  { id: 'airlines', label: 'Airline Analytics', icon: Layers },
  { id: 'leadtime', label: 'Lead-Time Elasticity', icon: Clock },
  { id: 'cpi', label: 'CPI Augmentation', icon: ShieldAlert },
  { id: 'backtest', label: '30-Day Backtesting', icon: ShieldCheck },
  { id: 'scraper', label: 'Scraper Monitor', icon: Activity },
  { id: 'quality', label: 'Data Quality & Governance', icon: Filter },
  { id: 'explorer', label: 'Data Explorer & Export', icon: Database },
  { id: 'methodology', label: 'Methodology & API', icon: BookOpen },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [demoMode, setDemoMode] = useState(true);
  const [isScraping, setIsScraping] = useState(false);
  const [selectedRouteCode, setSelectedRouteCode] = useState('DEL-BOM');

  // Core Data States
  const [kpis, setKpis] = useState(null);
  const [dailyIndex, setDailyIndex] = useState(null);
  const [heatmap, setHeatmap] = useState([]);
  const [leadTime, setLeadTime] = useState([]);
  const [components, setComponents] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [kpiRes, dailyRes, heatRes, leadRes, compRes, routesRes] = await Promise.all([
        fetchKPIs(),
        fetchDailyIndex(),
        fetchHeatmap(),
        fetchLeadTime(),
        fetchFareComponents(),
        fetchRoutes()
      ]);
      setKpis(kpiRes);
      setDailyIndex(dailyRes);
      setHeatmap(heatRes);
      setLeadTime(leadRes);
      setComponents(compRes);
      setRoutes(routesRes);
    } catch (err) {
      console.error('Error loading initial APIx dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleTriggerScrape = async (scoped = true) => {
    try {
      setIsScraping(true);
      await triggerCollection(scoped);
      await loadInitialData();
    } catch (err) {
      console.error('Scraper trigger error:', err);
    } finally {
      setIsScraping(false);
    }
  };

  const handleRouteSelect = (routeCode) => {
    setSelectedRouteCode(routeCode);
    setActiveTab('routes');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* 1. Official Header */}
      <Header
        kpis={kpis}
        demoMode={demoMode}
        setDemoMode={setDemoMode}
        onTriggerScrape={handleTriggerScrape}
        isScraping={isScraping}
      />

      {/* 2. Top Navigation Tabs Bar */}
      <nav className="bg-white border-b border-slate-200 sticky top-[89px] z-40 shadow-xs overflow-x-auto">
        <div className="px-6 flex space-x-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 whitespace-nowrap transition-all ${
                  isActive
                    ? 'border-blue-600 text-blue-700 bg-blue-50/50'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* 3. Main Dashboard Body */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        {/* KPI Ribbon Displayed on All Tabs */}
        <KPIRibbon kpis={kpis} />

        {/* Dynamic Tab View Content */}
        {activeTab === 'overview' && (
          <OverviewDashboard
            dailyIndex={dailyIndex}
            heatmap={heatmap}
            leadTime={leadTime}
            components={components}
            onSelectRoute={handleRouteSelect}
          />
        )}

        {activeTab === 'routes' && (
          <RouteBasketView
            routes={routes}
            selectedRouteCode={selectedRouteCode}
            onSelectRoute={setSelectedRouteCode}
            onWeightsChanged={loadInitialData}
          />
        )}

        {activeTab === 'airlines' && <AirlineAnalyticsView />}

        {activeTab === 'leadtime' && <LeadTimeView leadTime={leadTime} />}

        {activeTab === 'cpi' && <CPIAugmentationView />}

        {activeTab === 'backtest' && <BacktestingView />}

        {activeTab === 'scraper' && (
          <ScraperMonitorView onScrapeCompleted={loadInitialData} />
        )}

        {activeTab === 'quality' && <DataQualityView />}

        {activeTab === 'explorer' && <DataExplorerView routes={routes} />}

        {activeTab === 'methodology' && <MethodologyView />}
      </main>

      {/* 4. Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 text-xs py-6 mt-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-200">APIx: Real-time Airfare Price Index for India</span>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Developed for the Smart India Hackathon (SIH) • Ministry of Statistics and Programme Implementation (MoSPI) • Reserve Bank of India (RBI)
            </p>
          </div>
          <div className="flex items-center space-x-4 text-[11px]">
            <span>FastAPI Backend (Port 8000)</span>
            <span>•</span>
            <span>React + Vite (Port 5173)</span>
            <span>•</span>
            <span>Laspeyres Weighted Model</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
