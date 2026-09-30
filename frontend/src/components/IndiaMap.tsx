import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { DashboardMapData } from "../types";

type IndiaMapProps = {
  cities: DashboardMapData[];
  selectedCityId: number | null;
  onCityClick: (id: number) => void;
};

const getAqiColor = (aqi: number | null) => {
  if (aqi === null) return "#94a3b8"; // Gray for unknown
  if (aqi <= 50) return "#22c55e"; // Green = Good
  if (aqi <= 100) return "#eab308"; // Yellow = Moderate
  if (aqi <= 150) return "#f97316"; // Orange = Unhealthy for sensitive groups
  return "#ef4444"; // Red = Unhealthy / Very Unhealthy
};

export const IndiaMap: React.FC<IndiaMapProps> = ({
  cities,
  selectedCityId,
  onCityClick,
}) => {
  // Use a state to force re-render when theme changes so the CSS class applies
  const [isDark, setIsDark] = useState(() => !document.body.classList.contains("light-theme"));

  useEffect(() => {
    // Observe class changes on the body
    const observer = new MutationObserver(() => {
      setIsDark(!document.body.classList.contains("light-theme"));
    });

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

  return (
    <div
      className="india-map-container"
      style={{ height: "100%", width: "100%" }}
    >
      <MapContainer
        center={[22.5, 78.5]}
        zoom={4.5}
        scrollWheelZoom={true}
        style={{
          height: "100%",
          width: "100%",
          borderRadius: "6px",
          background: isDark ? "#111827" : "#f3f4f6",
        }}
        zoomControl={false}
      >
        <TileLayer
          key={isDark ? "dark" : "light"}
          url={tileUrl}
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          className={isDark ? "map-tiles-dark" : "map-tiles-light"}
        />

        {cities.map((city) => (
          <CircleMarker
            key={city.city_id}
            center={[city.latitude, city.longitude]}
            radius={city.city_id === selectedCityId ? 8 : 6}
            pathOptions={{
              color:
                city.city_id === selectedCityId ? "#1f2937" : "transparent",
              weight: city.city_id === selectedCityId ? 2 : 0,
              fillColor: getAqiColor(city.aqi),
              fillOpacity: 1,
            }}
            eventHandlers={{
              click: () => onCityClick(city.city_id),
            }}
          >
            <Popup className="city-map-popup">
              <strong>{city.city_name}</strong>
              <br />
              AQI: {city.aqi ?? "N/A"}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};
