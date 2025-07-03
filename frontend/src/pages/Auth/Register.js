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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
  Stack,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Visibility,
  VisibilityOff,
  PersonAdd as PersonAddIcon,
  AutoAwesome as AutoAwesomeIcon,
  Edit as EditIcon,
  Psychology as PsychologyIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

const Register = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showElements, setShowElements] = useState(false);

  const { control, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      fullName: '',
      username: '',
      email: '',
      ageGroup: '',
      password: '',
      confirmPassword: '',
    }
  });

  const password = watch('password');

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowElements(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('http://localhost:8001/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (response.ok) {
        navigate('/login', { 
          state: { message: 'Registration successful! Please log in.' }
        });
      } else {
        setError(result.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const ageGroups = [
    { value: '3-5', label: '3-5 years (Preschool)' },
    { value: '6-8', label: '6-8 years (Early Elementary)' },
    { value: '9-11', label: '9-11 years (Elementary)' },
    { value: '12-14', label: '12-14 years (Middle School)' },
    { value: '15-17', label: '15-17 years (High School)' },
    { value: '18+', label: '18+ years (Adult)' },
  ];

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
          <PersonAddIcon sx={{ fontSize: 70, color: 'white', animation: `float 8s ease-in-out infinite 2s` }} />
        </Box>

        {/* 居中注册卡片 */}
        <Paper
          elevation={24}
          sx={{
            width: '100%',
            maxWidth: { xs: '90%', sm: '450px', md: '500px' },
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
              <PersonAddIcon sx={{ fontSize: 40, color: 'white' }} />
            </Box>
            
            <Typography variant="h4" fontWeight="700" gutterBottom sx={{ zIndex: 1, position: 'relative' }}>
              Join WritingWay
            </Typography>
            
            <Typography variant="body1" sx={{ opacity: 0.9, zIndex: 1, position: 'relative' }}>
              Start your AI-powered writing journey
            </Typography>
          </Box>

          {/* 表单内容区域 */}
          <Box sx={{ p: { xs: 4, sm: 5, md: 6 } }}>
            {/* 错误提示 */}
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

            {/* 注册表单 */}
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={3}>
                {/* 全名输入 */}
                <Controller
                  name="fullName"
                  control={control}
                  rules={{
                    required: 'Full name is required',
                    minLength: { value: 2, message: 'Name must be at least 2 characters' }
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Full Name"
                      placeholder="Enter your full name"
                      error={!!errors.fullName}
                      helperText={errors.fullName?.message}
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

                {/* 用户名输入 */}
                <Controller
                  name="username"
                  control={control}
                  rules={{
                    required: 'Username is required',
                    minLength: { value: 3, message: 'Username must be at least 3 characters' },
                    pattern: { value: /^[a-zA-Z0-9_]+$/, message: 'Username can only contain letters, numbers, and underscores' }
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Username"
                      placeholder="Choose a username"
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

                {/* 邮箱输入 */}
                <Controller
                  name="email"
                  control={control}
                  rules={{
                    required: 'Email is required',
                    pattern: { value: /^\S+@\S+\.\S+$/, message: 'Please enter a valid email address' }
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type="email"
                      label="Email Address"
                      placeholder="Enter your email"
                      error={!!errors.email}
                      helperText={errors.email?.message}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailIcon sx={{ color: '#6366F1' }} />
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

                {/* 年龄组选择 */}
                <Controller
                  name="ageGroup"
                  control={control}
                  rules={{ required: 'Age group is required' }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.ageGroup}>
                      <InputLabel>Age Group</InputLabel>
                      <Select
                        {...field}
                        label="Age Group"
                        sx={{
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
                        }}
                      >
                        {ageGroups.map((group) => (
                          <MenuItem key={group.value} value={group.value}>
                            {group.label}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.ageGroup && (
                        <FormHelperText>{errors.ageGroup.message}</FormHelperText>
                      )}
                    </FormControl>
                  )}
                />

                {/* 密码输入 */}
                <Controller
                  name="password"
                  control={control}
                  rules={{
                    required: 'Password is required',
                    minLength: { value: 6, message: 'Password must be at least 6 characters' }
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type={showPassword ? 'text' : 'password'}
                      label="Password"
                      placeholder="Create a password"
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

                {/* 确认密码输入 */}
                <Controller
                  name="confirmPassword"
                  control={control}
                  rules={{
                    required: 'Please confirm your password',
                    validate: value => value === password || 'Passwords do not match'
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type={showConfirmPassword ? 'text' : 'password'}
                      label="Confirm Password"
                      placeholder="Confirm your password"
                      error={!!errors.confirmPassword}
                      helperText={errors.confirmPassword?.message}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              edge="end"
                              sx={{ color: '#6366F1' }}
                            >
                              {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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

                {/* 注册按钮 */}
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PersonAddIcon />}
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
                  {loading ? 'Creating Account...' : 'Create Account'}
                </Button>

                {/* 登录链接 */}
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Already have an account?{' '}
                    <Link
                      component={RouterLink}
                      to="/login"
                      sx={{
                        color: '#6366F1',
                        fontWeight: 600,
                        textDecoration: 'none',
                        '&:hover': {
                          textDecoration: 'underline',
                        }
                      }}
                    >
                      Sign In
                    </Link>
                  </Typography>
                </Box>

                {/* 访客模式 */}
                <Box sx={{ textAlign: 'center', mt: 1 }}>
                  <Button
                    component={RouterLink}
                    to="/guest"
                    variant="text"
                    sx={{
                      color: '#6366F1',
                      textTransform: 'none',
                      fontWeight: 500,
                      '&:hover': {
                        backgroundColor: 'rgba(99, 102, 241, 0.04)',
                      }
                    }}
                  >
                    Try Guest Mode
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

export default Register;
