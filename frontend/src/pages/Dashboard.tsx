import { useState, useEffect, useCallback } from "react";
import type { AnalyticsCity, WeatherHistory, AirQualityHistory, ForecastResponse } from "../types";
import { CitySelector } from "../components/CitySelector";
import { HistoricalChart } from "../components/HistoricalChart";
import { Forecast } from "../components/Forecast";
import { PipelineStatusIndicator } from "../components/PipelineStatusIndicator";
import { getWeatherCondition, getWeatherIconComponent } from "../utils/weather";
import { RefreshCw } from "lucide-react";
import { format, parseISO } from "date-fns";

const API_URL = "http://localhost:8000";

type DashboardProps = {
  cities: AnalyticsCity[];
  selectedCityId: number | null;
  onCityChange: (id: number) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
};

export const Dashboard = ({
  cities,
  selectedCityId,
  onCityChange,
  onRefresh,
  isRefreshing,
}: DashboardProps) => {
  const [weatherHistory, setWeatherHistory] = useState<WeatherHistory[]>([]);
  const [aqiHistory, setAqiHistory] = useState<AirQualityHistory[]>([]);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);

  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const [forecastLoading, setForecastLoading] = useState(true);
  const [forecastError, setForecastError] = useState<string | null>(null);

  const fetchHistoryAndForecast = useCallback(async () => {
    if (!selectedCityId) return;
    
    // Fetch History
    try {
      setHistoryLoading(true);
      setHistoryError(null);
      const [wRes, aqRes] = await Promise.all([
        fetch(`${API_URL}/weather/history/${selectedCityId}?hours=24`),
        fetch(`${API_URL}/air-quality/history/${selectedCityId}?hours=24`),
      ]);

      if (!wRes.ok || !aqRes.ok) throw new Error("Failed to load historical data");

      setWeatherHistory(await wRes.json());
      setAqiHistory(await aqRes.json());
    } catch (err) {
      setHistoryError(err instanceof Error ? err.message : "Error loading history");
    } finally {
      setHistoryLoading(false);
    }

    // Fetch Forecast
    try {
      setForecastLoading(true);
      setForecastError(null);
      const fRes = await fetch(`${API_URL}/weather/forecast/${selectedCityId}`);
      
      if (!fRes.ok) throw new Error("Failed to load forecast data");
      setForecast(await fRes.json());
    } catch (err) {
      setForecastError(err instanceof Error ? err.message : "Error loading forecast");
    } finally {
      setForecastLoading(false);
    }
  }, [selectedCityId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchHistoryAndForecast();
  }, [fetchHistoryAndForecast]);

  const handleRefresh = () => {
    onRefresh();
    fetchHistoryAndForecast();
  };

  const selectedCity = cities.find((city) => city.city_id === selectedCityId) ?? null;

  // Development weather preview override
  const devOverride = typeof window !== "undefined" 
    ? new URLSearchParams(window.location.search).get("weather") 
    : null;

  if (!selectedCity) {
    return (
      <div className="dashboard-content empty-state">
        <p>No city selected.</p>
      </div>
    );
  }

  const { weather, air_quality } = selectedCity;
  
  // Apply dev override for testing icons if present
  let effectiveWeatherCode = weather.weather_code;
  if (devOverride) {
    if (devOverride === "clear") effectiveWeatherCode = 0;
    else if (devOverride === "partly-cloudy") effectiveWeatherCode = 1;
    else if (devOverride === "cloudy") effectiveWeatherCode = 3;
    else if (devOverride === "rain") effectiveWeatherCode = 61;
    else if (devOverride === "snow") effectiveWeatherCode = 71;
    else if (devOverride === "thunderstorm" || devOverride === "storm") effectiveWeatherCode = 95;
  }

  const weatherCond = getWeatherCondition(effectiveWeatherCode);
  const MainWeatherIcon = getWeatherIconComponent(effectiveWeatherCode);
  
  const lastUpdated = weather.observed_at 
    ? format(parseISO(weather.observed_at), "HH:mm") 
    : "Unknown";

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-content">
        <header className="dashboard-header">
          <div className="header-title">
            <h1>{selectedCity.name}, {selectedCity.country}</h1>
            <p className="subtitle">{weatherCond} &middot; Updated {lastUpdated}</p>
          </div>
          <div className="header-actions">
            <PipelineStatusIndicator />
            <CitySelector
              cities={cities}
              selectedCityId={selectedCityId}
              onCityChange={onCityChange}
            />
            <button
              type="button"
              className="action-button icon-only"
              onClick={handleRefresh}
              disabled={isRefreshing || historyLoading || forecastLoading}
              title="Refresh data"
            >
              <RefreshCw size={18} className={isRefreshing ? "spin" : ""} />
            </button>
          </div>
        </header>

        <div className="dashboard-grid">
          
          <section className="dashboard-card current-weather-card">
            <div className="current-weather-main">
              {/* eslint-disable-next-line react-hooks/static-components */}
              <MainWeatherIcon size={56} className="hero-icon" />
              <div className="hero-temp-block">
                <span className="hero-temp">{weather.temperature_c ?? "—"}°C</span>
                <span className="hero-cond">{weatherCond}</span>
              </div>
            </div>
            <div className="current-weather-details">
              <div className="detail-row"><span>Feels like</span><strong>{weather.apparent_temperature_c ?? "—"}°C</strong></div>
              <div className="detail-row"><span>Humidity</span><strong>{weather.humidity_percent ?? "—"}%</strong></div>
              <div className="detail-row"><span>Wind</span><strong>{weather.wind_speed_kmh ?? "—"} km/h</strong></div>
              <div className="detail-row"><span>Rain</span><strong>{weather.precipitation_mm ?? "—"} mm</strong></div>
            </div>
          </section>

          <section className="dashboard-card air-quality-card">
            <h2 className="section-title">AIR QUALITY</h2>
            <div className="aq-layout">
              <div className="aq-primary">
                <div className="aq-metric">
                  <span className="aq-label">PM2.5</span>
                  <span className="aq-val">{air_quality.pm2_5 ?? "—"}<small>µg/m³</small></span>
                </div>
                <div className="aq-metric">
                  <span className="aq-label">US AQI</span>
                  <span className="aq-val">{air_quality.us_aqi ?? "—"}</span>
                </div>
              </div>
              <div className="aq-secondary">
                <div className="aq-row"><span>PM10</span><span>{air_quality.pm10 ?? "—"} µg/m³</span></div>
                <div className="aq-row"><span>Ozone (O₃)</span><span>{air_quality.ozone ?? "—"} µg/m³</span></div>
                <div className="aq-row"><span>NO₂</span><span>{air_quality.nitrogen_dioxide ?? "—"} µg/m³</span></div>
                <div className="aq-row"><span>CO</span><span>{air_quality.carbon_monoxide ?? "—"} µg/m³</span></div>
                <div className="aq-row"><span>SO₂</span><span>{air_quality.sulphur_dioxide ?? "—"} µg/m³</span></div>
              </div>
            </div>
          </section>

          <section className="dashboard-card history-card">
            <h2 className="section-title">24H HISTORY</h2>
            <div className="history-grid">
              <HistoricalChart 
                title="Temperature"
                data={weatherHistory}
                dataKey="temperature_c"
                color="var(--accent-color)"
                unit="°C"
                loading={historyLoading}
                error={historyError}
                onRetry={fetchHistoryAndForecast}
              />
              <HistoricalChart 
                title="PM2.5"
                data={aqiHistory}
                dataKey="pm2_5"
                color="var(--warning)"
                unit="µg/m³"
                loading={historyLoading}
                error={historyError}
                onRetry={fetchHistoryAndForecast}
              />
            </div>
          </section>

          <section className="dashboard-card forecast-card-section">
            <Forecast 
              daily={forecast?.daily ?? []}
              hourly={forecast?.hourly ?? []}
              loading={forecastLoading}
              error={forecastError}
              onRetry={fetchHistoryAndForecast}
            />
          </section>

        </div>
      </div>
    </div>
  );
};
