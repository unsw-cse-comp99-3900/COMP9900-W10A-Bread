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

const Settings = () => {
  const queryClient = useQueryClient();
  const [showApiKeys, setShowApiKeys] = useState(false);

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
      onSuccess: () => {
        queryClient.invalidateQueries('settings');
        toast.success('Settings saved successfully!');
      },
      onError: () => {
        toast.error('Failed to save settings');
      },
    }
  );

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
      ai_settings: {
        openai_api_key: '',
        anthropic_api_key: '',
        preferred_provider: 'openai',
      },
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
        ai_settings: {
          openai_api_key: settings.ai_settings?.openai_api_key || '',
          anthropic_api_key: settings.ai_settings?.anthropic_api_key || '',
          preferred_provider: settings.ai_settings?.preferred_provider || 'openai',
        },
      });
    }
  }, [settings, reset]);

  const onSubmit = (data) => {
    updateSettingsMutation.mutate(data);
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
            AI Settings
          </Typography>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            Configure your AI service providers. API keys are stored securely and only used for your writing assistance.
          </Alert>

          <Controller
            name="ai_settings.preferred_provider"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Preferred AI Provider</InputLabel>
                <Select {...field} label="Preferred AI Provider">
                  <MenuItem value="openai">OpenAI (GPT)</MenuItem>
                  <MenuItem value="anthropic">Anthropic (Claude)</MenuItem>
                </Select>
              </FormControl>
            )}
          />

          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              onClick={() => setShowApiKeys(!showApiKeys)}
              sx={{ mb: 2 }}
            >
              {showApiKeys ? 'Hide' : 'Show'} API Keys
            </Button>
          </Box>

          {showApiKeys && (
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Controller
                name="ai_settings.openai_api_key"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="OpenAI API Key"
                    type="password"
                    fullWidth
                    placeholder="sk-..."
                    helperText="Get your API key from https://platform.openai.com/api-keys"
                  />
                )}
              />

              <Controller
                name="ai_settings.anthropic_api_key"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Anthropic API Key"
                    type="password"
                    fullWidth
                    placeholder="sk-ant-..."
                    helperText="Get your API key from https://console.anthropic.com/"
                  />
                )}
              />
            </Box>
          )}
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
