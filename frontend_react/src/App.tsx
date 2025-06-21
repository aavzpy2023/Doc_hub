// --- /frontend_react/src/App.tsx ---
import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar/Sidebar";
import MainContent from "./components/MainContent/MainContent";
import ThemeSwitcher from "./components/ThemeSwitcher/ThemeSwitcher";
import styles from "./App.module.css"; // Usaremos CSS Módulos para App

function App() {
  const [theme, setTheme] = useState<string>(() => {
    return localStorage.getItem("docuhub_theme") || "light";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("docuhub_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  return (
    <div className={styles.appLayout}>
      <Sidebar>
        {/* Pasamos el ThemeSwitcher como hijo para que se renderice en el header del Sidebar */}
        <ThemeSwitcher currentTheme={theme} toggleTheme={toggleTheme} />
      </Sidebar>
      <MainContent />
    </div>
  );
}

export default App;
