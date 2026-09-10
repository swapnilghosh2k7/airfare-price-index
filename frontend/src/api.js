/**
 * API Client for APIx Backend Services
 */

const API_BASE = '/api';

export async function fetchKPIs() {
  const res = await fetch(`${API_BASE}/index/current`);
  if (!res.ok) throw new Error('Failed to fetch current index KPIs');
  return res.json();
}

export async function fetchDailyIndex(startDate, endDate) {
  let url = `${API_BASE}/index/daily?limit=90`;
  if (startDate) url += `&start_date=${startDate}`;
  if (endDate) url += `&end_date=${endDate}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch daily index');
  return res.json();
}

export async function fetchWeeklyIndex() {
  const res = await fetch(`${API_BASE}/index/weekly`);
  if (!res.ok) throw new Error('Failed to fetch weekly index');
  return res.json();
}

export async function fetchMonthlyIndex() {
  const res = await fetch(`${API_BASE}/index/monthly`);
  if (!res.ok) throw new Error('Failed to fetch monthly index');
  return res.json();
}

export async function fetchHeatmap() {
  const res = await fetch(`${API_BASE}/analytics/heatmap`);
  if (!res.ok) throw new Error('Failed to fetch route heatmap');
  return res.json();
}

export async function fetchLeadTime(route) {
  const url = route ? `${API_BASE}/analytics/lead-time?route=${route}` : `${API_BASE}/analytics/lead-time`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch lead-time elasticity');
  return res.json();
}

export async function fetchRouteDetails(routeCode) {
  const res = await fetch(`${API_BASE}/analytics/route/${routeCode}`);
  if (!res.ok) throw new Error(`Failed to fetch route details for ${routeCode}`);
  return res.json();
}

export async function fetchAirlineComparison() {
  const res = await fetch(`${API_BASE}/analytics/airlines`);
  if (!res.ok) throw new Error('Failed to fetch airline comparisons');
  return res.json();
}

export async function fetchFareComponents() {
  const res = await fetch(`${API_BASE}/analytics/components`);
  if (!res.ok) throw new Error('Failed to fetch fare components');
  return res.json();
}

export async function fetchBacktest() {
  const res = await fetch(`${API_BASE}/backtest`);
  if (!res.ok) throw new Error('Failed to fetch backtest results');
  return res.json();
}

export async function uploadDGCAReference(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/backtest/upload-dgca`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload DGCA benchmark CSV');
  return res.json();
}

export async function fetchScraperStatus() {
  const res = await fetch(`${API_BASE}/scraper/status`);
  if (!res.ok) throw new Error('Failed to fetch scraper status');
  return res.json();
}

export async function triggerCollection(scoped = false) {
  const res = await fetch(`${API_BASE}/scraper/trigger?scoped=${scoped}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to trigger scraper collection');
  return res.json();
}

export async function fetchScraperRuns() {
  const res = await fetch(`${API_BASE}/scraper/runs`);
  if (!res.ok) throw new Error('Failed to fetch scraper runs');
  return res.json();
}

export async function fetchScraperErrors() {
  const res = await fetch(`${API_BASE}/scraper/errors`);
  if (!res.ok) throw new Error('Failed to fetch scraper errors');
  return res.json();
}

export async function fetchDataQuality() {
  const res = await fetch(`${API_BASE}/data-quality`);
  if (!res.ok) throw new Error('Failed to fetch data quality metrics');
  return res.json();
}

export async function fetchCPIAugmentation() {
  const res = await fetch(`${API_BASE}/cpi-augmentation`);
  if (!res.ok) throw new Error('Failed to fetch CPI augmentation data');
  return res.json();
}

export async function fetchFares(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/fares?${query}`);
  if (!res.ok) throw new Error('Failed to fetch fare observations');
  return res.json();
}

export async function fetchRoutes() {
  const res = await fetch(`${API_BASE}/routes`);
  if (!res.ok) throw new Error('Failed to fetch routes');
  return res.json();
}

export async function updateRouteWeight(routeCode, weight) {
  const res = await fetch(`${API_BASE}/routes/weight`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ route_code: routeCode, weight }),
  });
  if (!res.ok) throw new Error('Failed to update route weight');
  return res.json();
}

export async function fetchMethodology() {
  const res = await fetch(`${API_BASE}/index/methodology`);
  if (!res.ok) throw new Error('Failed to fetch methodology specs');
  return res.json();
}
