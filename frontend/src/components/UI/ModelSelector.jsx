import './ModelSelector.css';

export default function ModelSelector({ models, selectedModel, onSelect, loading }) {
  return (
    <div className="model-selector">
      <label className="model-selector-label">Model</label>
      <div className="model-select-wrapper">
        <select
          className="model-select"
          value={selectedModel}
          onChange={(e) => onSelect(e.target.value)}
          disabled={loading || models.length === 0}
        >
          {models.length === 0 ? (
            <option value="">No models found</option>
          ) : (
            models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))
          )}
        </select>
        <div className="model-select-arrow">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
    </div>
  );
}
