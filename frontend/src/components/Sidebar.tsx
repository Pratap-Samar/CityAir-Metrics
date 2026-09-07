import React from "react";
import {
  Home,
  BarChart2,
  Database,
  Info,
  ChevronDown,
  Leaf,
  Menu
} from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

type SidebarProps = {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
};

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  onTabChange, 
  isCollapsed, 
  onToggleCollapse 
}) => {
  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-brand">
        <Leaf size={24} className="brand-logo" />
        <h2>CityAir Metrics</h2>
        {!isCollapsed && (
          <button 
            onClick={onToggleCollapse}
            style={{ marginLeft: "auto", border: "none", background: "none", cursor: "pointer", color: "var(--muted-text)" }}
          >
            <Menu size={20} />
          </button>
        )}
      </div>

      {isCollapsed && (
        <div style={{ display: "flex", justifyContent: "center", marginBottom: "16px" }}>
          <button 
            onClick={onToggleCollapse}
            style={{ border: "none", background: "none", cursor: "pointer", color: "var(--muted-text)" }}
          >
            <Menu size={20} />
          </button>
        </div>
      )}

      <nav className="sidebar-nav">
        <button
          onClick={() => onTabChange("dashboard")}
          className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
        >
          <Home size={20} className="nav-icon" />
          <span>Dashboard</span>
        </button>

        <button
          onClick={() => onTabChange("analytics")}
          className={`nav-item ${activeTab === "analytics" ? "active" : ""}`}
        >
          <BarChart2 size={20} className="nav-icon" />
          <span>Analytics</span>
          {!isCollapsed && <ChevronDown size={16} className="nav-icon" style={{ marginLeft: "auto" }} />}
        </button>

        {!isCollapsed && activeTab === "analytics" && (
          <div className="nav-sub">
            <div className="nav-sub-item">Compare</div>
            <div className="nav-sub-item">Rankings</div>
          </div>
        )}

        <button
          onClick={() => onTabChange("pipeline")}
          className={`nav-item ${activeTab === "pipeline" ? "active" : ""}`}
        >
          <Database size={20} className="nav-icon" />
          <span>Data Pipeline</span>
        </button>

        <button
          onClick={() => onTabChange("about")}
          className={`nav-item ${activeTab === "about" ? "active" : ""}`}
        >
          <Info size={20} className="nav-icon" />
          <span>About</span>
        </button>

        <ThemeToggle isCollapsed={isCollapsed} />
      </nav>
    </aside>
  );
};
