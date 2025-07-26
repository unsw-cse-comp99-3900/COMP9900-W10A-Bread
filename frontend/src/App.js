import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import { ThemeContextProvider, useThemeContext } from './contexts/ThemeContext';
import './styles/modernAnimations.css';

import { useAuthStore } from './stores/authStore';
import Navbar from './components/Layout/Navbar';
import PublicNavbar from './components/Layout/PublicNavbar';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import ProjectView from './pages/Project/ProjectView';
import DocumentEditor from './pages/Document/DocumentEditor';
import Settings from './pages/Settings/Settings';
import GuestMode from './pages/Guest/GuestMode';
import GuestEditor from './pages/Guest/GuestEditor';
import ProtectedRoute from './components/Auth/ProtectedRoute';

function AppContent() {
  const { isAuthenticated, initializeAuth } = useAuthStore();
  const { theme } = useThemeContext();
  const location = useLocation();

  // Initialize auth on app start
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // 隐藏导航栏的页面
  const hideNavbarPages = ['/login', '/register'];
  const shouldHideNavbar = hideNavbarPages.includes(location.pathname);

  // Dynamic background based on theme
  const getBackground = () => {
    if (shouldHideNavbar) return 'transparent';

    return theme.palette.mode === 'dark'
      ? 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%)'
      : 'linear-gradient(135deg, #FEFBF7 0%, #F9F7F4 50%, #FEF7ED 100%)';
  };

  return (
    <>
      <CssBaseline />
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background: getBackground(),
      }}>
        {!shouldHideNavbar && (isAuthenticated ? <Navbar /> : <PublicNavbar />)}

      <Box sx={{
        flex: 1,
        ...(shouldHideNavbar && { minHeight: '100vh' })
      }}>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} 
          />
          <Route
            path="/register"
            element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />}
          />

          {/* Guest mode routes - no authentication required */}
          <Route path="/guest" element={<GuestMode />} />
          <Route path="/guest/editor" element={<GuestEditor />} />

          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/project/:projectId" element={
            <ProtectedRoute>
              <ProjectView />
            </ProtectedRoute>
          } />
          
          <Route path="/project/:projectId/document/:documentId" element={
            <ProtectedRoute>
              <DocumentEditor />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
          
          {/* Default redirect */}
          <Route
            path="/"
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/guest"} />
            }
          />
          
          {/* Catch all route */}
          <Route 
            path="*" 
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} />
            } 
          />
        </Routes>
      </Box>
      </Box>
    </>
  );
}

function App() {
  return (
    <ThemeContextProvider>
      <AppContent />
    </ThemeContextProvider>
  );
}

export default App;
