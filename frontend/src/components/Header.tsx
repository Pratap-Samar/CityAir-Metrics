import React, { useState, useEffect, useRef } from "react";
import { Search, Calendar, MapPin } from "lucide-react";
import type { DashboardMapData } from "../types";
import { PipelineStatusIndicator } from "./PipelineStatusIndicator";

type HeaderProps = {
  cities: DashboardMapData[];
  selectedCityId: number | null;
  onCityChange: (id: number) => void;
};

export const Header: React.FC<HeaderProps> = ({ cities, onCityChange }) => {
  const [query, setQuery] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const datePart = currentTime.toLocaleString("en-US", {
    timeZone: "Asia/Kolkata",
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric"
  });
  
  const timePart = currentTime.toLocaleString("en-US", {
    timeZone: "Asia/Kolkata",
    hour: "numeric",
    minute: "2-digit",
    hour12: true
  });
  
  const dateStr = `${datePart}  ${timePart}`;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredCities = cities.filter(c => 
    c.city_name.toLowerCase().includes(query.toLowerCase()) || 
    c.country.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (id: number) => {
    onCityChange(id);
    setQuery("");
    setShowDropdown(false);
  };

  return (
    <header className="global-header">
      <div className="header-search-container" ref={dropdownRef}>
        <Search size={18} className="search-icon" />
        <input 
          type="text" 
          placeholder="Search city..." 
          className="header-search-input"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowDropdown(true);
          }}
          onFocus={() => setShowDropdown(true)}
        />
        {showDropdown && query.trim() !== "" && (
          <div className="header-search-dropdown">
            {filteredCities.length > 0 ? (
              filteredCities.map(city => (
                <div 
                  key={city.city_id} 
                  className="search-result-item"
                  onClick={() => handleSelect(city.city_id)}
                >
                  <MapPin size={16} color="#6b7280" />
                  <span><strong>{city.city_name}</strong>, {city.country}</span>
                </div>
              ))
            ) : (
              <div className="search-no-results">No cities found</div>
            )}
          </div>
        )}
      </div>

      <div className="header-right">
        <div className="header-datetime">
          <Calendar size={16} color="#6b7280" />
          <span>{dateStr}</span>
        </div>
        <PipelineStatusIndicator />
      </div>
    </header>
  );
};
