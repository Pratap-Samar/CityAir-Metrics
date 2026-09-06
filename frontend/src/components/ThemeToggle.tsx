import React, { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

type ThemeToggleProps = {
  isCollapsed?: boolean;
};

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ isCollapsed = false }) => {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== "undefined") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      const stored = localStorage.getItem("theme");
      return stored === "dark" || (!stored && prefersDark);
    }
    return false;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
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
    <button onClick={toggleTheme} className="theme-toggle" title={isCollapsed ? "Toggle theme" : undefined}>
      {isDark ? <Moon size={20} className="nav-icon" /> : <Sun size={20} className="nav-icon" />}
      {!isCollapsed && <span className="nav-label">{isDark ? "Dark Mode" : "Light Mode"}</span>}
    </button>
  );
};
