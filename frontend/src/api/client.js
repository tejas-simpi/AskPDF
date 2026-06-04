const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

export const api = {
  // Health
  health: () => request('/health'),

  // Models
  getModels: () => request('/models'),

  // Generic Chat
  sendMessage: (message, model, systemPrompt) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        model,
        system_prompt: systemPrompt,
      }),
    }),

  clearChat: () =>
    request('/chat/clear', { method: 'POST' }),

  // PDF
  uploadPDFs: (files) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    return request('/pdf/upload', {
      method: 'POST',
      body: formData,
    });
  },

  getPDFPages: () => request('/pdf/pages'),

  askPDF: (question, model) =>
    request('/pdf/ask', {
      method: 'POST',
      body: JSON.stringify({ question, model }),
    }),

  deletePDFCollection: () =>
    request('/pdf/delete', { method: 'DELETE' }),
};
