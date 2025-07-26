import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
} from '@mui/material';
import {
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
  AccountCircle as GuestIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const PublicNavbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const isGuestMode = location.pathname.startsWith('/guest');

  return (
    <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
      <Toolbar>
        <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
          <EditIcon sx={{ mr: 1 }} />
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ cursor: 'pointer' }}
            onClick={() => navigate('/')}
          >
            WritingWay
          </Typography>
          {isGuestMode && (
            <Chip 
              label="Guest Mode" 
              size="small" 
              sx={{ 
                ml: 2, 
                backgroundColor: 'rgba(255,255,255,0.2)', 
                color: 'white' 
              }} 
            />
          )}
        </Box>

        <Box display="flex" alignItems="center" gap={1}>
          {!isGuestMode && (
            <Button
              color="inherit"
              startIcon={<GuestIcon />}
              onClick={() => navigate('/guest')}
            >
              Try Guest Mode
            </Button>
          )}
          
          <Button
            color="inherit"
            startIcon={<LoginIcon />}
            onClick={() => navigate('/login')}
          >
            Login
          </Button>
          
          <Button
            color="inherit"
            startIcon={<RegisterIcon />}
            onClick={() => navigate('/register')}
            variant="outlined"
            sx={{ 
              borderColor: 'white', 
              '&:hover': { 
                borderColor: 'white', 
                backgroundColor: 'rgba(255,255,255,0.1)' 
              } 
            }}
          >
            Register
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default PublicNavbar;
