import { useState, useEffect } from 'react';
import { api } from '../api/client';
import ChatWindow from '../components/Chat/ChatWindow';
import ModelSelector from '../components/UI/ModelSelector';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import './GenericChat.css';

export default function GenericChat() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful AI assistant.');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch available models on mount
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

  const handleSend = async (message) => {
    if (!selectedModel) return;

    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setLoading(true);
    setError('');

    try {
      const data = await api.sendMessage(message, selectedModel, systemPrompt);
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

  const handleClear = async () => {
    try {
      await api.clearChat();
    } catch {
      // Ignore
    }
    setMessages([]);
  };

  if (modelsLoading) {
    return (
      <div className="generic-chat-loading">
        <LoadingSpinner size="lg" text="Loading models..." />
      </div>
    );
  }

  return (
    <div className="generic-chat">
      {/* Sidebar */}
      <aside className="generic-chat-sidebar">
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h3>💬 Chat Settings</h3>
            <div className="sidebar-header-accent"></div>
          </div>

          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onSelect={setSelectedModel}
            loading={loading}
          />

          <div className="sidebar-section">
            <label className="sidebar-label" htmlFor="system-prompt">System Prompt</label>
            <textarea
              id="system-prompt"
              className="sidebar-textarea"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Define how the chatbot should behave..."
              rows={4}
            />
          </div>

          <div className="sidebar-section">
            <label className="sidebar-label">Actions</label>
            <button
              className="btn btn-full"
              onClick={handleClear}
              disabled={messages.length === 0}
              id="clear-chat-btn"
            >
              🗑️ Clear Chat History
            </button>
          </div>

          <div className="sidebar-divider"></div>

          <div className="sidebar-info">
            <div className="sidebar-info-row">
              <span className="sidebar-info-label">Model</span>
              <span className="sidebar-info-value">{selectedModel || 'None'}</span>
            </div>
            <div className="sidebar-info-row">
              <span className="sidebar-info-label">Messages</span>
              <span className="sidebar-info-value">{messages.length}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="generic-chat-main">
        <div className="page-header fade-in-up">
          <h2>💬 Context-Free Chat</h2>
          <p>Chat with your locally downloaded LLM without any document context</p>
          <div className="page-header-accent"></div>
        </div>


        {error && (
          <div className="error-banner fade-in">
            ⚠️ {error}
          </div>
        )}

        <div className="chat-container">
          <ChatWindow
            messages={messages}
            onSend={handleSend}
            loading={loading}
            emptyIcon="💬"
            emptyTitle="Start a Conversation"
            emptyDesc="Responses here are from the LLM's general knowledge — not from any PDF. Need document answers? Use PDF Chat."
            placeholder="Type your message here..."
          />
        </div>
      </main>
    </div>
  );
}
