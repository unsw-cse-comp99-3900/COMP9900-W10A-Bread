import React, { createContext, useContext, useState, useEffect } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { useAuthStore } from '../stores/authStore';
import api from '../services/api';

// 基础主题配置
const baseTheme = {
  // 字体配置
  typography: {
    fontFamily: [
      'Inter',
      'Poppins',
      '-apple-system',
      'BlinkMacSystemFont',
      '"SF Pro Text"',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  
  // 组件样式
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '24px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '24px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
};

// Light theme configuration
const lightTheme = {
  palette: {
    mode: 'light',
    primary: {
      main: '#6366F1',
      light: '#818CF8',
      dark: '#4F46E5',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#F87171',
      light: '#FCA5A5',
      dark: '#EF4444',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FEFBF7',
      paper: '#FFFFFF',
      soft: '#F9F7F4',
      warm: '#FEF7ED',
    },
    text: {
      primary: '#1F2937',
      secondary: '#6B7280',
      disabled: '#9CA3AF',
    },
  },
};

// Dark theme configuration
const darkTheme = {
  palette: {
    mode: 'dark',
    primary: {
      main: '#818CF8',
      light: '#A5B4FC',
      dark: '#6366F1',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FCA5A5',
      light: '#FECACA',
      dark: '#F87171',
      contrastText: '#000000',
    },
    background: {
      default: '#0F172A',
      paper: '#1E293B',
      soft: '#334155',
      warm: '#475569',
    },
    text: {
      primary: '#F8FAFC',
      secondary: '#CBD5E1',
      disabled: '#64748B',
    },
  },
};

const ThemeContext = createContext();

export const useThemeContext = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeContext must be used within a ThemeContextProvider');
  }
  return context;
};

export const ThemeContextProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuthStore();
  const [settings, setSettings] = useState({
    theme: 'light',
    fontSize: 14,
  });

  // Fetch user settings
  useEffect(() => {
    const fetchSettings = async () => {
      if (isAuthenticated) {
        try {
          const response = await api.get('/settings/');
          setSettings({
            theme: response.data.theme || 'light',
            fontSize: response.data.font_size || 14,
          });
        } catch (error) {
          console.error('Failed to fetch settings:', error);
        }
      }
    };

    fetchSettings();
  }, [isAuthenticated, user]);

  // Create dynamic theme based on settings
  const theme = createTheme({
    ...baseTheme,
    ...(settings.theme === 'dark' ? darkTheme : lightTheme),
    typography: {
      ...baseTheme.typography,
      fontSize: settings.fontSize,
      h1: {
        fontSize: `${settings.fontSize * 2.5 / 14}rem`,
        fontWeight: 700,
        lineHeight: 1.2,
        letterSpacing: '-0.025em',
      },
      h2: {
        fontSize: `${settings.fontSize * 2 / 14}rem`,
        fontWeight: 600,
        lineHeight: 1.3,
        letterSpacing: '-0.025em',
      },
      h3: {
        fontSize: `${settings.fontSize * 1.5 / 14}rem`,
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h4: {
        fontSize: `${settings.fontSize * 1.25 / 14}rem`,
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h5: {
        fontSize: `${settings.fontSize * 1.125 / 14}rem`,
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h6: {
        fontSize: `${settings.fontSize / 14}rem`,
        fontWeight: 600,
        lineHeight: 1.4,
      },
      body1: {
        fontSize: `${settings.fontSize / 14}rem`,
        lineHeight: 1.6,
      },
      body2: {
        fontSize: `${settings.fontSize * 0.875 / 14}rem`,
        lineHeight: 1.6,
      },
    },
  });

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return (
    <ThemeContext.Provider value={{ settings, updateSettings, theme }}>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};
