import { useNavigate, useLocation } from 'react-router-dom';
import ThemeToggle from '../UI/ThemeToggle';
import './Navbar.css';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-left">
          {!isHome && (
            <button className="navbar-back" onClick={() => navigate('/')} id="nav-back">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              Home
            </button>
          )}
          <button className="navbar-brand" onClick={() => navigate('/')} id="nav-brand">
            <span className="navbar-brand-icon">📄</span>
            <span className="navbar-brand-text gradient-text">AskPDF</span>
          </button>
        </div>
        <div className="navbar-right">
          <div className="navbar-badge">
            <span className="navbar-badge-dot"></span>
            100% Local
          </div>
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}
