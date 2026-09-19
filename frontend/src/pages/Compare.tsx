import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import type { DashboardMapData } from "../types";
import "./Compare.css";
import { 
  Wind, Droplets, Thermometer, CloudRain, Activity, 
  X, Info, BarChart2, CheckCircle2
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList
} from "recharts";

type CompareProps = {
  cities: DashboardMapData[];
};

const CITY_COLORS = ["#ef4444", "#22c55e", "#3b82f6", "#f59e0b"];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ backgroundColor: "#1f2937", padding: "8px 12px", borderRadius: "6px", color: "#fff", fontSize: "0.85rem" }}>
        <p style={{ margin: 0, fontWeight: "bold" }}>{label}</p>
        <p style={{ margin: 0 }}>{`${payload[0].value}`}</p>
      </div>
    );
  }
  return null;
};

export const Compare: React.FC<CompareProps> = ({ cities }) => {
  const [selectedCityIds, setSelectedCityIds] = useState<number[]>([]);
  const [showAddDropdown, setShowAddDropdown] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowAddDropdown(false);
        setSearchQuery("");
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleAddCity = (id: number) => {
    if (selectedCityIds.length < 4 && !selectedCityIds.includes(id)) {
      setSelectedCityIds([...selectedCityIds, id]);
    }
    setShowAddDropdown(false);
    setSearchQuery("");
  };

  const handleRemoveCity = (id: number) => {
    setSelectedCityIds(selectedCityIds.filter(c => c !== id));
  };

  const selectedCitiesData = selectedCityIds
    .map(id => cities.find(c => c.city_id === id))
    .filter((c): c is DashboardMapData => c !== undefined);

  const availableCities = cities
    .filter(c => !selectedCityIds.includes(c.city_id))
    .filter(c => c.city_name.toLowerCase().includes(searchQuery.toLowerCase()) || c.state.toLowerCase().includes(searchQuery.toLowerCase()));

  const getAqiStatus = (aqi: number | null) => {
    if (aqi === null) return { label: "Unknown", class: "gray" };
    if (aqi <= 50) return { label: "Good", class: "green" };
    if (aqi <= 100) return { label: "Moderate", class: "yellow" };
    if (aqi <= 150) return { label: "Unhealthy for Sensitive Groups", class: "orange" };
    if (aqi <= 200) return { label: "Unhealthy", class: "red" };
    return { label: "Very Unhealthy", class: "red" };
  };

  // Helper to determine best/worst stat
  const getBestWorstClass = (cityId: number, metric: keyof DashboardMapData, lowerIsBetter = true) => {
    const validCities = selectedCitiesData.filter(c => c[metric] !== null);
    if (validCities.length < 2) return "";
    
    const values = validCities.map(c => c[metric] as number);
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    if (min === max) return "";
    
    const cityVal = selectedCitiesData.find(c => c.city_id === cityId)?.[metric];
    if (cityVal === null || cityVal === undefined) return "";
    
    if (lowerIsBetter) {
      if (cityVal === min) return "stat-best";
      if (cityVal === max) return "stat-worst";
    }
    return "";
  };

  const chartData = selectedCitiesData.map((c, i) => ({
    name: c.city_name,
    aqi: c.aqi !== null ? Math.round(c.aqi) : 0,
    temp: c.temperature_c !== null ? Math.round(c.temperature_c) : 0,
    fill: CITY_COLORS[i]
  }));

  return (
    <div className="compare-page-wrapper">
      <div className="compare-page-header">
        <h1>Compare Cities</h1>
        <p>Compare environmental conditions across up to four cities</p>
      </div>

      <div className="compare-city-bar">
        {selectedCitiesData.map((city, idx) => (
          <div key={city.city_id} className="city-chip">
            <div className="chip-left">
              <div className="chip-dot" style={{ backgroundColor: CITY_COLORS[idx] }}></div>
              <div 
                className="chip-info" 
                style={{ cursor: "pointer" }} 
                onClick={() => navigate(`/city/${encodeURIComponent(city.city_name)}`)}
              >
                <div className="chip-name">{city.city_name}</div>
                <div className="chip-state">{city.state}</div>
              </div>
            </div>
            <button className="chip-close" onClick={() => handleRemoveCity(city.city_id)}>
              <X size={18} />
            </button>
          </div>
        ))}

        {selectedCityIds.length < 4 && (
          <div className="add-city-wrapper" ref={dropdownRef}>
            <button className="add-city-btn" onClick={() => setShowAddDropdown(!showAddDropdown)}>
              + Add City
              <span>(Max 4 cities)</span>
            </button>
            {showAddDropdown && (
              <div className="add-city-dropdown">
                <div className="add-city-search">
                  <input 
                    type="text" 
                    placeholder="Search city..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="add-city-options">
                  {availableCities.length > 0 ? (
                    availableCities.map(city => (
                      <div 
                        key={city.city_id} 
                        className="add-city-dropdown-item"
                        onClick={() => handleAddCity(city.city_id)}
                      >
                        <strong>{city.city_name}</strong>
                        <span>{city.state}</span>
                      </div>
                    ))
                  ) : (
                    <div className="add-city-dropdown-item">No matches found</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {selectedCitiesData.length > 0 && (
        <>
          <div className="compare-table-card">
            <div className="compare-table-header">
              <h3>Current Conditions</h3>
              <p>Latest available data for selected cities</p>
            </div>
            
            <div className="compare-table">
              <div className="compare-tr compare-th">
                <div className="compare-td"></div>
                {selectedCitiesData.map((city, idx) => (
                  <div key={city.city_id} className="compare-td center" style={{ flexDirection: "column" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div className="chip-dot" style={{ backgroundColor: CITY_COLORS[idx] }}></div>
                      <div className="chip-name" style={{ cursor: "pointer" }} onClick={() => navigate(`/city/${encodeURIComponent(city.city_name)}`)}>
                        {city.city_name}
                      </div>
                    </div>
                    <div className="chip-state" style={{ marginLeft: "22px" }}>{city.state}</div>
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><BarChart2 size={16}/> AQI</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className={`compare-td center ${getBestWorstClass(c.city_id, 'aqi')}`}>
                    {c.aqi !== null ? Math.round(c.aqi) : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><Activity size={16}/> PM2.5</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className={`compare-td center ${getBestWorstClass(c.city_id, 'pm2_5')}`}>
                    {c.pm2_5 !== null ? `${Math.round(c.pm2_5)} µg/m³` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><Activity size={16}/> PM10</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className={`compare-td center ${getBestWorstClass(c.city_id, 'pm10')}`}>
                    {c.pm10 !== null ? `${Math.round(c.pm10)} µg/m³` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><Thermometer size={16}/> Temperature</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className="compare-td center">
                    {c.temperature_c !== null ? `${Math.round(c.temperature_c)}°C` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><Droplets size={16}/> Humidity</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className="compare-td center">
                    {c.humidity_percent !== null ? `${Math.round(c.humidity_percent)}%` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><Wind size={16}/> Wind</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className="compare-td center">
                    {c.wind_speed_kmh !== null ? `${Math.round(c.wind_speed_kmh)} km/h` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><CloudRain size={16}/> Precipitation</div>
                {selectedCitiesData.map(c => (
                  <div key={c.city_id} className="compare-td center">
                    {c.precipitation_mm !== null ? `${c.precipitation_mm} mm` : "-"}
                  </div>
                ))}
              </div>

              <div className="compare-tr">
                <div className="compare-td"><CheckCircle2 size={16}/> Status</div>
                {selectedCitiesData.map(c => {
                  const status = getAqiStatus(c.aqi);
                  return (
                    <div key={c.city_id} className="compare-td center">
                      <span className={`aqi-badge-compare ${status.class}`}>{status.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="compare-charts-grid">
            <div className="compare-chart-box">
              <h3>AQI Comparison</h3>
              <p>Current AQI across selected cities</p>
              <div className="compare-chart-inner">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} stroke="#9ca3af" fontSize={12} dy={10} />
                    <YAxis axisLine={false} tickLine={false} stroke="#9ca3af" fontSize={12} dx={-10} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: "transparent" }} />
                    <Bar dataKey="aqi" radius={[4, 4, 0, 0]} maxBarSize={60}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                      <LabelList dataKey="aqi" position="top" fill="var(--text-color)" fontWeight={600} fontSize={12} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="compare-chart-box">
              <h3>Temperature Comparison</h3>
              <p>Current temperature across selected cities</p>
              <div className="compare-chart-inner">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} stroke="#9ca3af" fontSize={12} dy={10} />
                    <YAxis axisLine={false} tickLine={false} stroke="#9ca3af" fontSize={12} dx={-10} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: "transparent" }} />
                    <Bar dataKey="temp" radius={[4, 4, 0, 0]} maxBarSize={60}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                      <LabelList dataKey="temp" position="top" fill="var(--text-color)" fontWeight={600} fontSize={12} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="compare-footer-info">
        <Info size={20} color="#3b82f6" />
        <div>
          Showing latest available data for the selected cities.<br/>
          Click on a city name to view the full city report.
        </div>
      </div>
    </div>
  );
};
