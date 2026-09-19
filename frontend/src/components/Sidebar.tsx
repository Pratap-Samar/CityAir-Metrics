import React from "react";
import {
  Home,
  Database,
  Info,
  Menu,
  GitCompare,
  ListOrdered
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
  onToggleCollapse,
}) => {
  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-brand" style={{ whiteSpace: "nowrap" }}>
        <h2>CityAir Metrics</h2>
        {!isCollapsed && (
          <button
            onClick={onToggleCollapse}
            style={{
              marginLeft: "auto",
              border: "none",
              background: "none",
              cursor: "pointer",
              color: "var(--muted-text)",
            }}
          >
            <Menu size={20} />
          </button>
        )}
      </div>

      {isCollapsed && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: "16px",
          }}
        >
          <button
            onClick={onToggleCollapse}
            style={{
              border: "none",
              background: "none",
              cursor: "pointer",
              color: "var(--muted-text)",
            }}
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
          onClick={() => onTabChange("ranking")}
          className={`nav-item ${activeTab === "ranking" ? "active" : ""}`}
        >
          <ListOrdered size={20} className="nav-icon" />
          <span>Rankings</span>
        </button>

        <button
          onClick={() => onTabChange("compare")}
          className={`nav-item ${activeTab === "compare" ? "active" : ""}`}
        >
          <GitCompare size={20} className="nav-icon" />
          <span>Compare</span>
        </button>

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
