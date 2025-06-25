import api from './api';

export const aiService = {
  // Chat with AI assistant
  chat: async (message, projectId = null, documentId = null, context = null) => {
    const response = await api.post('/ai/chat', {
      message,
      project_id: projectId,
      document_id: documentId,
      context,
    });
    return response.data;
  },

  // Get writing assistance
  getWritingAssistance: async (text, assistanceType, projectId = null) => {
    const response = await api.post('/ai/writing-assistance', {
      text,
      assistance_type: assistanceType,
      project_id: projectId,
    });
    return response.data;
  },

  // Get conversation history
  getConversationHistory: async (projectId) => {
    const response = await api.get(`/ai/conversations/${projectId}`);
    return response.data;
  },

  // Clear conversation
  clearConversation: async (conversationId) => {
    const response = await api.delete(`/ai/conversations/${conversationId}`);
    return response.data;
  },
};

export default aiService;
