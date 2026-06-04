import { useNavigate } from 'react-router-dom';
import './FeatureCard.css';

export default function FeatureCard({ icon, title, description, to, delay = 0 }) {
  const navigate = useNavigate();

  return (
    <button
      className="feature-card"
      onClick={() => navigate(to)}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="feature-card-glow"></div>
      <div className="feature-card-content">
        <span className="feature-card-icon">{icon}</span>
        <h3 className="feature-card-title">{title}</h3>
        <p className="feature-card-desc">{description}</p>
        <span className="feature-card-arrow">→</span>
      </div>
    </button>
  );
}
