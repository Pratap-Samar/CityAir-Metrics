import React, { useState, useEffect } from "react";
import { Trophy, Info } from "lucide-react";
import type { CityRanking } from "../types";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import "./Rankings.css";

const API_URL = "http://localhost:8000";

type RankingsProps = {
  onCitySelect: (id: number) => void;
};

type Period = "24h" | "7d" | "30d";

export const Rankings: React.FC<RankingsProps> = ({ onCitySelect }) => {
  const [period, setPeriod] = useState<Period>("24h");
  const [data, setData] = useState<CityRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (selectedPeriod: Period) => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(
        `${API_URL}/dashboard/rankings?metric=aqi&period=${selectedPeriod}`
      );
      if (!res.ok) {
        throw new Error("Failed to fetch rankings");
      }
      const json = await res.json();
      setData(json);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData(period);
  }, [period]);

  const getAqiDetails = (aqi: number | null) => {
    if (aqi === null) return { label: "Unknown", className: "gray", value: "-" };
    const val = Math.round(aqi);
    if (val <= 50) return { label: "Good", className: "green", value: val };
    if (val <= 100) return { label: "Moderate", className: "yellow", value: val };
    if (val <= 150) return { label: "Unhealthy for Sensitive Groups", className: "orange", value: val };
    if (val <= 200) return { label: "Unhealthy", className: "red", value: val };
    return { label: "Very Unhealthy", className: "red", value: val };
  };

  const periodLabelMap: Record<Period, string> = {
    "24h": "Today",
    "7d": "This Week",
    "30d": "This Month",
  };

  const periodLabel = periodLabelMap[period];

  // Worst cities are at the start of the array (highest AQI)
  const worstCities = data.slice(0, 5);
  
  // Best cities are at the end of the array (lowest AQI). Reverse to show absolute lowest first.
  const bestCities = data.slice().reverse().slice(0, 5);

  const renderTable = (cities: CityRanking[]) => {
    return (
      <table className="rankings-table">
        <thead>
          <tr>
            <th>#</th>
            <th>City</th>
            <th>State</th>
            <th>AQI</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {cities.map((city, idx) => {
            const { label, className, value } = getAqiDetails(city.value);
            return (
              <tr key={city.city_id} onClick={() => onCitySelect(city.city_id)}>
                <td className="rank-idx">{idx + 1}</td>
                <td className="rank-city">{city.name}</td>
                <td className="rank-state">{city.country}</td>
                <td className="rank-value">{value}</td>
                <td>
                  <span className={`aqi-badge ${className}`}>{label}</span>
                </td>
              </tr>
            );
          })}
          {cities.length === 0 && (
            <tr>
              <td colSpan={5} style={{ textAlign: "center", padding: "20px" }}>
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    );
  };

  return (
    <div className="rankings-page">
      <div className="rankings-header">
        <h1>Rankings</h1>
        <p>Air quality rankings across monitored state capitals</p>
      </div>

      <div className="rankings-tabs">
        <button
          className={`ranking-tab ${period === "24h" ? "active" : ""}`}
          onClick={() => setPeriod("24h")}
        >
          Today
        </button>
        <button
          className={`ranking-tab ${period === "7d" ? "active" : ""}`}
          onClick={() => setPeriod("7d")}
        >
          This Week
        </button>
        <button
          className={`ranking-tab ${period === "30d" ? "active" : ""}`}
          onClick={() => setPeriod("30d")}
        >
          This Month
        </button>
      </div>

      {loading && data.length === 0 ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchData(period)} />
      ) : (
        <div className="rankings-grid">
          <div className="dashboard-card ranking-card">
            <div className="ranking-card-header">
              <div className="ranking-icon-wrapper best">
                <Trophy size={24} color="#10b981" />
              </div>
              <div>
                <h2>Best Cities</h2>
                <p className="ranking-subtitle">Lowest AQI ({periodLabel})</p>
              </div>
            </div>
            {renderTable(bestCities)}
          </div>

          <div className="dashboard-card ranking-card">
            <div className="ranking-card-header">
              <div className="ranking-icon-wrapper worst">
                <Trophy size={24} color="#ef4444" />
              </div>
              <div>
                <h2>Worst Cities</h2>
                <p className="ranking-subtitle">Highest AQI ({periodLabel})</p>
              </div>
            </div>
            {renderTable(worstCities)}
          </div>
        </div>
      )}

      <div className="rankings-alert">
        <Info size={20} className="rankings-alert-icon" />
        <div>
          <p>Rankings are based on average AQI for the selected period.</p>
          <p>Lower AQI indicates better air quality.</p>
        </div>
      </div>
    </div>
  );
};
