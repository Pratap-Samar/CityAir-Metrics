import React from "react";
import { MapPin } from "lucide-react";
import type { DashboardMapData } from "../types";

type CitySelectorProps = {
  cities: DashboardMapData[];
  selectedCityId: number | null;
  onCityChange: (id: number) => void;
};

export const CitySelector: React.FC<CitySelectorProps> = ({
  cities,
  selectedCityId,
  onCityChange,
}) => {
  return (
    <div className="city-selector-wrapper">
      <MapPin size={20} className="city-selector-icon" />
      <select
        className="city-selector"
        value={selectedCityId ?? ""}
        onChange={(e) => onCityChange(Number(e.target.value))}
        aria-label="Select City"
      >
        {cities.map((city) => (
          <option key={city.city_id} value={city.city_id}>
            {city.city_name}, {city.country}
          </option>
        ))}
      </select>
    </div>
  );
};
