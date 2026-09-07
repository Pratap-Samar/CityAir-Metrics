export type DashboardSummary = {
  total_cities: number;
  average_aqi: number | null;
  previous_period_aqi: number | null;
  aqi_absolute_change: number | null;
  aqi_percentage_change: number | null;
  aqi_direction: "increasing" | "decreasing" | "stable" | null;
  average_temperature_c: number | null;
  previous_period_temperature_c: number | null;
  temperature_absolute_change: number | null;
  temperature_percentage_change: number | null;
  temperature_direction: "increasing" | "decreasing" | "stable" | null;
  last_observation_at: string | null;
  weather_freshness_minutes: number | null;
  air_quality_freshness_minutes: number | null;
  data_freshness_minutes: number | null;
};

export type DashboardMapData = {
  city_id: number;
  city_name: string;
  country: string;
  latitude: number;
  longitude: number;
  aqi: number | null;
  pm2_5: number | null;
  pm10: number | null;
  temperature_c: number | null;
  humidity_percent: number | null;
  wind_speed_kmh: number | null;
  precipitation_mm: number | null;
  weather_observed_at: string | null;
  air_quality_observed_at: string | null;
};

export type TimeSeriesTrend = {
  timestamp: string;
  value: number | null;
  observation_count: number;
};

export type BiggestChange = {
  city_id: number;
  name: string;
  country: string;
  current_value: number | null;
  previous_value: number | null;
  absolute_change: number | null;
  percentage_change: number | null;
};

export type CityRanking = {
  city_id: number;
  name: string;
  country: string;
  value: number | null;
  previous_value: number | null;
  change: number | null;
  percentage_change: number | null;
};

export type PipelineStatus = {
  status: string;
  is_active: boolean;
  started_at: string | null;
  completed_at: string | null;
  cities_processed: number | null;
  cities_failed: number | null;
  duration_seconds: number | null;
  error_message: string | null;
};

export type ForecastHourly = {
  time: string;
  temperature_2m: number | null;
  apparent_temperature: number | null;
  precipitation_probability: number | null;
  weather_code: number | null;
};

export type ForecastDaily = {
  time: string;
  weather_code: number | null;
  temperature_2m_max: number | null;
  temperature_2m_min: number | null;
  precipitation_probability_max: number | null;
};

export type ForecastResponse = {
  hourly: ForecastHourly[];
  daily: ForecastDaily[];
};
