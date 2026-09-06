import React, { useState } from "react";
import { ThemeToggle } from "./ThemeToggle";
import { getWeatherIconComponent } from "../utils/weather";
import {
  LayoutDashboard,
  Building2,
  GitCompare,
  Trophy,
  ChartLine,
  CloudLightning,
  Settings,
  PanelLeftClose,
  PanelLeftOpen
} from "lucide-react";

type SidebarProps = {
  activeTab: string;
  onTabChange: (tab: string) => void;
  weatherCode?: number | null;
};

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, weatherCode = null }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const WeatherIcon = getWeatherIconComponent(weatherCode ?? null);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "cities", label: "Cities", icon: Building2 },
    { id: "compare", label: "Compare", icon: GitCompare },
    { id: "rankings", label: "Rankings", icon: Trophy },
    { id: "history", label: "History", icon: ChartLine },
    { id: "severe-weather", label: "Severe Weather", icon: CloudLightning },
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <div className="brand-mark">
          <span className="brand-full">CITYAIR METRICS</span>
          <span className="brand-short">CA</span>
        </div>
        <button 
          className="collapse-toggle" 
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>

      <div className="sidebar-weather-badge" title="Current weather">
        {/* eslint-disable-next-line react-hooks/static-components */}
        <WeatherIcon size={16} className="sidebar-weather-icon" />
        <span className="nav-label sidebar-weather-label">
          {weatherCode !== null && weatherCode !== undefined ? "Live" : ""}
        </span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`nav-item ${activeTab === item.id ? "active" : ""}`}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon size={20} className="nav-icon" />
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          onClick={() => onTabChange("settings")}
          className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
          title={isCollapsed ? "Settings" : undefined}
        >
          <Settings size={20} className="nav-icon" />
          <span className="nav-label">Settings</span>
        </button>
        <ThemeToggle isCollapsed={isCollapsed} />
      </div>
    </aside>
  );
};