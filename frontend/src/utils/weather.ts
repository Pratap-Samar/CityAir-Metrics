export const getWeatherCondition = (code: number | null): string => {
  if (code === null) return "—";
  
  // WMO Weather interpretation codes (approximate mapping)
  if (code === 0) return "Clear";
  if (code === 1 || code === 2) return "Partly cloudy";
  if (code === 3) return "Cloudy";
  if (code >= 45 && code <= 48) return "Fog";
  if (code >= 51 && code <= 57) return "Drizzle";
  if (code >= 61 && code <= 65) return "Rain";
  if (code >= 66 && code <= 67) return "Freezing Rain";
  if (code >= 71 && code <= 77) return "Snow";
  if (code >= 80 && code <= 82) return "Rain showers";
  if (code >= 85 && code <= 86) return "Snow showers";
  if (code >= 95 && code <= 99) return "Thunderstorm";

  return "Unknown";
};


import { Sun, CloudSun, Cloud, CloudRain, CloudLightning, CloudSnow } from "lucide-react";

export const getWeatherIconComponent = (code: number | null) => {
  if (code === null) return Cloud;
  if (code === 0) return Sun;
  if (code === 1 || code === 2) return CloudSun;
  if (code === 3 || (code >= 45 && code <= 48)) return Cloud;
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return CloudRain;
  if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) return CloudSnow;
  if (code >= 95 && code <= 99) return CloudLightning;
  return Cloud;
};
