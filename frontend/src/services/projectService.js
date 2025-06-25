import api from './api';

export const projectService = {
  // Get all projects
  getProjects: async () => {
    const response = await api.get('/projects/');
    return response.data;
  },

  // Get a specific project
  getProject: async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  // Create a new project
  createProject: async (projectData) => {
    const response = await api.post('/projects/', projectData);
    return response.data;
  },

  // Update a project
  updateProject: async (projectId, projectData) => {
    const response = await api.put(`/projects/${projectId}`, projectData);
    return response.data;
  },

  // Delete a project
  deleteProject: async (projectId) => {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },

  // Get project documents
  getProjectDocuments: async (projectId) => {
    const response = await api.get(`/documents/project/${projectId}`);
    return response.data;
  },

  // Create a document
  createDocument: async (documentData) => {
    const response = await api.post('/documents/', documentData);
    return response.data;
  },

  // Get a specific document
  getDocument: async (documentId) => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  // Update a document
  updateDocument: async (documentId, documentData) => {
    const response = await api.put(`/documents/${documentId}`, documentData);
    return response.data;
  },

  // Delete a document
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },
};

export default projectService;
