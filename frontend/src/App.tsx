import { useState, useEffect } from "react";
import "./App.css";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { Dashboard } from "./pages/Dashboard";
import { CityPage } from "./pages/CityPage";
import type { DashboardMapData, DashboardSummary } from "./types";

import { LoadingState } from "./components/LoadingState";
import { ErrorState } from "./components/ErrorState";

const API_URL = "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [cities, setCities] = useState<DashboardMapData[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [selectedCityId, setSelectedCityId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isCollapsed, setIsCollapsed] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [mapRes, summaryRes] = await Promise.all([
        fetch(`${API_URL}/dashboard/map`),
        fetch(`${API_URL}/dashboard/summary`),
      ]);

      if (!mapRes.ok || !summaryRes.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const mapData = await mapRes.json();
      const summaryData = await summaryRes.json();

      const citiesArray = Array.isArray(mapData)
        ? mapData
        : mapData.cities || [];
      setCities(citiesArray);
      setSummary(summaryData);

      if (citiesArray.length > 0 && selectedCityId === null) {
        const delhi = citiesArray.find(
          (c: DashboardMapData) => c.city_name === "New Delhi",
        );
        setSelectedCityId(delhi ? delhi.city_id : citiesArray[0].city_id);
      }
    } catch (err: Error | unknown) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line
    fetchDashboardData();
  }, []);

  const handleCityChange = (id: number) => {
    setSelectedCityId(id);
    setActiveTab("city");
  };

  const handleCitySelectMap = (id: number) => {
    setSelectedCityId(id);
  };

  const renderContent = () => {
    if (loading && cities.length === 0) return <LoadingState />;
    if (error)
      return <ErrorState message={error} onRetry={fetchDashboardData} />;

    switch (activeTab) {
      case "dashboard":
        return (
          <Dashboard
            cities={cities}
            summary={summary}
            selectedCityId={selectedCityId}
            onCityChange={handleCitySelectMap}
            onViewReport={() => setActiveTab("city")}
          />
        );
      case "city":
        return (
          <CityPage
            cities={cities}
            cityId={selectedCityId}
            onBack={() => setActiveTab("dashboard")}
          />
        );
      default:
        return <div style={{ padding: "24px" }}>Coming Soon: {activeTab}</div>;
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
      />
      <div className="app-right">
        <Header
          cities={cities}
          selectedCityId={selectedCityId}
          onCityChange={handleCityChange}
        />
        <main className="main-content">{renderContent()}</main>
      </div>
    </div>
  );
}

export default App;
