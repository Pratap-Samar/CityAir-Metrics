import { format, parseISO } from "date-fns";
import type { ForecastDaily, ForecastHourly } from "../types";
import { getWeatherIconComponent } from "../utils/weather";

type ForecastProps = {
  daily: ForecastDaily[];
  hourly: ForecastHourly[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
};

export const Forecast = ({ daily, hourly, loading, error, onRetry }: ForecastProps) => {
  if (loading) {
    return (
      <div className="forecast-content">
        <h2 className="section-title">FORECAST</h2>
        <div className="forecast-skeleton">Loading forecast...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="forecast-content">
        <h2 className="section-title">FORECAST</h2>
        <div className="forecast-error">
          <p>Unable to load forecast data.</p>
          <button onClick={onRetry} className="action-button small">Retry</button>
        </div>
      </div>
    );
  }

  if (daily.length === 0) return null;

  return (
    <div className="forecast-content">
      <h2 className="section-title">FORECAST</h2>
      
      <div className="forecast-daily-row">
        {daily.map((day, idx) => {
          const isToday = idx === 0;
          const Icon = getWeatherIconComponent(day.weather_code);
          const maxTemp = day.temperature_2m_max !== null ? Math.round(day.temperature_2m_max) : "\u2014";
          const minTemp = day.temperature_2m_min !== null ? Math.round(day.temperature_2m_min) : "\u2014";

          return (
            <div key={day.time} className={`forecast-day-item ${isToday ? "today" : ""}`}>
              <span className="fd-name">{isToday ? "Today" : format(parseISO(day.time), "EEE")}</span>
              <Icon size={22} className="fd-icon" />
              <div className="fd-temps">
                <span className="fd-max">{maxTemp}°</span>
                <span className="fd-min">{minTemp}°</span>
              </div>
            </div>
          );
        })}
      </div>
      
      {hourly.length > 0 && (
        <>
          <div className="forecast-divider" />
          <div className="forecast-hourly-section">
            <h3 className="subsection-title">NEXT HOURS</h3>
            <div className="forecast-hourly-row">
              {hourly.slice(0, 12).map((hour) => {
                const Icon = getWeatherIconComponent(hour.weather_code);
                const temp = hour.temperature_2m !== null ? Math.round(hour.temperature_2m) : "\u2014";
                return (
                  <div key={hour.time} className="hourly-item">
                    <span className="hourly-time">{format(parseISO(hour.time), "HH")}</span>
                    <Icon size={16} className="hourly-icon" />
                    <span className="hourly-temp">{temp}°</span>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};