import React, { useMemo } from "react";
import type { DashboardMapData, DashboardSummary } from "../types";
import { IndiaMap } from "../components/IndiaMap";
import { SelectedCityPanel } from "../components/SelectedCityPanel";
import { HistoricalChart } from "../components/HistoricalChart";
import { BarChart2, Thermometer, Building2 } from "lucide-react";
import { getMockIndiaAqiTrend, getMockIndiaTempTrend, getMockRecentPipelineRuns } from "../api/mockAdapter";

type DashboardProps = {
  cities: DashboardMapData[];
  summary: DashboardSummary | null;
  selectedCityId: number | null;
  onCityChange: (id: number) => void;
};

export const Dashboard: React.FC<DashboardProps> = ({
  cities,
  summary,
  selectedCityId,
  onCityChange,
}) => {
  const selectedCity = cities.find((c) => c.city_id === selectedCityId);

  const [aqiPeriod, setAqiPeriod] = React.useState<"24H" | "7D" | "30D">("24H");
  const [tempPeriod, setTempPeriod] = React.useState<"24H" | "7D" | "30D">("24H");

  const aqiTrend = useMemo(() => getMockIndiaAqiTrend(aqiPeriod), [aqiPeriod]);
  const tempTrend = useMemo(() => getMockIndiaTempTrend(tempPeriod), [tempPeriod]);
  const pipelineRuns = useMemo(() => getMockRecentPipelineRuns(), []);

  return (
    <div className="dashboard-page">
      {/* SECTION 1: Summary Cards */}
      <section className="dashboard-row-1">
        <div className="dashboard-card summary-card">
          <div className="sc-icon-circle"><BarChart2 size={24} /></div>
          <div className="sc-content">
            <div className="sc-title">AVG AQI (India)</div>
            <div className="sc-value">
              {summary?.average_aqi !== null && summary?.average_aqi !== undefined ? Math.round(summary.average_aqi) : "-"}
            </div>
            <div className="sc-subtitle">Moderate (All state capitals)</div>
          </div>
        </div>

        <div className="dashboard-card summary-card">
          <div className="sc-icon-circle"><Thermometer size={24} /></div>
          <div className="sc-content">
            <div className="sc-title">AVG TEMPERATURE (India)</div>
            <div className="sc-value">
              {summary?.average_temperature_c !== null && summary?.average_temperature_c !== undefined ? `${Math.round(summary.average_temperature_c)}°C` : "-"}
            </div>
            <div className="sc-subtitle">(All state capitals)</div>
          </div>
        </div>

        <div className="dashboard-card summary-card">
          <div className="sc-icon-circle"><Building2 size={24} /></div>
          <div className="sc-content">
            <div className="sc-title">CITIES MONITORED</div>
            <div className="sc-value">
              {summary?.total_cities ?? "-"}
            </div>
            <div className="sc-subtitle">State capitals</div>
          </div>
        </div>
      </section>

      {/* SECTION 2: Map + Selected City */}
      <section className="dashboard-row-2">
        <div className="dashboard-card map-card">
          <h3 className="map-card-title">Air Quality Across State Capitals</h3>
          <div className="map-legend-simple">
            <div className="legend-item"><div className="dot" style={{ backgroundColor: "#22c55e" }} /> Good</div>
            <div className="legend-item"><div className="dot" style={{ backgroundColor: "#facc15" }} /> Moderate</div>
            <div className="legend-item"><div className="dot" style={{ backgroundColor: "#f97316" }} /> Unhealthy</div>
            <div className="legend-item"><div className="dot" style={{ backgroundColor: "#ef4444" }} /> Very Unhealthy</div>
          </div>
          <div className="map-container-inner">
            <IndiaMap 
              cities={cities} 
              selectedCityId={selectedCityId} 
              onCityClick={onCityChange} 
            />
          </div>
        </div>
        
        <div className="city-panel-container">
          {selectedCity ? (
            <SelectedCityPanel city={selectedCity} />
          ) : (
            <div className="dashboard-card city-panel-card" style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
              <p>Select a city on the map to view details.</p>
            </div>
          )}
        </div>
      </section>

      {/* SECTION 3: Bottom Row */}
      <section className="dashboard-row-3">
        <div className="dashboard-card trend-card">
          <div className="trend-header">
            <div className="trend-title">AQI Trend &mdash; India (All State Capitals)</div>
            <div className="trend-toggles">
              <button className={`trend-toggle ${aqiPeriod === "24H" ? "active" : ""}`} onClick={() => setAqiPeriod("24H")}>24H</button>
              <button className={`trend-toggle ${aqiPeriod === "7D" ? "active" : ""}`} onClick={() => setAqiPeriod("7D")}>7D</button>
              <button className={`trend-toggle ${aqiPeriod === "30D" ? "active" : ""}`} onClick={() => setAqiPeriod("30D")}>30D</button>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, height: "calc(100% - 32px)" }}>
            <HistoricalChart 
              title=""
              data={aqiTrend}
              dataKey="value"
              color="#6b7280" 
              unit="AQI"
              loading={false}
              error={null}
              onRetry={() => {}}
            />
          </div>
        </div>

        <div className="dashboard-card trend-card">
          <div className="trend-header">
            <div className="trend-title">Temperature Trend &mdash; India (All State Capitals)</div>
            <div className="trend-toggles">
              <button className={`trend-toggle ${tempPeriod === "24H" ? "active" : ""}`} onClick={() => setTempPeriod("24H")}>24H</button>
              <button className={`trend-toggle ${tempPeriod === "7D" ? "active" : ""}`} onClick={() => setTempPeriod("7D")}>7D</button>
              <button className={`trend-toggle ${tempPeriod === "30D" ? "active" : ""}`} onClick={() => setTempPeriod("30D")}>30D</button>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, height: "calc(100% - 32px)" }}>
            <HistoricalChart 
              title=""
              data={tempTrend}
              dataKey="value"
              color="#6b7280"
              unit="°C"
              loading={false}
              error={null}
              onRetry={() => {}}
            />
          </div>
        </div>

        <div className="dashboard-card pipeline-card">
          <div className="trend-header">
            <div className="trend-title">Recent Pipeline Runs</div>
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            <table className="pipeline-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Pipeline</th>
                  <th>Status</th>
                  <th>Records</th>
                </tr>
              </thead>
              <tbody>
                {pipelineRuns.map(run => (
                  <tr key={run.id}>
                    <td>{new Date(run.time).toLocaleTimeString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false })}</td>
                    <td>{run.type}</td>
                    <td>
                      <span className="status-pill">{run.status}</span>
                    </td>
                    <td>28</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
};
