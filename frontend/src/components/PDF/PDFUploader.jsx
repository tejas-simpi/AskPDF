import { useRef, useState } from 'react';
import './PDFUploader.css';

export default function PDFUploader({ onUpload, loading, uploadedFiles = [] }) {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFiles = (files) => {
    const pdfFiles = Array.from(files).filter(f => f.type === 'application/pdf');
    if (pdfFiles.length > 0) {
      onUpload(pdfFiles);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleChange = (e) => {
    handleFiles(e.target.files);
  };

  return (
    <div className="pdf-uploader-section">
      <div
        className={`pdf-dropzone ${dragActive ? 'pdf-dropzone-active' : ''} ${loading ? 'pdf-dropzone-loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        id="pdf-dropzone"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleChange}
          className="pdf-file-input"
          id="pdf-file-input"
        />
        <div className="pdf-dropzone-content">
          <div className="pdf-dropzone-icon">
            {loading ? '⏳' : '📄'}
          </div>
          <div className="pdf-dropzone-text">
            {loading ? 'Processing PDFs...' : 'Drop PDF files here or click to browse'}
          </div>
          <div className="pdf-dropzone-hint">
            Supports multiple PDF files
          </div>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="pdf-file-pills">
          {uploadedFiles.map((name, i) => (
            <span key={i} className="pdf-file-pill">
              📄 {name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
