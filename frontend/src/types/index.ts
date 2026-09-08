export interface RouteItem {
  id: number;
  route_code: string;
  origin: string;
  destination: string;
  origin_city: string;
  destination_city: string;
  weight: number;
  active: boolean;
}

export interface CarrierItem {
  id: number;
  name: string;
  iata_code: string;
  source_type: string;
  active: boolean;
}

export interface IndexSummary {
  latest_date: string;
  national_apix: number;
  daily_change_pct: number;
  weekly_change_pct: number;
  monthly_change_pct: number;
  total_observations: number;
  base_period: string;
  methodology_version: string;
}

export interface IndexObservationItem {
  id: number;
  observation_date: string;
  route_code: string;
  lead_time_bucket: number;
  route_index: number;
  national_index: number;
  base_period: string;
  weight: number;
  sample_count: number;
  methodology_version: string;
}

export interface LeadTimeAnalytics {
  lead_time_days: number;
  lead_time_label: string;
  median_fare: number;
  mean_fare: number;
  min_fare: number;
  max_fare: number;
  sample_count: number;
}

export interface CarrierAnalytics {
  carrier: string;
  median_total_fare: number;
  mean_base_fare: number;
  mean_taxes: number;
  mean_airport_fee: number;
  mean_fuel_surcharge: number;
  mean_convenience_fee: number;
  mean_user_development_fee: number;
  quote_count: number;
}

export interface RouteAnalytics {
  route_code: string;
  current_route_index: number;
  earliest_route_index: number;
  inflation_30d_pct: number;
  volatility_std_dev: number;
  coefficient_of_variation_pct: number;
  observation_days: number;
}

export interface FareQuoteItem {
  id: number;
  observation_timestamp: string;
  origin: string;
  destination: string;
  departure_date: string;
  lead_time_days: number;
  carrier: string;
  flight_number: string;
  fare_class: string;
  base_fare: number;
  taxes: number;
  airport_fee: number;
  fuel_surcharge: number;
  user_development_fee: number;
  convenience_fee: number;
  other_fee: number;
  total_fare: number;
  currency: string;
  source: string;
  availability_status: string;
  collection_status: string;
  raw_hash: string;
}

export interface DataQualitySummary {
  total_quotes: number;
  valid_quotes: number;
  outlier_quotes: number;
  duplicate_quotes: number;
  average_quality_score: number;
  missing_fields_count: number;
}

export interface CollectionRunItem {
  id: number;
  started_at: string;
  completed_at: string | null;
  source: string;
  routes_requested: number;
  quotes_collected: number;
  quotes_valid: number;
  quotes_rejected: number;
  status: string;
  error_summary: string | null;
}
