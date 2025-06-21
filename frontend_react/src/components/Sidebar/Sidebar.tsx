// --- /frontend_react/src/components/Sidebar/Sidebar.tsx ---
import React from "react";
import styles from "./Sidebar.module.css";

interface SidebarProps {
  children?: React.ReactNode; // Para aceptar el ThemeSwitcher
}

const Sidebar: React.FC<SidebarProps> = ({ children }) => {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarHeader}>
        <h2>Documentación</h2>
        {children} {/* Aquí se renderizará el ThemeSwitcher */}
      </div>
      <div className={styles.fileTree}>
        <p style={{ color: "var(--text-muted)", padding: "1rem" }}>
          Árbol de archivos (próximamente)...
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
