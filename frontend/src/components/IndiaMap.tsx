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
  const [isDark, setIsDark] = useState(() =>
    document.documentElement.classList.contains("dark"),
  );
  const [geoData, setGeoData] = useState<any>(null);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains("dark"));
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    // Fetch the perfect WGS84 GeoJSON that unifies PoK and Aksai Chin natively
    fetch('/india-perfect-wgs84.json')
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => console.error("Failed to load state boundaries", err));

    return () => observer.disconnect();
  }, []);

  // Define strict bounding box for India to prevent panning away
  const indiaBounds: import("leaflet").LatLngBoundsExpression = [
    [5.0, 65.0], // South-West corner
    [39.0, 100.0] // North-East corner
  ];

  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div
      className="india-map-container"
      style={{ height: "100%", width: "100%" }}
    >
      <MapContainer
        center={isMobile ? [23.5, 82.0] : [22.5, 78.5]}
        zoom={isMobile ? 3.8 : 4.5}
        minZoom={3.5} // Allow zooming out more on mobile
        zoomSnap={0.1} // Enable fractional zoom snapping for perfect fit
        maxBounds={indiaBounds}
        maxBoundsViscosity={1.0}
        scrollWheelZoom={true}
        style={{
          height: "100%",
          width: "100%",
          borderRadius: "6px",
          background: "transparent", // Use transparent so the parent card color comes through
        }}
        zoomControl={false}
      >
        {/* Render GeoJSON FIRST, then CircleMarkers so markers stay on top */}
        {geoData && (
          <>
            <GeoJSON
              key={`bounds-${isDark ? "dark" : "light"}`}
              data={geoData}
              style={{
                color: isDark ? "#4b5563" : "#6b7280", // Crisp state borders
                weight: 1,
                fillColor: isDark ? "#1f2937" : "#d1d5db", // Solid state fill
                fillOpacity: 1,
                interactive: false // MUST NOT intercept clicks for markers
              }}
            />
            {cities.map((city) => (
              <CircleMarker
                key={city.city_id}
                center={[city.latitude, city.longitude]}
                radius={city.city_id === selectedCityId ? 8 : 6}
                interactive={true} // Explicitly ensure markers are clickable
                pathOptions={{
                  color:
                    city.city_id === selectedCityId ? (isDark ? "#ffffff" : "#0f172a") : "transparent",
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
          </>
        )}
      </MapContainer>
    </div>
  );
};
