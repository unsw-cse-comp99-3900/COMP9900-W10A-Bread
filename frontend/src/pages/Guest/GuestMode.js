import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { ModernCard, ModernCardContent } from '../../components/Modern/ModernCard';
import { ModernButton } from '../../components/Modern/ModernButton';
import {
  Edit as EditIcon,
  AutoFixHigh as AIIcon,
  Lightbulb as LightbulbIcon,
  AccountCircle as GuestIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import guestService from '../../services/guestService';

const GuestMode = () => {
  const navigate = useNavigate();
  const [selectedDemo, setSelectedDemo] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('upper_secondary');

  // Fetch demo content
  const { data: demoData } = useQuery(
    'guest-demo-content',
    () => guestService.getDemoContent(),
    {
      onError: (error) => {
        console.error('Failed to load demo content:', error);
      },
    }
  );

  // Fetch age groups info
  const { data: ageGroupsData } = useQuery(
    'guest-age-groups',
    () => guestService.getAgeGroups(),
    {
      onError: (error) => {
        console.error('Failed to load age groups:', error);
      },
    }
  );

  const handleStartWriting = (demoProject = null) => {
    const projectData = demoProject || {
      name: 'My Writing Project',
      description: 'A new writing project',
      sample_text: ''
    };

    navigate('/guest/editor', {
      state: {
        projectData,
        isGuest: true,
        selectedAgeGroup
      }
    });
  };

  const demoProjects = demoData?.demo_projects || [];
  const tips = demoData?.tips || [];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={4} className="fade-in">
        <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
          <Box sx={{
            width: 64,
            height: 64,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mr: 2,
            boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)',
          }}>
            <GuestIcon sx={{ fontSize: 32, color: 'white' }} />
          </Box>
          <Typography variant="h2" component="h1" fontWeight="bold" sx={{
            background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Guest Mode
          </Typography>
        </Box>
        <Typography variant="h5" color="text.secondary" mb={3} sx={{ fontWeight: 400 }}>
          Try WritingWay without registration - Experience AI-powered writing assistance
        </Typography>
        <Box display="flex" alignItems="center" justifyContent="center" gap={3} mb={4} className="fade-in-delay-1">
          <FormControl size="medium" sx={{
            minWidth: 240,
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
            }
          }}>
            <InputLabel sx={{ fontWeight: 500 }}>Choose Your Age Group</InputLabel>
            <Select
              value={selectedAgeGroup}
              label="Choose Your Age Group"
              onChange={(e) => setSelectedAgeGroup(e.target.value)}
            >
              {ageGroupsData?.age_groups?.map((group) => (
                <MenuItem key={group.value} value={group.value}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Chip
            label="Guest Mode"
            sx={{
              background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
              color: '#1F2937',
              fontWeight: 600,
              px: 2,
              py: 1,
              fontSize: '0.875rem',
            }}
          />
        </Box>
      </Box>

      {/* Guest Mode Info */}
      <ModernCard variant="glass" sx={{ mb: 4 }} className="fade-in-delay-2">
        <ModernCardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Box sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2,
            }}>
              <Typography sx={{ fontSize: '1.25rem' }}>🎯</Typography>
            </Box>
            <Typography variant="h6" fontWeight="bold" color="primary">
              Guest Mode Features
            </Typography>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography sx={{ mr: 1, fontSize: '1rem' }}>✨</Typography>
                <Typography variant="body2">No registration required - start writing immediately</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography sx={{ mr: 1, fontSize: '1rem' }}>🎭</Typography>
                <Typography variant="body2">Choose your age group for appropriate AI suggestions</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography sx={{ mr: 1, fontSize: '1rem' }}>💡</Typography>
                <Typography variant="body2">Writing prompts and creative guidance</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography sx={{ mr: 1, fontSize: '1rem' }}>💾</Typography>
                <Typography variant="body2">Your work is stored locally (register to save permanently)</Typography>
              </Box>
            </Grid>
          </Grid>
        </ModernCardContent>
      </ModernCard>

      {/* Quick Start */}
      <ModernCard variant="warm" sx={{ mb: 4 }} className="fade-in-delay-3">
        <ModernCardContent>
          <Box textAlign="center">
            <Typography variant="h4" gutterBottom sx={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2,
            }}>
              🚀 Quick Start
            </Typography>
            <Typography variant="body1" color="text.secondary" mb={4} sx={{ fontSize: '1.125rem' }}>
              Jump right into writing with our AI-powered editor
            </Typography>
            <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
              <ModernButton
                modernVariant="primary"
                size="large"
                startIcon={<EditIcon />}
                onClick={() => handleStartWriting()}
                sx={{ minWidth: 180 }}
              >
                Start Writing Now
              </ModernButton>
              <ModernButton
                modernVariant="outline"
                size="large"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{ minWidth: 120 }}
              >
                Login
              </ModernButton>
              <ModernButton
                modernVariant="accent"
                size="large"
                startIcon={<RegisterIcon />}
                onClick={() => navigate('/register')}
                sx={{ minWidth: 120 }}
              >
                Register
              </ModernButton>
            </Box>
          </Box>
        </ModernCardContent>
      </ModernCard>

      {/* Demo Projects */}
      <Box mb={4}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h4" gutterBottom sx={{
            fontWeight: 700,
            color: '#1F2937',
            mb: 2,
          }}>
            📚 Try These Demo Projects
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.125rem' }}>
            Start with pre-made project ideas to explore different writing styles
          </Typography>
        </Box>
        <Grid container spacing={3}>
          {demoProjects.map((project, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <ModernCard
                hoverable
                floating
                onClick={() => handleStartWriting(project)}
                className={`fade-in-delay-${index + 1}`}
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  background: index % 2 === 0 ? 'rgba(255, 255, 255, 0.9)' : 'rgba(254, 247, 237, 0.9)',
                }}
              >
                <ModernCardContent>
                  <Box mb={2}>
                    <Typography variant="h6" gutterBottom sx={{
                      fontWeight: 600,
                      color: '#1F2937',
                      lineHeight: 1.3,
                    }}>
                      {project.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={2} sx={{ lineHeight: 1.6 }}>
                      {project.description}
                    </Typography>
                    <Box sx={{
                      p: 2,
                      borderRadius: 2,
                      background: 'rgba(99, 102, 241, 0.05)',
                      border: '1px solid rgba(99, 102, 241, 0.1)',
                    }}>
                      <Typography variant="body2" sx={{
                        fontStyle: 'italic',
                        fontSize: '0.8rem',
                        color: '#6B7280',
                        lineHeight: 1.5,
                      }}>
                        "{project.sample_text.substring(0, 80)}..."
                      </Typography>
                    </Box>
                  </Box>
                  <ModernButton
                    modernVariant="primary"
                    size="small"
                    startIcon={<EditIcon />}
                    fullWidth
                  >
                    Start Writing
                  </ModernButton>
                </ModernCardContent>
              </ModernCard>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Features Overview */}
      <Box mb={4}>
        <Typography variant="h4" textAlign="center" gutterBottom sx={{
          fontWeight: 700,
          color: '#1F2937',
          mb: 4,
        }}>
          ✨ What You Can Do
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <ModernCard variant="glass" hoverable sx={{ height: '100%', textAlign: 'center' }} className="fade-in-delay-1">
              <ModernCardContent>
                <Box sx={{
                  width: 64,
                  height: 64,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                }}>
                  <AIIcon sx={{ fontSize: 32, color: 'white' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  AI Writing Assistant
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  Get intelligent suggestions to improve, continue, or analyze your writing with age-appropriate guidance.
                </Typography>
              </ModernCardContent>
            </ModernCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <ModernCard variant="warm" hoverable sx={{ height: '100%', textAlign: 'center' }} className="fade-in-delay-2">
              <ModernCardContent>
                <Box sx={{
                  width: 64,
                  height: 64,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                }}>
                  <LightbulbIcon sx={{ fontSize: 32, color: '#1F2937' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Writing Prompts
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  Get creative writing prompts and guidance based on your project theme and writing goals.
                </Typography>
              </ModernCardContent>
            </ModernCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <ModernCard variant="glass" hoverable sx={{ height: '100%', textAlign: 'center' }} className="fade-in-delay-3">
              <ModernCardContent>
                <Box sx={{
                  width: 64,
                  height: 64,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #F87171 0%, #EF4444 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                }}>
                  <EditIcon sx={{ fontSize: 32, color: 'white' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Rich Text Editor
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  Write with a powerful editor that supports formatting and provides a distraction-free experience.
                </Typography>
              </ModernCardContent>
            </ModernCard>
          </Grid>
        </Grid>
      </Box>

      {/* Tips */}
      {tips.length > 0 && (
        <ModernCard variant="glass" className="fade-in-delay-3">
          <ModernCardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Box sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}>
                <Typography sx={{ fontSize: '1.25rem' }}>💡</Typography>
              </Box>
              <Typography variant="h6" fontWeight="bold">
                Tips for Guest Mode
              </Typography>
            </Box>
            <Box component="ul" sx={{ pl: 2, m: 0 }}>
              {tips.map((tip, index) => (
                <Typography component="li" variant="body2" key={index} sx={{
                  mb: 1,
                  lineHeight: 1.6,
                  color: '#374151',
                }}>
                  {tip}
                </Typography>
              ))}
            </Box>
          </ModernCardContent>
        </ModernCard>
      )}
    </Container>
  );
};

export default GuestMode;
