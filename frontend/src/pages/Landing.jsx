import FeatureCard from '../components/UI/FeatureCard';
import './Landing.css';

export default function Landing() {
  return (
    <div className="landing">
      {/* Background Effects */}
      <div className="landing-bg">
        <div className="landing-orb landing-orb-1"></div>
        <div className="landing-orb landing-orb-2"></div>
        <div className="landing-grid"></div>
      </div>

      {/* Hero Section */}
      <div className="landing-hero fade-in-up">
        <div className="landing-accent-bar"></div>
        <h1 className="landing-title">
          <span className="gradient-text-animated">AskPDF</span>
        </h1>
        <p className="landing-subtitle">
          Your intelligent document companion.<br />
          Private, local, and powerful.
        </p>
        <div className="landing-badge">
          <span className="landing-badge-dot"></span>
          Powered by Ollama &bull; 100% Local &bull; Fully Private
        </div>
      </div>

      {/* Feature Cards */}
      <div className="landing-cards">
        <FeatureCard
          icon="💬"
          title="Context-Free Chat"
          description="Chat directly with your locally available LLM without any document context"
          to="/chat"
          delay={100}
        />
        <FeatureCard
          icon="📄"
          title="PDF-Powered Chat"
          description="Upload PDFs and ask questions with RAG-powered intelligent answers"
          to="/pdf"
          delay={250}
        />
      </div>

      {/* Bottom Features */}
      <div className="landing-features fade-in-up" style={{ animationDelay: '400ms' }}>
        <div className="landing-feature">
          <span className="landing-feature-icon">🔒</span>
          <span>Fully Private</span>
        </div>
        <div className="landing-feature-divider"></div>
        <div className="landing-feature">
          <span className="landing-feature-icon">⚡</span>
          <span>Fast Local Processing</span>
        </div>
        <div className="landing-feature-divider"></div>
        <div className="landing-feature">
          <span className="landing-feature-icon">🧠</span>
          <span>Multi-Query RAG</span>
        </div>
      </div>
    </div>
  );
}
