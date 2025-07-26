import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';

import api from '../../services/api';
import { aiService } from '../../services/aiService';
import { useAuthStore } from '../../stores/authStore';
import { useThemeContext } from '../../contexts/ThemeContext';

const Settings = () => {
  const queryClient = useQueryClient();
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [ageGroups, setAgeGroups] = useState([]);
  const { user, updateUser } = useAuthStore();
  const { updateSettings: updateThemeSettings } = useThemeContext();

  // Fetch user settings
  const { data: settings, isLoading } = useQuery(
    'settings',
    async () => {
      const response = await api.get('/settings/');
      return response.data;
    },
    {
      onError: () => {
        toast.error('Failed to load settings');
      },
    }
  );

  // Update settings mutation
  const updateSettingsMutation = useMutation(
    async (data) => {
      const response = await api.put('/settings/', data);
      return response.data;
    },
    {
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries('settings');
        // Update theme context with new settings
        updateThemeSettings({
          theme: variables.theme,
          fontSize: variables.font_size,
        });
        toast.success('Settings saved successfully!');
      },
      onError: () => {
        toast.error('Failed to save settings');
      },
    }
  );

  // Update user profile mutation
  const updateUserMutation = useMutation(
    async (userData) => {
      const response = await api.put('/auth/profile', userData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        updateUser(data);
        toast.success('Profile updated successfully!');
      },
      onError: () => {
        toast.error('Failed to update profile');
      },
    }
  );

  // Fetch age groups
  React.useEffect(() => {
    const fetchAgeGroups = async () => {
      try {
        const response = await aiService.getAgeGroups();
        setAgeGroups(response.age_groups || []);
      } catch (error) {
        console.error('Failed to fetch age groups:', error);
      }
    };

    fetchAgeGroups();
  }, []);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: {
      theme: 'light',
      language: 'en',
      font_size: 14,
      auto_save: true,
      age_group: '',
    },
  });

  // Reset form when settings are loaded
  React.useEffect(() => {
    if (settings) {
      reset({
        theme: settings.theme || 'light',
        language: settings.language || 'en',
        font_size: settings.font_size || 14,
        auto_save: settings.auto_save !== undefined ? settings.auto_save : true,
        age_group: user?.age_group || '',
      });
    }
  }, [settings, user, reset]);

  const onSubmit = (data) => {
    // Extract age_group from data for user profile update
    const { age_group, ...settingsData } = data;

    // Update settings
    updateSettingsMutation.mutate(settingsData);

    // Update user profile if age_group changed
    if (age_group !== user?.age_group) {
      updateUserMutation.mutate({ age_group });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Appearance
          </Typography>
          
          <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' } }}>
            <Controller
              name="theme"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>Theme</InputLabel>
                  <Select {...field} label="Theme">
                    <MenuItem value="light">Light</MenuItem>
                    <MenuItem value="dark">Dark</MenuItem>
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="language"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>Language</InputLabel>
                  <Select {...field} label="Language">
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Español</MenuItem>
                    <MenuItem value="fr">Français</MenuItem>
                    <MenuItem value="de">Deutsch</MenuItem>
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="age_group"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>Age Group</InputLabel>
                  <Select {...field} label="Age Group">
                    <MenuItem value="">
                      <em>Select your age group</em>
                    </MenuItem>
                    {ageGroups.map((group) => (
                      <MenuItem key={group.value} value={group.value}>
                        {group.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="font_size"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Font Size"
                  type="number"
                  inputProps={{ min: 10, max: 24 }}
                  fullWidth
                />
              )}
            />
          </Box>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Editor Settings
          </Typography>
          
          <Controller
            name="auto_save"
            control={control}
            render={({ field: { value, onChange } }) => (
              <FormControlLabel
                control={
                  <Switch
                    checked={value}
                    onChange={(e) => onChange(e.target.checked)}
                  />
                }
                label="Auto-save documents"
              />
            )}
          />
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            AI Writing Assistant
          </Typography>

          <Alert severity="info" sx={{ mb: 2 }}>
            Our AI writing assistant automatically selects the best language model for each task to provide you with optimal writing support. The system intelligently switches between different AI services based on your writing needs.
          </Alert>

          <Box sx={{
            p: 2,
            bgcolor: 'background.paper',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider'
          }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Smart AI Selection:</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Writing prompts and creative suggestions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Story analysis and improvement recommendations
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Age-appropriate writing guidance
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Intelligent fallback system for reliable service
            </Typography>
          </Box>
        </Paper>

        <Box display="flex" justifyContent="flex-end">
          <Button
            type="submit"
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!isDirty || updateSettingsMutation.isLoading}
          >
            {updateSettingsMutation.isLoading ? <CircularProgress size={20} /> : 'Save Settings'}
          </Button>
        </Box>
      </form>
    </Container>
  );
};

export default Settings;
