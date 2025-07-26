import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Fade,
  Chip,
  Button,
  Tooltip
} from '@mui/material';
import {
  Lightbulb as LightbulbIcon,
  Close as CloseIcon,
  CheckCircle as AcceptIcon,
  Cancel as IgnoreIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';
import api from '../../services/api';

// Animations
const slideInUp = keyframes`
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`;

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(25, 118, 210, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0);
  }
`;

// Styled components
const SuggestionCard = styled(Paper)(({ theme, priority }) => ({
  position: 'fixed',
  bottom: theme.spacing(3),
  right: theme.spacing(3),
  width: '320px',
  maxWidth: '90vw',
  padding: theme.spacing(2),
  borderRadius: theme.spacing(2),
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  animation: `${slideInUp} 0.3s ease-out`,
  zIndex: 1300,
  border: priority === 1 ? '2px solid #ff6b6b' : 'none',
  '&::before': priority === 1 ? {
    content: '""',
    position: 'absolute',
    top: -2,
    left: -2,
    right: -2,
    bottom: -2,
    borderRadius: theme.spacing(2),
    background: 'linear-gradient(45deg, #ff6b6b, #feca57)',
    zIndex: -1,
    animation: `${pulse} 2s infinite`
  } : {}
}));

const SuggestionHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(1)
}));

const SuggestionContent = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2)
}));

const ActionButtons = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  justifyContent: 'flex-end'
}));

const CategoryChip = styled(Chip)(({ category }) => ({
  fontSize: '0.7rem',
  height: '20px',
  backgroundColor: category === 'correction' ? '#ff6b6b' : 
                   category === 'enhancement' ? '#4ecdc4' : '#feca57',
  color: 'white',
  fontWeight: 'bold'
}));

const RealtimeAIAssistant = ({ 
  text, 
  cursorPosition, 
  ageGroup = 'upper_primary',
  onTextChange,
  isEnabled = true,
  userPreferences = {}
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [isVisible, setIsVisible] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastAnalyzedText, setLastAnalyzedText] = useState('');
  const [nextCheckDelay, setNextCheckDelay] = useState(3);
  const [ignoredSuggestions, setIgnoredSuggestions] = useState(new Set());
  
  const timeoutRef = useRef(null);
  const lastAnalysisTime = useRef(0);
  const analysisCount = useRef(0);
  const sessionId = useRef(Math.random().toString(36).substr(2, 9)); // Generate unique session ID

  // Debounced analysis function
  const debouncedAnalyze = useCallback(async () => {
    if (!isEnabled || !text || text.length < 10) {
      setSuggestions([]);
      setIsVisible(false);
      return;
    }

    // Avoid analyzing the same text repeatedly
    if (text === lastAnalyzedText) {
      return;
    }

    // Rate limiting: max 1 analysis per 2 seconds
    const now = Date.now();
    if (now - lastAnalysisTime.current < 2000) {
      return;
    }

    setIsAnalyzing(true);
    lastAnalysisTime.current = now;
    analysisCount.current += 1;

    try {
      const response = await api.post('/realtime/suggestions', {
        text,
        cursor_position: cursorPosition,
        age_group: ageGroup,
        user_preferences: {
          ...userPreferences,
          analysis_count: analysisCount.current,
          session_id: sessionId.current
        }
      });

      const { suggestions: newSuggestions, should_show, next_check_delay } = response.data;
      
      // Filter out ignored suggestions
      const filteredSuggestions = newSuggestions.filter(
        suggestion => !ignoredSuggestions.has(suggestion.id)
      );

      setSuggestions(filteredSuggestions);
      setIsVisible(should_show && filteredSuggestions.length > 0);
      setNextCheckDelay(next_check_delay);
      setLastAnalyzedText(text);

      console.log('📝 Real-time analysis:', {
        suggestions: filteredSuggestions.length,
        should_show,
        next_check_delay,
        analysis_time: response.data.analysis_time_ms
      });

    } catch (error) {
      console.error('❌ Real-time suggestion error:', error);
      setSuggestions([]);
      setIsVisible(false);
    } finally {
      setIsAnalyzing(false);
    }
  }, [text, cursorPosition, ageGroup, isEnabled, userPreferences, lastAnalyzedText, ignoredSuggestions]);

  // Set up debounced analysis
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Debounce delay based on text length and typing speed
    const debounceDelay = text.length > 100 ? 3000 : 2500;

    timeoutRef.current = setTimeout(() => {
      debouncedAnalyze();
    }, debounceDelay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text, debouncedAnalyze]);

  // Auto-hide suggestions after a delay
  useEffect(() => {
    if (isVisible && suggestions.length > 0) {
      const hideTimeout = setTimeout(() => {
        setIsVisible(false);
      }, 8000); // Show for 8 seconds

      return () => clearTimeout(hideTimeout);
    }
  }, [isVisible, suggestions]);

  const handleAcceptSuggestion = (suggestion) => {
    console.log('✅ Accepted suggestion:', suggestion.type);
    
    // Apply suggestion if it has specific text
    if (suggestion.suggestion && onTextChange) {
      onTextChange(suggestion.suggestion);
    }

    // Hide current suggestions
    setIsVisible(false);
    setSuggestions([]);
    
    // Track acceptance for learning
    // TODO: Send analytics to backend
  };

  const handleIgnoreSuggestion = (suggestion) => {
    console.log('❌ Ignored suggestion:', suggestion.type);
    
    // Add to ignored list
    setIgnoredSuggestions(prev => new Set([...prev, suggestion.id]));
    
    // Remove from current suggestions
    setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
    
    // Hide if no more suggestions
    if (suggestions.length <= 1) {
      setIsVisible(false);
    }
  };

  const handleDismissAll = () => {
    setIsVisible(false);
    setSuggestions([]);
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'correction':
        return '🔧';
      case 'enhancement':
        return '✨';
      case 'inspiration':
        return '💡';
      default:
        return '📝';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 1:
        return '#ff6b6b'; // High priority - red
      case 2:
        return '#feca57'; // Medium priority - yellow
      default:
        return '#4ecdc4'; // Low priority - teal
    }
  };

  if (!isEnabled || !isVisible || suggestions.length === 0) {
    return null;
  }

  const currentSuggestion = suggestions[0]; // Show only the highest priority suggestion

  return (
    <Fade in={isVisible} timeout={300}>
      <SuggestionCard priority={currentSuggestion.priority}>
        <SuggestionHeader>
          <Box display="flex" alignItems="center" gap={1}>
            <LightbulbIcon sx={{ color: '#feca57', fontSize: '1.2rem' }} />
            <Typography variant="subtitle2" fontWeight="bold">
              Writing Tip
            </Typography>
            <CategoryChip 
              label={getCategoryIcon(currentSuggestion.category)}
              category={currentSuggestion.category}
              size="small"
            />
          </Box>
          <Tooltip title="Dismiss">
            <IconButton 
              size="small" 
              onClick={handleDismissAll}
              sx={{ color: 'white', opacity: 0.7 }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </SuggestionHeader>

        <SuggestionContent>
          <Typography variant="body2" sx={{ lineHeight: 1.4 }}>
            {currentSuggestion.message}
          </Typography>
          
          {currentSuggestion.suggestion && (
            <Box 
              mt={1} 
              p={1} 
              sx={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)', 
                borderRadius: 1,
                fontSize: '0.85rem',
                fontStyle: 'italic'
              }}
            >
              "{currentSuggestion.suggestion}"
            </Box>
          )}
        </SuggestionContent>

        <ActionButtons>
          <Button
            size="small"
            variant="outlined"
            startIcon={<IgnoreIcon />}
            onClick={() => handleIgnoreSuggestion(currentSuggestion)}
            sx={{ 
              color: 'white', 
              borderColor: 'rgba(255, 255, 255, 0.5)',
              '&:hover': {
                borderColor: 'white',
                backgroundColor: 'rgba(255, 255, 255, 0.1)'
              }
            }}
          >
            Skip
          </Button>
          
          {currentSuggestion.suggestion && (
            <Button
              size="small"
              variant="contained"
              startIcon={<AcceptIcon />}
              onClick={() => handleAcceptSuggestion(currentSuggestion)}
              sx={{ 
                backgroundColor: '#4ecdc4',
                '&:hover': {
                  backgroundColor: '#45b7aa'
                }
              }}
            >
              Apply
            </Button>
          )}
        </ActionButtons>

        {suggestions.length > 1 && (
          <Box mt={1}>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              +{suggestions.length - 1} more suggestion{suggestions.length > 2 ? 's' : ''}
            </Typography>
          </Box>
        )}
      </SuggestionCard>
    </Fade>
  );
};

export default RealtimeAIAssistant;
