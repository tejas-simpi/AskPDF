import { useState } from 'react';
import './PDFViewer.css';

export default function PDFViewer({ pages = [], totalPages = 0 }) {
  const [zoom, setZoom] = useState(100);

  if (pages.length === 0) return null;

  return (
    <div className="pdf-viewer">
      <div className="pdf-viewer-header">
        <div className="pdf-viewer-title">
          📄 Document Preview
        </div>
        <div className="pdf-viewer-badge">
          {totalPages} page{totalPages !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="pdf-viewer-controls">
        <label className="pdf-zoom-label" htmlFor="pdf-zoom">Zoom</label>
        <input
          id="pdf-zoom"
          type="range"
          className="pdf-zoom-slider"
          min={50}
          max={200}
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
        />
        <span className="pdf-zoom-value">{zoom}%</span>
      </div>

      <div className="pdf-pages-container">
        {pages.map((src, i) => (
          <img
            key={i}
            src={src}
            alt={`Page ${i + 1}`}
            className="pdf-page-image"
            style={{ width: `${zoom}%` }}
          />
        ))}
      </div>
    </div>
  );
}
