import api from './api';

// Guest mode service - no authentication required
export const guestService = {
  // Get writing assistance for guests
  getWritingAssistance: async (text, assistanceType, ageGroup = 'high_school') => {
    const response = await api.post('/guest/writing-assistance', {
      text,
      assistance_type: assistanceType,
      age_group: ageGroup,
    }, {
      timeout: 120000, // 120 seconds timeout for AI requests
    });
    return response.data;
  },

  // Get writing prompts for guests
  getWritingPrompts: async (projectName = 'My Writing Project', ageGroup = 'high_school') => {
    const response = await api.post('/guest/writing-prompts', {
      project_name: projectName,
      age_group: ageGroup,
    });
    return response.data;
  },

  // Get available age groups (informational)
  getAgeGroups: async () => {
    const response = await api.get('/guest/age-groups');
    return response.data;
  },

  // Get demo content
  getDemoContent: async () => {
    const response = await api.get('/guest/demo-content');
    return response.data;
  },

  // Health check for guest mode
  healthCheck: async () => {
    const response = await api.get('/guest/health');
    return response.data;
  },
};

export default guestService;
