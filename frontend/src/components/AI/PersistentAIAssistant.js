import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Fade,
  Chip,
  Button,
  Tooltip,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Lightbulb as LightbulbIcon,
  AutoAwesome as AutoAwesomeIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  DragIndicator as DragIndicatorIcon
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';
import api, { realtimeApi } from '../../services/api';

// Animations
const glow = keyframes`
  0% {
    box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
  }
  100% {
    box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
  }
`;

const slideIn = keyframes`
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

// Styled components with project theme colors
const AssistantContainer = styled(Card)(({ theme, isVisible, isDragging }) => ({
  position: 'fixed',
  width: '350px',
  maxWidth: '90vw',
  zIndex: 1200,
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  borderRadius: theme.spacing(3),
  border: '2px solid rgba(255, 255, 255, 0.2)',
  backdropFilter: 'blur(10px)',
  animation: isVisible && !isDragging ? `${slideIn} 0.5s ease-out` : 'none',
  transition: isDragging ? 'none' : 'all 0.3s ease',
  transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
  opacity: isVisible ? 1 : 0,
  cursor: isDragging ? 'grabbing' : 'default',
  userSelect: 'none',
  '&:hover': {
    animation: !isDragging ? `${glow} 2s infinite` : 'none',
  }
}));

const AssistantHeader = styled(Box)(({ theme, isDragHandle }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: `${theme.spacing(3)} ${theme.spacing(3)} 0 0`,
  borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
  cursor: isDragHandle ? 'grab' : 'default',
  '&:active': {
    cursor: isDragHandle ? 'grabbing' : 'default',
  }
}));

const SuggestionContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing(2),
  color: 'white',
  '& .MuiTypography-root': {
    color: 'white',
    textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
    lineHeight: 1.6
  }
}));

const ActionButtons = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  padding: theme.spacing(2),
  paddingTop: 0,
  justifyContent: 'flex-end'
}));

const StatusIndicator = styled(Box)(({ theme, status }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1, 2),
  borderRadius: theme.spacing(1),
  backgroundColor: status === 'thinking' ? 'rgba(255, 193, 7, 0.2)' : 
                   status === 'ready' ? 'rgba(76, 175, 80, 0.2)' : 
                   'rgba(158, 158, 158, 0.2)',
  border: `1px solid ${status === 'thinking' ? '#FFC107' : 
                       status === 'ready' ? '#4CAF50' : 
                       '#9E9E9E'}`,
  '& .MuiTypography-root': {
    fontSize: '0.75rem',
    fontWeight: 'bold',
    color: status === 'thinking' ? '#FFC107' : 
           status === 'ready' ? '#4CAF50' : 
           '#9E9E9E'
  }
}));

const PersistentAIAssistant = ({
  text,
  cursorPosition,
  ageGroup = 'upper_primary',
  isEnabled = true,
  userPreferences = {}
}) => {
  const [currentSuggestion, setCurrentSuggestion] = useState(null);
  const [isVisible, setIsVisible] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [status, setStatus] = useState('ready'); // 'ready', 'thinking', 'idle'
  const [lastAnalyzedText, setLastAnalyzedText] = useState('');
  const [analysisCount, setAnalysisCount] = useState(0);

  // Dragging state
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState(() => {
    // Load saved position from localStorage or use default
    const saved = localStorage.getItem('ai-assistant-position');
    return saved ? JSON.parse(saved) : { x: window.innerWidth - 370, y: 80 };
  });

  const timeoutRef = useRef(null);
  const lastAnalysisTime = useRef(0);
  const sessionId = useRef(Math.random().toString(36).substr(2, 9));
  const dragRef = useRef({ startX: 0, startY: 0, startPosX: 0, startPosY: 0 });

  // Helper function to get current paragraph context
  const getCurrentParagraph = (text, position) => {
    const beforeCursor = text.substring(0, position);
    const afterCursor = text.substring(position);

    // Find paragraph boundaries
    const lastParagraphBreak = Math.max(
      beforeCursor.lastIndexOf('\n\n'),
      beforeCursor.lastIndexOf('</p>'),
      0
    );

    const nextParagraphBreak = Math.min(
      afterCursor.indexOf('\n\n') !== -1 ? position + afterCursor.indexOf('\n\n') : text.length,
      afterCursor.indexOf('<p>') !== -1 ? position + afterCursor.indexOf('<p>') : text.length,
      text.length
    );

    return text.substring(lastParagraphBreak, nextParagraphBreak).trim();
  };

  // Debounced analysis function
  const debouncedAnalyze = useCallback(async () => {
    if (!isEnabled || !text || text.length < 15) {
      setCurrentSuggestion(null);
      setStatus('idle');
      return;
    }

    // Avoid analyzing the same text repeatedly (but allow retry if no suggestion was generated)
    if (text === lastAnalyzedText && currentSuggestion) {
      console.log('🔄 Skipping analysis - same text and suggestion exists');
      return;
    }

    // Rate limiting: max 1 analysis per 3 seconds
    const now = Date.now();
    if (now - lastAnalysisTime.current < 3000) {
      return;
    }

    setIsAnalyzing(true);
    setStatus('thinking');
    lastAnalysisTime.current = now;
    setAnalysisCount(prev => prev + 1);

    // Set this early to prevent duplicate requests
    setLastAnalyzedText(text);

    try {
      // Get text before and after cursor for better context
      const textBeforeCursor = text.substring(0, cursorPosition);
      const textAfterCursor = text.substring(cursorPosition);
      const currentParagraph = getCurrentParagraph(text, cursorPosition);

      const response = await realtimeApi.post('/realtime/suggestions', {
        text,
        cursor_position: cursorPosition,
        text_before_cursor: textBeforeCursor,
        text_after_cursor: textAfterCursor,
        current_paragraph: currentParagraph,
        age_group: ageGroup,
        context: "writing_story",
        user_preferences: {
          ...userPreferences,
          analysis_count: analysisCount,
          session_id: sessionId.current,
          writing_context: {
            total_words: text.split(' ').length,
            current_position: cursorPosition,
            is_at_end: cursorPosition >= text.length - 5
          }
        }
      });

      const { suggestions, should_show } = response.data;

      console.log('🔍 Debug - API Response:', {
        suggestions,
        should_show,
        suggestions_length: suggestions.length,
        first_suggestion: suggestions[0],
        analysis_time: response.data.analysis_time_ms
      });

      if (should_show && suggestions.length > 0) {
        console.log('✅ Setting suggestion:', suggestions[0]);
        setCurrentSuggestion(suggestions[0]);
        setStatus('ready');
      } else {
        console.log('❌ No suggestion to show:', { should_show, suggestions_length: suggestions.length });
        setCurrentSuggestion(null);
        setStatus('idle');
      }

      console.log('🤖 AI suggestion generated:', {
        suggestion: suggestions[0]?.message,
        analysis_time: response.data.analysis_time_ms
      });

    } catch (error) {
      console.error('❌ AI suggestion error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setCurrentSuggestion(null);
      setStatus('idle');
    } finally {
      setIsAnalyzing(false);
    }
  }, [text, cursorPosition, ageGroup, isEnabled, userPreferences, lastAnalyzedText, analysisCount, currentSuggestion]);

  // Set up debounced analysis
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Debounce delay based on text length - reduced for better UX
    const debounceDelay = text.length > 100 ? 2000 : 1500;

    timeoutRef.current = setTimeout(() => {
      debouncedAnalyze();
    }, debounceDelay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text, debouncedAnalyze]);

  const handleRefresh = () => {
    setLastAnalyzedText(''); // Force re-analysis
    debouncedAnalyze();
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  // Dragging functionality
  const handleMouseDown = (e) => {
    if (e.target.closest('.drag-handle')) {
      setIsDragging(true);
      dragRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        startPosX: position.x,
        startPosY: position.y
      };

      // Prevent text selection during drag
      e.preventDefault();
      document.body.style.userSelect = 'none';
    }
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;

    const deltaX = e.clientX - dragRef.current.startX;
    const deltaY = e.clientY - dragRef.current.startY;

    const newX = Math.max(0, Math.min(
      window.innerWidth - 350,
      dragRef.current.startPosX + deltaX
    ));
    const newY = Math.max(0, Math.min(
      window.innerHeight - 200,
      dragRef.current.startPosY + deltaY
    ));

    setPosition({ x: newX, y: newY });
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(false);
      document.body.style.userSelect = '';

      // Save position to localStorage
      localStorage.setItem('ai-assistant-position', JSON.stringify(position));
    }
  }, [isDragging, position]);

  // Add global mouse event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const getStatusText = () => {
    switch (status) {
      case 'thinking':
        return 'AI is thinking...';
      case 'ready':
        return 'Suggestion ready';
      case 'idle':
        return 'Waiting for content';
      default:
        return 'Ready';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'thinking':
        return <AutoAwesomeIcon sx={{ fontSize: '1rem', animation: 'spin 1s linear infinite' }} />;
      case 'ready':
        return <PsychologyIcon sx={{ fontSize: '1rem' }} />;
      default:
        return <LightbulbIcon sx={{ fontSize: '1rem' }} />;
    }
  };

  if (!isEnabled) {
    return null;
  }

  return (
    <>
      {/* Toggle button when hidden */}
      {!isVisible && (
        <Tooltip title="Show AI Writing Assistant">
          <IconButton
            onClick={toggleVisibility}
            sx={{
              position: 'fixed',
              left: position.x + 10,
              top: position.y + 10,
              zIndex: 1201,
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': {
                backgroundColor: 'primary.dark',
              }
            }}
          >
            <VisibilityIcon />
          </IconButton>
        </Tooltip>
      )}

      <AssistantContainer
        isVisible={isVisible}
        isDragging={isDragging}
        onMouseDown={handleMouseDown}
        style={{
          left: position.x,
          top: position.y,
        }}
      >
        <AssistantHeader isDragHandle className="drag-handle">
          <Box display="flex" alignItems="center" gap={1}>
            <DragIndicatorIcon sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '1.2rem' }} />
            <LightbulbIcon sx={{ color: '#FCD34D', fontSize: '1.5rem' }} />
            <Typography variant="h6" fontWeight="bold" color="white">
              AI Writing Assistant
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Refresh suggestion">
              <IconButton
                size="small"
                onClick={handleRefresh}
                disabled={isAnalyzing}
                sx={{ color: 'white', opacity: 0.8 }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Hide assistant">
              <IconButton
                size="small"
                onClick={toggleVisibility}
                sx={{ color: 'white', opacity: 0.8 }}
              >
                <VisibilityOffIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </AssistantHeader>

        <SuggestionContent>
          <StatusIndicator status={status}>
            {getStatusIcon()}
            <Typography variant="caption">
              {getStatusText()}
            </Typography>
          </StatusIndicator>

          <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.2)' }} />

          {currentSuggestion ? (
            <Box>
              <Typography variant="body1" sx={{
                fontSize: '1rem',
                fontWeight: 500,
                marginBottom: 1
              }}>
                💡 Writing Tip:
              </Typography>
              <Typography variant="body2" sx={{
                fontSize: '0.95rem',
                lineHeight: 1.6,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                padding: 2,
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.2)'
              }}>
                {currentSuggestion.message}
              </Typography>
              {/* Debug info */}
              <Typography variant="caption" sx={{
                fontSize: '0.7rem',
                opacity: 0.7,
                mt: 1,
                display: 'block'
              }}>
                Debug: {currentSuggestion.type} | {currentSuggestion.id}
              </Typography>
              
              <Chip 
                label={`Age: ${ageGroup.replace('_', ' ')}`}
                size="small"
                sx={{ 
                  mt: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  fontSize: '0.7rem'
                }}
              />
            </Box>
          ) : (
            <Box textAlign="center" py={2}>
              <Typography variant="body2" sx={{ 
                opacity: 0.8,
                fontStyle: 'italic'
              }}>
                {text.length < 15 
                  ? "Start writing to get AI suggestions..." 
                  : "Keep writing for more suggestions!"}
              </Typography>
            </Box>
          )}
        </SuggestionContent>
      </AssistantContainer>
    </>
  );
};

export default PersistentAIAssistant;
