import { useEffect, useState } from "react";
import "./App.css";
import type { AnalyticsCity } from "./types";
import { Sidebar } from "./components/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { ComingSoon } from "./pages/ComingSoon";
import { LoadingState } from "./components/LoadingState";
import { ErrorState } from "./components/ErrorState";

const API_URL = "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [cities, setCities] = useState<AnalyticsCity[]>([]);
  const [selectedCityId, setSelectedCityId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const response = await fetch(`${API_URL}/analytics`);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();

      setCities(data);

      if (data.length > 0 && selectedCityId === null) {
        setSelectedCityId(data[0].city_id);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load dashboard data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_URL}/analytics`);

        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();

        setCities(data);

        if (data.length > 0) {
          setSelectedCityId(data[0].city_id);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Unable to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialData();
  }, []);

  const handleCityChange = (id: number) => {
    setSelectedCityId(id);
  };

  const renderContent = () => {
    if (loading && !refreshing) {
      return <LoadingState />;
    }

    if (error && !cities.length) {
      return <ErrorState message={error} onRetry={() => fetchAnalytics(true)} />;
    }

    switch (activeTab) {
      case "dashboard":
        return (
          <Dashboard
            cities={cities}
            selectedCityId={selectedCityId}
            onCityChange={handleCityChange}
            onRefresh={() => fetchAnalytics(true)}
            isRefreshing={refreshing}
          />
        );
      case "cities":
        return <ComingSoon title="Cities Directory" />;
      case "compare":
        return <ComingSoon title="Compare Cities" />;
      case "rankings":
        return <ComingSoon title="City Rankings" />;
      case "history":
        return <ComingSoon title="Historical Data" />;
      case "severe-weather":
        return <ComingSoon title="Severe Weather Alerts" />;
      case "settings":
        return <ComingSoon title="Settings" />;
      default:
        return <Dashboard
            cities={cities}
            selectedCityId={selectedCityId}
            onCityChange={handleCityChange}
            onRefresh={() => fetchAnalytics(true)}
            isRefreshing={refreshing}
          />;
    }
  };

  const selectedCity = cities.find((c) => c.city_id === selectedCityId) ?? null;
  const currentWeatherCode = selectedCity?.weather?.weather_code ?? null;

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} weatherCode={currentWeatherCode} />
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
