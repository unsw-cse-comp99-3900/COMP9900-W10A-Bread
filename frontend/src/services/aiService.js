import api from './api';

// 为AI请求创建专门的配置
const createAIRequest = (timeout = 90000) => {
  return {
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  };
};

export const aiService = {
  // Chat with AI assistant
  chat: async (message, projectId = null, documentId = null, context = null) => {
    const response = await api.post('/ai/chat', {
      message,
      project_id: projectId,
      document_id: documentId,
      context,
    }, createAIRequest(90000)); // 90秒超时
    return response.data;
  },

  // Get writing assistance
  getWritingAssistance: async (text, assistanceType, projectId = null, ageGroup = null) => {
    const response = await api.post('/ai/writing-assistance', {
      text,
      assistance_type: assistanceType,
      project_id: projectId,
      age_group: ageGroup,
    }, createAIRequest(120000)); // 120 seconds timeout for analysis
    return response.data;
  },

  // Get available age groups
  getAgeGroups: async () => {
    const response = await api.get('/ai/age-groups');
    return response.data;
  },

  // Get writing prompts for a project
  getWritingPrompts: async (projectId) => {
    const response = await api.get(`/ai/writing-prompts/${projectId}`);
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
