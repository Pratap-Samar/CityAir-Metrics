import React from "react";
import type { DashboardMapData } from "../types";
import { getWeatherCondition, getWeatherIconComponent } from "../utils/weather";
import { MapPin, Droplet, Wind, CloudRain, ArrowRight } from "lucide-react";

type SelectedCityPanelProps = {
  city: DashboardMapData;
};

export const SelectedCityPanel: React.FC<SelectedCityPanelProps> = ({ city }) => {
  const weatherCode = city.temperature_c !== null ? 1 : null;
  const conditionText = getWeatherCondition(weatherCode);
  const WeatherIcon = getWeatherIconComponent(weatherCode);

  let aqiLabel = "Unknown";
  let aqiClass = "gray";
  if (city.aqi !== null) {
    if (city.aqi <= 50) { aqiLabel = "Good"; aqiClass = "green"; }
    else if (city.aqi <= 100) { aqiLabel = "Moderate"; aqiClass = "yellow"; }
    else if (city.aqi <= 150) { aqiLabel = "Unhealthy for Sensitive Groups"; aqiClass = "orange"; }
    else if (city.aqi <= 200) { aqiLabel = "Unhealthy"; aqiClass = "red"; }
    else { aqiLabel = "Very Unhealthy"; aqiClass = "red"; }
  }

  return (
    <div className="dashboard-card city-panel-card" style={{ height: "100%" }}>
      <div className="scp-top">
        <div>
          <h2 className="scp-city-name">{city.city_name}</h2>
          <p className="scp-city-sub">{city.country}</p>
        </div>
        <div className="scp-badge">
          <MapPin size={12} /> Selected via map
        </div>
      </div>

      <div className="scp-weather-main">
        {/* eslint-disable-next-line react-hooks/static-components */}
        <WeatherIcon size={72} className="scp-weather-icon" />
        <div>
          <div className="scp-temp-val">{city.temperature_c !== null ? Math.round(city.temperature_c) : "-"}&deg;C</div>
          <div className="scp-cond-val">{conditionText}</div>
        </div>
      </div>

      <div className="scp-divider"></div>

      <div className="scp-grid-3">
        <div className="scp-feature">
          <Droplet size={24} className="scp-feature-icon" />
          <div className="scp-feature-text">
            <div className="scp-feature-label">Humidity</div>
            <div className="scp-feature-val">
              {city.humidity_percent !== null ? `${Math.round(city.humidity_percent)}%` : "-"}
            </div>
          </div>
        </div>
        <div className="scp-feature">
          <Wind size={24} className="scp-feature-icon" />
          <div className="scp-feature-text">
            <div className="scp-feature-label">Wind</div>
            <div className="scp-feature-val">
              {city.wind_speed_kmh !== null ? `${Math.round(city.wind_speed_kmh)} km/h` : "-"}
            </div>
          </div>
        </div>
        <div className="scp-feature">
          <CloudRain size={24} className="scp-feature-icon" />
          <div className="scp-feature-text">
            <div className="scp-feature-label">Precipitation</div>
            <div className="scp-feature-val">
              {city.precipitation_mm !== null ? `${city.precipitation_mm} mm` : "-"}
            </div>
          </div>
        </div>
      </div>

      <div className="scp-divider"></div>

      <div className="scp-grid-3">
        <div className="scp-feature-text">
          <div className="scp-feature-label">AQI</div>
          <div className="aqi-val-row" style={{ marginTop: "4px" }}>
            <span className="huge">{city.aqi !== null ? Math.round(city.aqi) : "-"}</span>
            <span className={`aqi-badge ${aqiClass}`}>{aqiLabel}</span>
          </div>
        </div>
        <div className="scp-feature-text">
          <div className="scp-feature-label">PM2.5</div>
          <div className="aqi-val-row" style={{ marginTop: "4px" }}>
            <span className="huge">{city.pm2_5 !== null ? Math.round(city.pm2_5) : "-"}</span> 
            <span className="unit-text">&micro;g/m&sup3;</span>
          </div>
        </div>
        <div className="scp-feature-text">
          <div className="scp-feature-label">PM10</div>
          <div className="aqi-val-row" style={{ marginTop: "4px" }}>
            <span className="huge">{city.pm10 !== null ? Math.round(city.pm10) : "-"}</span> 
            <span className="unit-text">&micro;g/m&sup3;</span>
          </div>
        </div>
      </div>

      <button className="scp-btn">
        View Full Report <ArrowRight size={16} />
      </button>
    </div>
  );
};
