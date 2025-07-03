import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, ThemeProvider, CssBaseline } from '@mui/material';
import modernTheme from './theme/modernTheme';
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

function App() {
  const { isAuthenticated, initializeAuth } = useAuthStore();
  const location = useLocation();

  // Initialize auth on app start
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // 隐藏导航栏的页面
  const hideNavbarPages = ['/login', '/register'];
  const shouldHideNavbar = hideNavbarPages.includes(location.pathname);

  return (
    <ThemeProvider theme={modernTheme}>
      <CssBaseline />
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background: shouldHideNavbar
          ? 'transparent'
          : 'linear-gradient(135deg, #FEFBF7 0%, #F9F7F4 50%, #FEF7ED 100%)',
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
    </ThemeProvider>
  );
}

export default App;
