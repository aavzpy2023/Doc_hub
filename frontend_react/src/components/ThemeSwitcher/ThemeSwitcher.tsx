// --- /frontend_react/src/components/ThemeSwitcher/ThemeSwitcher.tsx ---
import React from "react";
import styles from "./ThemeSwitcher.module.css";

interface ThemeSwitcherProps {
  currentTheme: string;
  toggleTheme: () => void;
}

const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({
  currentTheme,
  toggleTheme,
}) => {
  return (
    <button
      onClick={toggleTheme}
      className={styles.themeButton}
      title="Cambiar tema"
    >
      {currentTheme === "light" ? "☀️" : "🌙"}
    </button>
  );
};

export default ThemeSwitcher;
