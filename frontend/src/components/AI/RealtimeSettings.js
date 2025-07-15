import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Divider,
  Button,
  Alert,
  Collapse
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Speed as SpeedIcon,
  Category as CategoryIcon,
  Psychology as PsychologyIcon,
  Save as SaveIcon
} from '@mui/icons-material';

const RealtimeSettings = ({ 
  settings = {}, 
  onSettingsChange,
  ageGroup = 'late_primary' 
}) => {
  const [localSettings, setLocalSettings] = useState({
    enabled: true,
    frequency: 'medium', // 'low', 'medium', 'high'
    suggestionTypes: ['vocabulary', 'structure', 'creativity', 'grammar'],
    showPriority: 'all', // 'high', 'medium', 'all'
    autoHideDelay: 8, // seconds
    maxSuggestionsPerSession: 10,
    focusMode: false, // Disable suggestions during rapid typing
    ...settings
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setLocalSettings(prev => ({ ...prev, ...settings }));
  }, [settings]);

  const handleSettingChange = (key, value) => {
    setLocalSettings(prev => {
      const newSettings = { ...prev, [key]: value };
      setHasChanges(true);
      return newSettings;
    });
  };

  const handleSuggestionTypeToggle = (type) => {
    setLocalSettings(prev => {
      const currentTypes = prev.suggestionTypes || [];
      const newTypes = currentTypes.includes(type)
        ? currentTypes.filter(t => t !== type)
        : [...currentTypes, type];
      
      setHasChanges(true);
      return { ...prev, suggestionTypes: newTypes };
    });
  };

  const handleSaveSettings = () => {
    if (onSettingsChange) {
      onSettingsChange(localSettings);
    }
    setHasChanges(false);
    
    // Save to localStorage for persistence
    localStorage.setItem('realtimeAISettings', JSON.stringify(localSettings));
  };

  const getFrequencyDescription = (frequency) => {
    switch (frequency) {
      case 'low':
        return 'Suggestions every 8-10 seconds when appropriate';
      case 'medium':
        return 'Suggestions every 4-6 seconds when appropriate';
      case 'high':
        return 'Suggestions every 2-3 seconds when appropriate';
      default:
        return '';
    }
  };

  const suggestionTypeInfo = {
    vocabulary: {
      icon: '📚',
      label: 'Vocabulary',
      description: 'Word choice and descriptive language suggestions'
    },
    structure: {
      icon: '🏗️',
      label: 'Structure',
      description: 'Sentence flow and paragraph organization'
    },
    creativity: {
      icon: '🎨',
      label: 'Creativity',
      description: 'Creative ideas and emotional expression'
    },
    grammar: {
      icon: '✏️',
      label: 'Grammar',
      description: 'Basic grammar and punctuation corrections'
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <AutoAwesomeIcon color="primary" />
        <Typography variant="h6">
          Real-time AI Writing Assistant
        </Typography>
      </Box>

      {/* Main Enable/Disable */}
      <Box mb={3}>
        <FormControlLabel
          control={
            <Switch
              checked={localSettings.enabled}
              onChange={(e) => handleSettingChange('enabled', e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body1" fontWeight="medium">
                Enable Real-time Suggestions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Get writing tips automatically as you type
              </Typography>
            </Box>
          }
        />
      </Box>

      <Collapse in={localSettings.enabled}>
        {/* Suggestion Frequency */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <SpeedIcon fontSize="small" color="action" />
            <Typography variant="subtitle2" fontWeight="medium">
              Suggestion Frequency
            </Typography>
          </Box>
          
          <FormControl fullWidth size="small">
            <Select
              value={localSettings.frequency}
              onChange={(e) => handleSettingChange('frequency', e.target.value)}
            >
              <MenuItem value="low">Low - Less frequent suggestions</MenuItem>
              <MenuItem value="medium">Medium - Balanced suggestions</MenuItem>
              <MenuItem value="high">High - More frequent suggestions</MenuItem>
            </Select>
          </FormControl>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {getFrequencyDescription(localSettings.frequency)}
          </Typography>
        </Box>

        {/* Suggestion Types */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <CategoryIcon fontSize="small" color="action" />
            <Typography variant="subtitle2" fontWeight="medium">
              Suggestion Types
            </Typography>
          </Box>
          
          <Box display="flex" flexWrap="wrap" gap={1}>
            {Object.entries(suggestionTypeInfo).map(([type, info]) => (
              <Chip
                key={type}
                icon={<span>{info.icon}</span>}
                label={info.label}
                variant={localSettings.suggestionTypes?.includes(type) ? "filled" : "outlined"}
                color={localSettings.suggestionTypes?.includes(type) ? "primary" : "default"}
                onClick={() => handleSuggestionTypeToggle(type)}
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Select which types of suggestions you'd like to receive
          </Typography>
        </Box>

        {/* Priority Filter */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <PsychologyIcon fontSize="small" color="action" />
            <Typography variant="subtitle2" fontWeight="medium">
              Show Suggestions
            </Typography>
          </Box>
          
          <FormControl fullWidth size="small">
            <Select
              value={localSettings.showPriority}
              onChange={(e) => handleSettingChange('showPriority', e.target.value)}
            >
              <MenuItem value="high">High Priority Only</MenuItem>
              <MenuItem value="medium">High & Medium Priority</MenuItem>
              <MenuItem value="all">All Suggestions</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Advanced Settings */}
        <Divider sx={{ my: 2 }} />
        
        <Button
          variant="text"
          onClick={() => setShowAdvanced(!showAdvanced)}
          sx={{ mb: 2 }}
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
        </Button>

        <Collapse in={showAdvanced}>
          <Box space={2}>
            {/* Auto-hide Delay */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                Auto-hide Delay: {localSettings.autoHideDelay} seconds
              </Typography>
              <Slider
                value={localSettings.autoHideDelay}
                onChange={(e, value) => handleSettingChange('autoHideDelay', value)}
                min={3}
                max={15}
                step={1}
                marks={[
                  { value: 3, label: '3s' },
                  { value: 8, label: '8s' },
                  { value: 15, label: '15s' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            {/* Focus Mode */}
            <Box mb={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={localSettings.focusMode}
                    onChange={(e) => handleSettingChange('focusMode', e.target.checked)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2" fontWeight="medium">
                      Focus Mode
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Pause suggestions during rapid typing
                    </Typography>
                  </Box>
                }
              />
            </Box>

            {/* Max Suggestions */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                Max Suggestions per Session: {localSettings.maxSuggestionsPerSession}
              </Typography>
              <Slider
                value={localSettings.maxSuggestionsPerSession}
                onChange={(e, value) => handleSettingChange('maxSuggestionsPerSession', value)}
                min={5}
                max={25}
                step={5}
                marks={[
                  { value: 5, label: '5' },
                  { value: 15, label: '15' },
                  { value: 25, label: '25' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>
          </Box>
        </Collapse>

        {/* Age Group Info */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Age Group: {ageGroup.replace('_', ' ').toUpperCase()}</strong>
            <br />
            Suggestions are automatically adapted to be age-appropriate and match your developmental stage.
          </Typography>
        </Alert>

        {/* Save Button */}
        {hasChanges && (
          <Box mt={3} display="flex" justifyContent="flex-end">
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSaveSettings}
              color="primary"
            >
              Save Settings
            </Button>
          </Box>
        )}
      </Collapse>
    </Paper>
  );
};

export default RealtimeSettings;
