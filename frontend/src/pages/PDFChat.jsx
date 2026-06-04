import { useState, useEffect } from 'react';
import { api } from '../api/client';
import ChatWindow from '../components/Chat/ChatWindow';
import ModelSelector from '../components/UI/ModelSelector';
import PDFUploader from '../components/PDF/PDFUploader';
import PDFViewer from '../components/PDF/PDFViewer';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import EmptyState from '../components/UI/EmptyState';
import './PDFChat.css';

export default function PDFChat() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfPages, setPdfPages] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [totalChunks, setTotalChunks] = useState(0);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setModelsLoading(true);
    try {
      const data = await api.getModels();
      setModels(data.models);
      if (data.models.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0]);
      }
    } catch (err) {
      setError('Could not connect to Ollama. Make sure it is running.');
    } finally {
      setModelsLoading(false);
    }
  };

  const handleUpload = async (files) => {
    setUploadLoading(true);
    setError('');

    try {
      const data = await api.uploadPDFs(files);
      setPdfPages(data.pages);
      setUploadedFiles(data.files);
      setTotalChunks(data.total_chunks);
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleSend = async (question) => {
    if (!selectedModel) return;

    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);
    setError('');

    try {
      const data = await api.askPDF(question, selectedModel);
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `⚠️ Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await api.deletePDFCollection();
      setPdfPages([]);
      setUploadedFiles([]);
      setMessages([]);
      setTotalChunks(0);
    } catch (err) {
      setError(`Delete failed: ${err.message}`);
    }
  };

  if (modelsLoading) {
    return (
      <div className="pdf-chat-loading">
        <LoadingSpinner size="lg" text="Loading models..." />
      </div>
    );
  }

  return (
    <div className="pdf-chat">
      {/* Left Panel — PDF Upload & Viewer */}
      <div className="pdf-chat-left">
        <div className="pdf-chat-left-inner">
          <div className="page-header fade-in-up">
            <h2>📄 PDF Chat</h2>
            <p>Upload PDFs and chat with your documents using RAG</p>
            <div className="page-header-accent"></div>
          </div>

          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onSelect={setSelectedModel}
            loading={loading}
          />

          <PDFUploader
            onUpload={handleUpload}
            loading={uploadLoading}
            uploadedFiles={uploadedFiles}
          />

          {error && (
            <div className="error-banner fade-in">
              ⚠️ {error}
            </div>
          )}

          <PDFViewer
            pages={pdfPages}
            totalPages={pdfPages.length}
          />

          {uploadedFiles.length > 0 && (
            <div className="pdf-chat-actions">
              <div className="pdf-chat-stats">
                <span className="pdf-stat">
                  📄 {uploadedFiles.length} file{uploadedFiles.length > 1 ? 's' : ''}
                </span>
                <span className="pdf-stat">
                  📊 {totalChunks} chunks
                </span>
                <span className="pdf-stat">
                  📃 {pdfPages.length} pages
                </span>
              </div>
              <button
                className="btn btn-danger btn-full"
                onClick={handleDelete}
                id="delete-collection-btn"
              >
                ⚠️ Delete Collection
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel — Chat */}
      <div className="pdf-chat-right">
        <div className="chat-container">
          {uploadedFiles.length === 0 ? (
            <div className="pdf-chat-empty-wrapper">
              <EmptyState
                icon="📄"
                title="Upload a PDF to Begin"
                description="Upload one or more PDF files, then ask questions about their content"
              />
            </div>
          ) : (
            <ChatWindow
              messages={messages}
              onSend={handleSend}
              loading={loading}
              emptyIcon="💬"
              emptyTitle="Ready to Chat"
              emptyDesc="Your documents are loaded. Ask a question below!"
              placeholder="Ask about your documents..."
            />
          )}
        </div>
      </div>
    </div>
  );
}
