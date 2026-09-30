import React, { useState, useEffect } from "react";
import { MapContainer, GeoJSON, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { DashboardMapData } from "../types";

type IndiaMapProps = {
  cities: DashboardMapData[];
  selectedCityId: number | null;
  onCityClick: (id: number) => void;
};

const getAqiColor = (aqi: number | null) => {
  if (aqi === null) return "#94a3b8";
  if (aqi <= 50) return "#22c55e";
  if (aqi <= 100) return "#eab308";
  if (aqi <= 150) return "#f97316";
  return "#ef4444";
};

export const IndiaMap: React.FC<IndiaMapProps> = ({
  cities,
  selectedCityId,
  onCityClick,
}) => {
  const [geoData, setGeoData] = useState<any>(null);
  const [isDark, setIsDark] = useState(() => !document.body.classList.contains("light-theme"));

  useEffect(() => {
    fetch("/india-map-simple.json")
      .then((res) => res.json())
      .then((data) => {
        setGeoData(data);
      })
      .catch((err) => console.error("Error loading GeoJSON:", err));

    const observer = new MutationObserver(() => {
      setIsDark(!document.body.classList.contains("light-theme"));
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

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
          background: "transparent",
        }}
        zoomControl={false}
      >
        {geoData && (
          <GeoJSON
            key={isDark ? "dark" : "light"}
            data={geoData}
            style={() => ({
              color: isDark ? "#4b5563" : "#d1d5db", // border color
              weight: 1,
              fillColor: isDark ? "#1f2937" : "#e5e7eb", // fill color
              fillOpacity: 0.4,
            })}
          />
        )}

        {cities.map((city) => (
          <CircleMarker
            key={city.city_id}
            center={[city.latitude, city.longitude]}
            radius={city.city_id === selectedCityId ? 8 : 6}
            pathOptions={{
              color: city.city_id === selectedCityId ? "#ffffff" : "transparent",
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
