import { useState, useEffect } from "react";
import { Routes, Route, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import "./App.css";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { Dashboard } from "./pages/Dashboard";
import { CityPage } from "./pages/CityPage";
import { Rankings } from "./pages/Rankings";
import { Compare } from "./pages/Compare";
import { DataPipeline } from "./pages/DataPipeline";
import { About } from "./pages/About";
import type { DashboardMapData, DashboardSummary } from "./types";

import { LoadingState } from "./components/LoadingState";
import { ErrorState } from "./components/ErrorState";

export const API_URL = "http://localhost:8000";

function CityPageRouteWrapper({ cities }: { cities: DashboardMapData[] }) {
  const { cityName } = useParams<{ cityName: string }>();
  const navigate = useNavigate();
  
  const city = cities.find(c => c.city_name.toLowerCase() === decodeURIComponent(cityName || "").toLowerCase());
  const cityId = city ? city.city_id : null;

  return (
    <CityPage
      cities={cities}
      cityId={cityId}
      onBack={() => navigate("/")}
    />
  );
}

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [cities, setCities] = useState<DashboardMapData[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  // Auto-collapse sidebar on tablet screens (<= 1024px)
  useEffect(() => {
    const checkSize = () => {
      if (window.innerWidth <= 1024) {
        setIsCollapsed(true);
      } else {
        setIsCollapsed(false);
      }
    };
    checkSize(); // initial check
    window.addEventListener('resize', checkSize);
    return () => window.removeEventListener('resize', checkSize);
  }, []);
  
  // Local state for dashboard map selection
  const [dashboardCityId, setDashboardCityId] = useState<number | null>(null);

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

      // Initialize dashboard selected city
      if (citiesArray.length > 0 && dashboardCityId === null) {
        const delhi = citiesArray.find((c: DashboardMapData) => c.city_name === "New Delhi" || c.city_name === "Delhi");
        setDashboardCityId(delhi ? delhi.city_id : citiesArray[0].city_id);
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
    const city = cities.find(c => c.city_id === id);
    if (city) {
      navigate(`/city/${encodeURIComponent(city.city_name)}`);
    }
  };

  // Derive active city ID for Header from URL or fallback to Dashboard selection
  let activeCityId: number | null = null;
  const cityMatch = location.pathname.match(/^\/city\/(.+)$/);
  if (cityMatch && cities.length > 0) {
    const name = decodeURIComponent(cityMatch[1]);
    const city = cities.find(c => c.city_name.toLowerCase() === name.toLowerCase());
    if (city) {
      activeCityId = city.city_id;
    }
  } else {
    activeCityId = dashboardCityId;
  }

  const renderContent = () => {
    if (loading && cities.length === 0) return <LoadingState />;
    if (error)
      return <ErrorState message={error} onRetry={fetchDashboardData} />;

    return (
      <Routes>
        <Route 
          path="/" 
          element={
            <Dashboard
              cities={cities}
              summary={summary}
              selectedCityId={dashboardCityId}
              onCityChange={(id) => setDashboardCityId(id)}
              onViewReport={() => {
                if (dashboardCityId) handleCityChange(dashboardCityId);
              }}
            />
          } 
        />
        <Route path="/city/:cityName" element={<CityPageRouteWrapper cities={cities} />} />
        <Route path="/ranking" element={<Rankings onCitySelect={handleCityChange} />} />
        <Route path="/compare" element={<Compare cities={cities} />} />
        <Route path="/pipeline" element={<DataPipeline summary={summary} />} />
        <Route path="/about" element={<About summary={summary} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  };

  // Map route to activeTab string for Sidebar
  let activeTab = "dashboard";
  if (location.pathname.startsWith("/city")) activeTab = "city";
  else if (location.pathname === "/ranking") activeTab = "ranking";
  else if (location.pathname === "/compare") activeTab = "compare";
  else if (location.pathname === "/pipeline") activeTab = "pipeline";
  else if (location.pathname === "/about") activeTab = "about";

  const handleTabChange = (tab: string) => {
    if (tab === "dashboard") navigate("/");
    else if (tab === "city") {
      if (activeCityId) handleCityChange(activeCityId);
      else if (cities.length > 0) handleCityChange(cities[0].city_id);
    }
    else navigate(`/${tab}`);
  };

  return (
    <div className="app-shell">
      <Sidebar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
      />
      <div className="app-right">
        <Header
          cities={cities}
          selectedCityId={activeCityId}
          onCityChange={handleCityChange}
        />
        <main className="main-content">{renderContent()}</main>
      </div>
    </div>
  );
}

export default App;
