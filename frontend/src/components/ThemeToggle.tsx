import React from "react";
import { Sun, Moon } from "lucide-react";

type ThemeToggleProps = {
  isCollapsed: boolean;
};

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ isCollapsed }) => {
  const [isDark, setIsDark] = React.useState(true); // Default dark based on our CSS

  const toggleTheme = () => {
    // In a real app, you would toggle a class on the body or html tag
    // and save the preference in localStorage.
    // For now, we'll just toggle local state to show the icon change.
    setIsDark(!isDark);
    
    if (isDark) {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className="nav-item theme-toggle"
      title={isCollapsed ? "Toggle theme" : undefined}
      style={{ marginTop: "auto", marginBottom: "80px" }}
    >
      {isDark ? (
        <Moon size={20} className="nav-icon" />
      ) : (
        <Sun size={20} className="nav-icon" />
      )}
      <span className="nav-label" style={{ marginLeft: "12px" }}>
        {isDark ? "Dark Mode" : "Light Mode"}
      </span>
    </button>
  );
};
