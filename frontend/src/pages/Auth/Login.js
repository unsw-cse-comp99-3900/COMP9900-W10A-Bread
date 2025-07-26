import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  Link,
  IconButton,
  InputAdornment,
  CircularProgress,
  Stack,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import {
  Person as PersonIcon,
  Visibility,
  VisibilityOff,
  Login as LoginIcon,
  AutoAwesome as AutoAwesomeIcon,
  Edit as EditIcon,
  Psychology as PsychologyIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { useAuthStore } from '../../stores/authStore';

const Login = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [showElements, setShowElements] = useState(false);

  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      username: '',
      password: '',
    }
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowElements(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const onSubmit = async (data) => {
    try {
      setError('');

      const result = await login(data);

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    }
  };

  const handleGuestMode = () => {
    navigate('/guest');
  };

  return (
    <>
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          position: 'relative',
          overflow: 'hidden',
          padding: 2,
        }}
      >
        {/* 背景装饰元素 */}
        <Box sx={{ position: 'absolute', top: '10%', right: '10%', zIndex: 1, opacity: 0.1 }}>
          <EditIcon sx={{ fontSize: 120, color: 'white', animation: `float 6s ease-in-out infinite` }} />
        </Box>
        <Box sx={{ position: 'absolute', bottom: '15%', left: '8%', zIndex: 1, opacity: 0.08 }}>
          <PsychologyIcon sx={{ fontSize: 90, color: 'white', animation: `float 9s ease-in-out infinite 1s` }} />
        </Box>
        <Box sx={{ position: 'absolute', top: '20%', left: '15%', zIndex: 1, opacity: 0.06 }}>
          <SchoolIcon sx={{ fontSize: 60, color: 'white', animation: `float 5s ease-in-out infinite 3s` }} />
        </Box>
        <Box sx={{ position: 'absolute', bottom: '25%', right: '20%', zIndex: 1, opacity: 0.1 }}>
          <AutoAwesomeIcon sx={{ fontSize: 45, color: 'white', animation: `float 7s ease-in-out infinite 0.5s` }} />
        </Box>
        <Box sx={{ position: 'absolute', top: '50%', left: '5%', zIndex: 1, opacity: 0.08 }}>
          <LoginIcon sx={{ fontSize: 70, color: 'white', animation: `float 8s ease-in-out infinite 2s` }} />
        </Box>

        {/* 居中登录卡片 */}
        <Paper
          elevation={24}
          sx={{
            width: '100%',
            maxWidth: { xs: '90%', sm: '400px', md: '450px' },
            borderRadius: 4,
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            transition: 'all 0.3s ease',
            zIndex: 2,
            position: 'relative',
            opacity: showElements ? 1 : 0,
            transform: showElements ? 'translateY(0)' : 'translateY(20px)',
            '&:hover': {
              transform: 'translateY(-8px)',
              boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
            }
          }}
        >
          {/* 头部区域 */}
          <Box
            sx={{
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%)',
              color: 'white',
              textAlign: 'center',
              py: 4,
              px: 3,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                backdropFilter: 'blur(10px)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                animation: `pulse 3s ease-in-out infinite`,
                position: 'relative',
                zIndex: 1,
              }}
            >
              <LoginIcon sx={{ fontSize: 40, color: 'white' }} />
            </Box>
            
            <Typography variant="h4" fontWeight="700" gutterBottom sx={{ zIndex: 1, position: 'relative' }}>
              Welcome Back
            </Typography>
            
            <Typography variant="body1" sx={{ opacity: 0.9, zIndex: 1, position: 'relative' }}>
              Sign in to continue your writing journey
            </Typography>
          </Box>

          {/* 表单区域 */}
          <Box sx={{ p: 4 }}>
            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 3,
                  borderRadius: 2,
                  '& .MuiAlert-message': {
                    fontSize: '0.95rem'
                  }
                }}
              >
                {error}
              </Alert>
            )}

            {/* 登录表单 */}
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={3}>
                {/* 用户名输入 */}
                <Controller
                  name="username"
                  control={control}
                  rules={{ required: 'Username is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Username"
                      placeholder="Enter your username"
                      error={!!errors.username}
                      helperText={errors.username?.message}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PersonIcon sx={{ color: '#6366F1' }} />
                          </InputAdornment>
                        ),
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          height: '56px',
                          fontSize: '1.1rem',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.15)',
                          },
                          '&.Mui-focused': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)',
                          }
                        }
                      }}
                    />
                  )}
                />

                {/* 密码输入 */}
                <Controller
                  name="password"
                  control={control}
                  rules={{ required: 'Password is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type={showPassword ? 'text' : 'password'}
                      label="Password"
                      placeholder="Enter your password"
                      error={!!errors.password}
                      helperText={errors.password?.message}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              sx={{ color: '#6366F1' }}
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          height: '56px',
                          fontSize: '1.1rem',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.15)',
                          },
                          '&.Mui-focused': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)',
                          }
                        }
                      }}
                    />
                  )}
                />

                {/* 登录按钮 */}
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
                  sx={{
                    py: 2,
                    height: '56px',
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                    boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)',
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5B5FE8 0%, #7C3AED 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 20px rgba(99, 102, 241, 0.6)',
                    },
                    '&:active': {
                      transform: 'translateY(0px)',
                    }
                  }}
                >
                  {isLoading ? 'Signing In...' : 'Sign In'}
                </Button>

                {/* 注册链接和访客模式 */}
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Don't have an account?{' '}
                    <Link 
                      component={RouterLink} 
                      to="/register" 
                      sx={{ 
                        color: '#6366F1', 
                        fontWeight: 600,
                        textDecoration: 'none',
                        '&:hover': {
                          textDecoration: 'underline',
                        }
                      }}
                    >
                      Sign up here
                    </Link>
                  </Typography>
                  
                  <Button
                    variant="outlined"
                    onClick={handleGuestMode}
                    sx={{
                      borderColor: '#6366F1',
                      color: '#6366F1',
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 500,
                      '&:hover': {
                        borderColor: '#5B5FE8',
                        backgroundColor: 'rgba(99, 102, 241, 0.04)',
                        transform: 'translateY(-1px)',
                      }
                    }}
                  >
                    Continue as Guest
                  </Button>
                </Box>
              </Stack>
            </form>
          </Box>
        </Paper>
      </Box>
    </>
  );
};

export default Login;
