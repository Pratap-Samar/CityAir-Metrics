export type AnalyticsCity = {
  city_id: number;
  name: string;
  country: string;
  weather: {
    observed_at: string | null;
    temperature_c: number | null;
    humidity_percent: number | null;
    apparent_temperature_c: number | null;
    precipitation_mm: number | null;
    weather_code: number | null;
    wind_speed_kmh: number | null;
    wind_direction_degrees: number | null;
  };
  air_quality: {
    observed_at: string | null;
    pm10: number | null;
    pm2_5: number | null;
    carbon_monoxide: number | null;
    nitrogen_dioxide: number | null;
    sulphur_dioxide: number | null;
    ozone: number | null;
    us_aqi: number | null;
  };
};

export type WeatherHistory = {
  observed_at: string;
  temperature_c: number | null;
  humidity_percent: number | null;
  apparent_temperature_c: number | null;
  precipitation_mm: number | null;
  wind_speed_kmh: number | null;
};

export type AirQualityHistory = {
  observed_at: string;
  pm10: number | null;
  pm2_5: number | null;
  carbon_monoxide: number | null;
  nitrogen_dioxide: number | null;
  sulphur_dioxide: number | null;
  ozone: number | null;
  us_aqi: number | null;
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

export type PipelineStatus = {
  status: string;
  is_active: boolean;
  started_at: string | null;
  completed_at: string | null;
  cities_processed: number | null;
  cities_failed: number | null;
};
