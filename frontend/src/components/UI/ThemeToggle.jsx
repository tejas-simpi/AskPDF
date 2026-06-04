import { useState, useEffect } from 'react';
import './ThemeToggle.css';

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('askpdf-theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('askpdf-theme', theme);
  }, [theme]);

  const toggle = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const isDark = theme === 'dark';

  return (
    <button
      className="theme-toggle"
      onClick={toggle}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      id="theme-toggle"
    >
      <div className={`theme-toggle-track ${isDark ? '' : 'theme-toggle-light'}`}>
        <span className="theme-toggle-icon theme-toggle-moon">🌙</span>
        <span className="theme-toggle-icon theme-toggle-sun">☀️</span>
        <div className="theme-toggle-thumb"></div>
      </div>
    </button>
  );
}
