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

// Create a separate instance for real-time suggestions with shorter timeout
const realtimeApi = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001/api',
  timeout: 15000, // 15秒超时，适合实时建议
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
      const isRealtimeRequest = error.config?.url?.includes('/realtime/');
      if (isRealtimeRequest) {
        // 实时建议超时不显示错误提示，静默处理
        console.warn('Real-time suggestion timeout - this is normal');
      } else if (isAIRequest) {
        toast.error('AI request timeout. The AI service may be busy, please try again.');
      } else {
        toast.error('Request timeout. Please check your connection.');
      }
    }

    return Promise.reject(error);
  }
);

// Add same interceptors to realtime API
realtimeApi.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

realtimeApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle real-time API errors silently for better UX
    if (error.code === 'ECONNABORTED') {
      console.warn('Real-time suggestion timeout - this is expected behavior');
    } else if (error.response?.status >= 500) {
      console.warn('Real-time suggestion service error:', error.response?.data?.detail);
    }
    return Promise.reject(error);
  }
);

export default api;
export { realtimeApi };
