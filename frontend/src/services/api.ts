import {
  IndexSummary,
  IndexObservationItem,
  RouteItem,
  CarrierItem,
  LeadTimeAnalytics,
  CarrierAnalytics,
  RouteAnalytics,
  FareQuoteItem,
  DataQualitySummary,
  CollectionRunItem
} from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const ApiService = {
  getHealth: () => fetchJson<{ status: string; app_name: string; version: string; demo_mode: boolean; methodology_version: string }>('/health'),
  
  getRoutes: () => fetchJson<RouteItem[]>('/routes'),
  getCarriers: () => fetchJson<CarrierItem[]>('/carriers'),

  getIndexSummary: () => fetchJson<IndexSummary>('/index'),
  getLatestIndex: () => fetchJson<IndexObservationItem[]>('/index/latest'),
  getIndexHistory: (route?: string, leadTime: number = 0) => {
    const params = new URLSearchParams();
    if (route) params.append('route', route);
    params.append('lead_time', leadTime.toString());
    return fetchJson<IndexObservationItem[]>(`/index/history?${params.toString()}`);
  },

  getLeadTimeAnalytics: (route?: string) => {
    const url = route ? `/analytics/lead-time?route=${encodeURIComponent(route)}` : '/analytics/lead-time';
    return fetchJson<LeadTimeAnalytics[]>(url);
  },

  getCarrierAnalytics: (route?: string) => {
    const url = route ? `/analytics/carriers?route=${encodeURIComponent(route)}` : '/analytics/carriers';
    return fetchJson<CarrierAnalytics[]>(url);
  },

  getRouteAnalytics: () => fetchJson<RouteAnalytics[]>('/analytics/routes'),

  getExperimentalForecast: () => fetchJson<Array<{ forecast_date: string; forecast_index: number; model: string; status: string }>>('/analytics/forecast'),
  getPriceAlerts: () => fetchJson<Array<{ type: string; severity: string; route_code: string; change_7d_pct: number; message: string; date: string }>>('/analytics/alerts'),
  getDemandPressureProxy: () => fetchJson<{ demand_pressure_score: number; limited_availability_pct: number; t1_to_t30_price_ratio: number; status: string; description: string }>('/analytics/demand-proxy'),

  getFares: (page: number = 1, size: number = 50, filters?: Record<string, string>) => {
    const params = new URLSearchParams({ page: page.toString(), size: size.toString() });
    if (filters) {
      Object.entries(filters).forEach(([k, v]) => {
        if (v) params.append(k, v);
      });
    }
    return fetchJson<{ total: number; page: number; size: number; pages: number; data: FareQuoteItem[] }>(`/fares?${params.toString()}`);
  },

  getDataQualitySummary: () => fetchJson<DataQualitySummary>('/data-quality'),
  getCollectionRuns: () => fetchJson<CollectionRunItem[]>('/collection-runs'),

  triggerRunDemo: async () => {
    const res = await fetch(`${API_BASE}/collection/run-demo`, { method: 'POST' });
    return res.json();
  },

  triggerRebuildIndex: async () => {
    const res = await fetch(`${API_BASE}/collection/rebuild-index`, { method: 'POST' });
    return res.json();
  }
};
