import React, { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

type ThemeToggleProps = {
  isCollapsed?: boolean;
};

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ isCollapsed = false }) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "dark") {
      setIsDark(true);
    }
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <button onClick={toggleTheme} className="nav-item theme-toggle" title={isCollapsed ? "Toggle theme" : undefined} style={{ marginTop: "auto", marginBottom: "80px" }}>
      {isDark ? <Moon size={20} className="nav-icon" /> : <Sun size={20} className="nav-icon" />}
      {!isCollapsed && <span className="nav-label" style={{ marginLeft: "12px" }}>{isDark ? "Dark Mode" : "Light Mode"}</span>}
    </button>
  );
};
