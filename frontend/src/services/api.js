import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001/api',
  timeout: 60000, // 增加到60秒，适合AI请求
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      toast.error('Access denied');
    } else if (error.response?.status >= 500) {
      // 检查是否是AI服务错误
      const errorMessage = error.response?.data?.detail || 'Server error';
      if (errorMessage.includes('AI service error')) {
        toast.error('AI service is temporarily unavailable. Please try again in a moment.');
      } else {
        toast.error('Server error. Please try again later.');
      }
    } else if (error.code === 'ECONNABORTED') {
      // 区分AI请求超时和普通请求超时
      const isAIRequest = error.config?.url?.includes('/ai/');
      if (isAIRequest) {
        toast.error('AI request timeout. The AI service may be busy, please try again.');
      } else {
        toast.error('Request timeout. Please check your connection.');
      }
    }

    return Promise.reject(error);
  }
);

export default api;
