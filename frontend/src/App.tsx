import { useEffect, useState } from "react";
import "./App.css";

type AnalyticsCity = {
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

const API_URL = "http://localhost:8000";

function App() {
  const [cities, setCities] = useState<AnalyticsCity[]>([]);
  const [selectedCityId, setSelectedCityId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/analytics`);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data: AnalyticsCity[] = await response.json();

      setCities(data);

      if (data.length > 0) {
        setSelectedCityId((currentId) => currentId ?? data[0].city_id);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load dashboard data.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const selectedCity =
    cities.find((city) => city.city_id === selectedCityId) ?? null;

  if (loading) {
    return (
      <main className="dashboard">
        <h1>CityAir Metrics</h1>
        <p>Loading city data...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="dashboard">
        <h1>CityAir Metrics</h1>
        <p className="error-message">{error}</p>
        <button
          type="button"
          className="refresh-button"
          onClick={fetchAnalytics}
        >
          Try again
        </button>
      </main>
    );
  }

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">DATA ENGINEERING PROJECT</p>
          <h1>CityAir Metrics</h1>
          <p className="subtitle">
            Weather and air-quality monitoring across cities.
          </p>
        </div>

        <button
          type="button"
          className="refresh-button"
          onClick={fetchAnalytics}
        >
          Refresh data
        </button>
      </header>

      <section className="controls">
        <label htmlFor="city-select">City</label>

        <select
          id="city-select"
          value={selectedCityId ?? ""}
          onChange={(event) => setSelectedCityId(Number(event.target.value))}
        >
          {cities.map((city) => (
            <option key={city.city_id} value={city.city_id}>
              {city.name}, {city.country}
            </option>
          ))}
        </select>
      </section>

      {selectedCity && (
        <>
          <section className="metrics-grid">
            <article className="metric-card">
              <p>Temperature</p>
              <strong>{selectedCity.weather.temperature_c ?? "—"}°C</strong>
              <span>Current temperature</span>
            </article>

            <article className="metric-card">
              <p>PM2.5</p>
              <strong>{selectedCity.air_quality.pm2_5 ?? "—"} µg/m³</strong>
              <span>Current concentration</span>
            </article>

            <article className="metric-card">
              <p>US AQI</p>
              <strong>{selectedCity.air_quality.us_aqi ?? "—"}</strong>
              <span>Current air quality index</span>
            </article>
          </section>

          <section className="panel">
            <div className="panel-header">
              <p className="eyebrow">CITY DETAILS</p>
              <h2>
                {selectedCity.name}, {selectedCity.country}
              </h2>
            </div>

            <div className="city-table">
              <div className="table-row table-header">
                <span>Metric</span>
                <span>Value</span>
                <span>Metric</span>
                <span>Value</span>
              </div>

              <div className="table-row">
                <strong>Humidity</strong>
                <span>{selectedCity.weather.humidity_percent ?? "—"}%</span>

                <strong>PM10</strong>
                <span>{selectedCity.air_quality.pm10 ?? "—"} µg/m³</span>
              </div>

              <div className="table-row">
                <strong>Wind speed</strong>
                <span>{selectedCity.weather.wind_speed_kmh ?? "—"} km/h</span>

                <strong>Ozone</strong>
                <span>{selectedCity.air_quality.ozone ?? "—"} µg/m³</span>
              </div>

              <div className="table-row">
                <strong>Precipitation</strong>
                <span>{selectedCity.weather.precipitation_mm ?? "—"} mm</span>

                <strong>NO₂</strong>
                <span>
                  {selectedCity.air_quality.nitrogen_dioxide ?? "—"} µg/m³
                </span>
              </div>
            </div>
          </section>

          <section className="charts-grid">
            <article className="panel chart-placeholder">
              <p className="eyebrow">TEMPERATURE TREND</p>
              <h2>Temperature over time</h2>

              <div className="placeholder">
                Historical chart will be added next.
              </div>
            </article>

            <article className="panel chart-placeholder">
              <p className="eyebrow">AIR QUALITY TREND</p>
              <h2>PM2.5 over time</h2>

              <div className="placeholder">
                Historical chart will be added next.
              </div>
            </article>
          </section>
        </>
      )}
    </main>
  );
}

export default App;
