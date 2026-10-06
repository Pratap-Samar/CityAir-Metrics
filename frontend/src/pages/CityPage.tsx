import React, { useState } from "react";
import { ArrowLeft } from "lucide-react";
import type { DashboardMapData, TimeSeriesTrend, ForecastDaily } from "../types";
import { getWeatherCondition } from "../utils/weather";
import { HistoricalChart } from "../components/HistoricalChart";

import { format } from "date-fns";
import {
  ColorfulSun,
  ColorfulCloudSun,
  ColorfulDroplet,
  ColorfulWind,
  ColorfulCloudRain,
  ColorfulAqiIcon,
  ColorfulPm25Icon,
  ColorfulPm10Icon,
  ColorfulTemperatureIcon,
} from "../components/ColorfulIcons";

type CityPageProps = {
  cityId: number | null;
  cities: DashboardMapData[];
  onBack: () => void;
};

const API_URL = "/api";

export const CityPage: React.FC<CityPageProps> = ({
  cityId,
  cities,
  onBack,
}) => {
  const city = cities.find((c) => c.city_id === cityId);

  const [aqiPeriod, setAqiPeriod] = useState<"24H" | "7D" | "30D">("24H");
  const [tempPeriod, setTempPeriod] = useState<"24H" | "7D" | "30D">("24H");

  const [aqiTrend, setAqiTrend] = useState<TimeSeriesTrend[]>([]);
  const [tempTrend, setTempTrend] = useState<TimeSeriesTrend[]>([]);

  React.useEffect(() => {
    if (!cityId) return;
    const fetchAqiTrend = async () => {
      try {
        const res = await fetch(`${API_URL}/dashboard/trends/${cityId}?metric=aqi&period=${aqiPeriod.toLowerCase()}`);
        if (res.ok) {
          const data = await res.json();
          setAqiTrend(data.trends || data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchAqiTrend();
  }, [cityId, aqiPeriod]);

  React.useEffect(() => {
    if (!cityId) return;
    const fetchTempTrend = async () => {
      try {
        const res = await fetch(`${API_URL}/dashboard/trends/${cityId}?metric=temperature&period=${tempPeriod.toLowerCase()}`);
        if (res.ok) {
          const data = await res.json();
          setTempTrend(data.trends || data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchTempTrend();
  }, [cityId, tempPeriod]);

  const [forecastLoading, setForecastLoading] = useState(true);
  const [forecastError, setForecastError] = useState<string | null>(null);
  const [forecastDaily, setForecastDaily] = useState<ForecastDaily[]>([]);

  React.useEffect(() => {
    if (!cityId) return;

    const fetchForecast = async () => {
      // reset state when city changes
      setForecastLoading(true);
      setForecastError(null);
      setForecastDaily([]);
      try {
        const res = await fetch(`${API_URL}/weather/forecast/${cityId}`);
        if (!res.ok) throw new Error("Failed to fetch forecast");
        const data = await res.json();
        setForecastDaily(data.daily || []);
      } catch (err) {
        setForecastError(err instanceof Error ? err.message : "Error fetching forecast");
      } finally {
        setForecastLoading(false);
      }
    };
    fetchForecast();
  }, [cityId]);



  if (!city) {
    return (
      <div
        className="city-page-container"
        style={{ padding: "24px", color: "var(--muted-text)" }}
      >
        <p>City not found.</p>
        <button
          onClick={onBack}
          className="scp-btn"
          style={{ width: "fit-content", marginTop: "16px" }}
        >
          <ArrowLeft size={16} /> Back to Dashboard
        </button>
      </div>
    );
  }

  const weatherCode = city.temperature_c !== null ? 0 : null; // mocked
  const conditionText = getWeatherCondition(weatherCode);
  const WeatherIcon = weatherCode === 0 ? ColorfulSun : ColorfulCloudSun;

  let aqiLabel = "Unknown";
  let aqiClass = "gray";
  if (city.aqi !== null) {
    if (city.aqi <= 50) {
      aqiLabel = "Good";
      aqiClass = "green";
    } else if (city.aqi <= 100) {
      aqiLabel = "Moderate";
      aqiClass = "yellow";
    } else if (city.aqi <= 150) {
      aqiLabel = "Unhealthy for Sensitive Groups";
      aqiClass = "orange";
    } else if (city.aqi <= 200) {
      aqiLabel = "Unhealthy";
      aqiClass = "red";
    } else {
      aqiLabel = "Very Unhealthy";
      aqiClass = "red";
    }
  }

  const lastUpdated = city.air_quality_observed_at
    ? new Date(city.air_quality_observed_at).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      })
    : "Unknown";

  return (
    <div className="city-page-container">
      {/* Header Area */}
      <div className="cp-header">
        <button onClick={onBack} className="cp-back-btn">
          <ArrowLeft size={16} /> Back to Dashboard
        </button>
        <div className="cp-last-updated" style={{ textAlign: "right" }}>
          <span style={{ color: "var(--muted-text)" }}>Latest observation:</span><br />
          <span style={{ color: "var(--foreground)" }}>{lastUpdated}</span>
        </div>
      </div>

      {/* City Title */}
      <div className="cp-title-section">
        <h1 className="cp-city-name">{city.city_name}</h1>
        <p className="cp-city-country">{city.state}</p>
      </div>

      {/* Row 1: AQI Metrics */}
      <div className="cp-row-1">
        <div className="dashboard-card cp-aqi-card">
          <div className="cp-icon-circle cp-aqi-icon">
            <ColorfulAqiIcon size={30} />
          </div>
          <div className="cp-metric-info">
            <div className="cp-metric-label">AQI</div>
            <div className="cp-metric-val">
              <span className="huge">
                {city.aqi !== null ? Math.round(city.aqi) : "-"}
              </span>
            </div>
            <div className="cp-metric-badge">
              <span className={`aqi-badge ${aqiClass}`}>{aqiLabel}</span>
            </div>
          </div>
        </div>

        <div className="dashboard-card cp-aqi-card">
          <div className="cp-icon-circle cp-pm25-icon">
            <ColorfulPm25Icon size={30} />
          </div>
          <div className="cp-metric-info">
            <div className="cp-metric-label">PM2.5</div>
            <div className="cp-metric-val">
              <span className="huge">
                {city.pm2_5 !== null ? Math.round(city.pm2_5) : "-"}
              </span>
              <span className="unit-text">µg/m³</span>
            </div>
          </div>
        </div>

        <div className="dashboard-card cp-aqi-card">
          <div className="cp-icon-circle cp-pm10-icon">
            <ColorfulPm10Icon size={30} />
          </div>
          <div className="cp-metric-info">
            <div className="cp-metric-label">PM10</div>
            <div className="cp-metric-val">
              <span className="huge">
                {city.pm10 !== null ? Math.round(city.pm10) : "-"}
              </span>
              <span className="unit-text">µg/m³</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Weather & Forecast */}
      <div className="cp-row-2">
        <div className="dashboard-card cp-weather-card">
          <h3 className="section-title">Current Weather</h3>
          <div
            className="cp-weather-main"
            style={{ display: "flex", gap: "24px", alignItems: "center" }}
          >
            <WeatherIcon size={80} className="scp-weather-icon" />

            <div style={{ display: "flex", alignItems: "center", gap: "18px" }}>
              <div className="cp-icon-circle cp-temp-icon">
                <ColorfulTemperatureIcon size={30} />
              </div>
              <div className="cp-metric-info">
                <div className="cp-metric-label">Temperature</div>
                <div className="cp-metric-val">
                  <span className="huge">
                    {city.temperature_c !== null
                      ? Math.round(city.temperature_c)
                      : "-"}
                  </span>
                  <span className="unit-text">°C</span>
                </div>
                <div
                  className="scp-cond-val"
                  style={{
                    marginTop: "4px",
                    color: "var(--muted-text)",
                    fontWeight: 500,
                  }}
                >
                  {conditionText}
                </div>
              </div>
            </div>
          </div>

          <div className="scp-divider"></div>

          <div className="cp-weather-features-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div className="scp-feature" style={{ flex: 1, minWidth: 0, justifyContent: "center" }}>
              <ColorfulDroplet size={20} className="scp-feature-icon" />
              <div className="scp-feature-text">
                <div className="scp-feature-label">Humidity</div>
                <div className="scp-feature-val">
                  {city.humidity_percent !== null
                    ? `${Math.round(city.humidity_percent)}%`
                    : "-"}
                </div>
              </div>
            </div>
            <div className="cp-feature-separator" style={{ width: "1px", height: "30px", backgroundColor: "var(--border-color)" }}></div>
            <div className="scp-feature" style={{ flex: 1, minWidth: 0, justifyContent: "center", paddingLeft: "8px" }}>
              <ColorfulWind size={20} className="scp-feature-icon" />
              <div className="scp-feature-text">
                <div className="scp-feature-label">Wind</div>
                <div className="scp-feature-val">
                  {city.wind_speed_kmh !== null
                    ? `${Math.round(city.wind_speed_kmh)} km/h`
                    : "-"}
                </div>
              </div>
            </div>
            <div className="cp-feature-separator" style={{ width: "1px", height: "30px", backgroundColor: "var(--border-color)" }}></div>
            <div className="scp-feature" style={{ flex: 1, minWidth: 0, justifyContent: "center", paddingLeft: "8px" }}>
              <ColorfulCloudRain size={20} className="scp-feature-icon" />
              <div className="scp-feature-text">
                <div className="scp-feature-label" style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>Precipitation</div>
                <div className="scp-feature-val">
                  {city.precipitation_mm !== null
                    ? `${city.precipitation_mm} mm`
                    : "-"}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-card cp-forecast-card">
          <h3 className="section-title">Forecast (Next 5 Days)</h3>
          {forecastLoading ? (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "150px", color: "var(--muted-text)" }}>
              Loading forecast...
            </div>
          ) : forecastError ? (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "150px", color: "var(--red-color, #c5240e)" }}>
              {forecastError}
            </div>
          ) : forecastDaily.length === 0 ? (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "150px", color: "var(--muted-text)" }}>
              No forecast available
            </div>
          ) : (
            <div className="cp-forecast-grid">
              {forecastDaily.slice(0, 5).map((day, i) => {
                const dayDate = new Date(day.time);
                const condition = getWeatherCondition(day.weather_code);
                
                let DayIcon = ColorfulCloudSun;
                if (day.weather_code === 0) DayIcon = ColorfulSun;
                else if (day.weather_code !== null && (day.weather_code >= 51 && day.weather_code <= 99)) DayIcon = ColorfulCloudRain;
                
                return (
                  <div key={i} className="cp-forecast-day">
                    <div className="fd-day-name">{format(dayDate, "EEE")}</div>
                    <div className="fd-date">{format(dayDate, "MMM d")}</div>
                    <div className="fd-icon-wrapper">
                      <DayIcon size={40} />
                    </div>
                    <div className="fd-max">{day.temperature_2m_max !== null ? Math.round(day.temperature_2m_max) : "-"}&deg;C</div>
                    <div className="fd-min">{day.temperature_2m_min !== null ? Math.round(day.temperature_2m_min) : "-"}&deg;C</div>
                    <div className="fd-cond">{condition}</div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Row 3: Trends */}
      <div className="cp-row-3">
        <div className="dashboard-card trend-card">
          <div className="trend-header">
            <div className="trend-title">
              AQI Trend &mdash; {city.city_name}
            </div>
            <div className="trend-toggles">
              <button
                className={`trend-toggle ${aqiPeriod === "24H" ? "active" : ""}`}
                onClick={() => setAqiPeriod("24H")}
              >
                24H
              </button>
              <button
                className={`trend-toggle ${aqiPeriod === "7D" ? "active" : ""}`}
                onClick={() => setAqiPeriod("7D")}
              >
                7D
              </button>
              <button
                className={`trend-toggle ${aqiPeriod === "30D" ? "active" : ""}`}
                onClick={() => setAqiPeriod("30D")}
              >
                30D
              </button>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, height: "calc(100% - 32px)" }}>
            <HistoricalChart
              data={aqiTrend}
              dataKey="value"
              color="#3d6cd1"
              unit="AQI"
              loading={false}
              error={null}
              onRetry={() => {}}
            />
          </div>
        </div>

        <div className="dashboard-card trend-card">
          <div className="trend-header">
            <div className="trend-title">
              Temperature Trend &mdash; {city.city_name}
            </div>
            <div className="trend-toggles">
              <button
                className={`trend-toggle ${tempPeriod === "24H" ? "active" : ""}`}
                onClick={() => setTempPeriod("24H")}
              >
                24H
              </button>
              <button
                className={`trend-toggle ${tempPeriod === "7D" ? "active" : ""}`}
                onClick={() => setTempPeriod("7D")}
              >
                7D
              </button>
              <button
                className={`trend-toggle ${tempPeriod === "30D" ? "active" : ""}`}
                onClick={() => setTempPeriod("30D")}
              >
                30D
              </button>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, height: "calc(100% - 32px)" }}>
            <HistoricalChart
              data={tempTrend}
              dataKey="value"
              color="#c5240e"
              unit="°C"
              loading={false}
              error={null}
              onRetry={() => {}}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
