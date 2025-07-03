import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Chip,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AutoFixHigh as AIIcon,
  Lightbulb as LightbulbIcon,
  ExpandMore as ExpandMoreIcon,
  Home as HomeIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from 'react-query';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { debounce } from 'lodash';
import guestService from '../../services/guestService';
import toast from 'react-hot-toast';

// Quill modules configuration for guest editor
const guestQuillModules = {
  toolbar: [
    [{ 'header': [1, 2, 3, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    ['blockquote', 'code-block'],
    ['link'],
    ['clean']
  ],
};

const guestQuillFormats = [
  'header', 'bold', 'italic', 'underline', 'strike',
  'list', 'bullet', 'blockquote', 'code-block', 'link'
];

const GuestEditor = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const projectData = location.state?.projectData || { name: 'My Writing Project', description: '', sample_text: '' };
  const selectedAgeGroup = location.state?.selectedAgeGroup || 'high_school';

  const [content, setContent] = useState(projectData.sample_text || '');

  // Optimized content change handler
  const handleContentChange = useCallback((value) => {
    if (value !== content) {
      setContent(value);
    }
  }, [content]);
  const [selectedText, setSelectedText] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [aiResultType, setAiResultType] = useState('');
  const [writingPrompts, setWritingPrompts] = useState([]);

  // Fetch writing prompts
  const { data: promptsData } = useQuery(
    ['guest-writing-prompts', projectData.name, selectedAgeGroup],
    () => guestService.getWritingPrompts(projectData.name, selectedAgeGroup),
    {
      onSuccess: (data) => {
        setWritingPrompts(data.prompts || []);
      },
      onError: (error) => {
        console.error('Failed to load writing prompts:', error);
      },
    }
  );

  // AI assistance mutation
  const aiAssistanceMutation = useMutation(
    (data) => guestService.getWritingAssistance(data.text, data.type, selectedAgeGroup),
    {
      onSuccess: (data, variables) => {
        setAiResult(data.result);
        setAiResultType(variables.type);
        toast.success('AI analysis completed!');
      },
      onError: (error) => {
        console.error('AI assistance error:', error);
        
        if (error.code === 'ECONNABORTED') {
          toast.error('AI request timeout. The AI service may be busy, please try again in a moment.');
        } else if (error.response?.status === 500) {
          const errorDetail = error.response?.data?.detail || '';
          if (errorDetail.includes('quota') || errorDetail.includes('billing')) {
            toast.error('AI service quota exceeded. Please try again later.');
          } else if (errorDetail.includes('timeout')) {
            toast.error('AI service timeout. Please try with shorter text or try again later.');
          } else {
            toast.error('AI service is temporarily unavailable. Please try again.');
          }
        } else {
          toast.error('Failed to get AI assistance. Please check your connection and try again.');
        }
      },
    }
  );

  const handleAIAssistance = (type) => {
    const textToAnalyze = selectedText || content;
    if (!textToAnalyze || textToAnalyze.trim() === '' || textToAnalyze === '<p><br></p>') {
      toast.error('Please write some content first or select text to analyze.');
      return;
    }

    aiAssistanceMutation.mutate({
      text: textToAnalyze,
      type: type,
    });
  };

  const handleSaveToLocal = () => {
    const dataToSave = {
      projectName: projectData.name,
      content: content,
      timestamp: new Date().toISOString(),
      mode: 'guest'
    };
    
    localStorage.setItem(`writingway_guest_${Date.now()}`, JSON.stringify(dataToSave));
    toast.success('Content saved to browser storage!');
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([content.replace(/<[^>]*>/g, '')], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${projectData.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Content downloaded!');
  };

  // Optimized auto-save to localStorage with debouncing
  const debouncedAutoSaveRef = useRef();

  useEffect(() => {
    // Create debounced auto-save function
    debouncedAutoSaveRef.current = debounce((contentToSave) => {
      if (contentToSave && contentToSave.trim() !== '' && contentToSave !== '<p><br></p>') {
        const autoSaveData = {
          projectName: projectData.name,
          content: contentToSave,
          timestamp: new Date().toISOString(),
          mode: 'guest_autosave'
        };
        localStorage.setItem('writingway_guest_autosave', JSON.stringify(autoSaveData));
      }
    }, 5000); // Debounce auto-save to 5 seconds

    return () => {
      if (debouncedAutoSaveRef.current) {
        debouncedAutoSaveRef.current.cancel();
      }
    };
  }, [projectData.name]);

  // Trigger auto-save when content changes
  useEffect(() => {
    if (debouncedAutoSaveRef.current) {
      debouncedAutoSaveRef.current(content);
    }
  }, [content]);

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" fontWeight="bold">
              {projectData.name}
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={1}>
              <Chip label="Guest Mode" color="primary" size="small" />
              <Chip
                label={promptsData?.age_group ?
                  promptsData.age_group.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Level' :
                  'High School Level'
                }
                color="secondary"
                size="small"
              />
              <Typography variant="body2" color="text.secondary">
                Content is not saved to database
              </Typography>
            </Box>
          </Box>
          <Box>
            <Tooltip title="Back to Guest Home">
              <IconButton onClick={() => navigate('/guest')} sx={{ mr: 1 }}>
                <HomeIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Save to Browser Storage">
              <IconButton onClick={handleSaveToLocal} sx={{ mr: 1 }}>
                <SaveIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Download as Text File">
              <IconButton onClick={handleDownload}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Paper>

      <Box display="flex" gap={2} sx={{ px: 2 }}>
        {/* Main Writing Area */}
        <Box flex={2}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              📝 Writing Area
            </Typography>
            
            {/* Writing Prompts - Show when content is empty */}
            {(!content || content.trim() === '' || content === '<p><br></p>') && writingPrompts.length > 0 && (
              <Card sx={{ mb: 2, backgroundColor: '#f8f9fa' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <LightbulbIcon sx={{ mr: 1, color: '#ffa726' }} />
                    <Typography variant="h6" color="primary">
                      Writing Ideas to Get Started
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Need help getting started? Here are some high school level writing ideas for your project:
                  </Typography>
                  
                  {writingPrompts.map((prompt, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          💡 {prompt.title}
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          {prompt.guidance}
                        </Typography>
                        {prompt.example && (
                          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                            {prompt.example}
                          </Typography>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            )}
            
            <Box sx={{ minHeight: '450px', border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <ReactQuill
                value={content}
                onChange={handleContentChange}
                style={{ height: '400px' }}
                modules={guestQuillModules}
                formats={guestQuillFormats}
                placeholder="Start writing your content here..."
                preserveWhitespace={false}
              />
            </Box>
          </Paper>
        </Box>

        {/* AI Assistant Panel */}
        <Box flex={1}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🤖 AI Writing Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {promptsData?.age_group ?
                promptsData.age_group.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Level Suggestions' :
                'High School Level Suggestions'
              }
            </Typography>

            <Stack spacing={2} sx={{ mb: 3 }}>
              <Button
                variant="outlined"
                startIcon={<AIIcon />}
                onClick={() => handleAIAssistance('improve')}
                disabled={aiAssistanceMutation.isLoading}
                fullWidth
              >
                Enhance Expression
              </Button>
              <Button
                variant="outlined"
                startIcon={<AIIcon />}
                onClick={() => handleAIAssistance('continue')}
                disabled={aiAssistanceMutation.isLoading}
                fullWidth
              >
                Continue Writing
              </Button>
              <Button
                variant="outlined"
                startIcon={<AIIcon />}
                onClick={() => handleAIAssistance('structure')}
                disabled={aiAssistanceMutation.isLoading}
                fullWidth
              >
                Structure Check
              </Button>
              <Button
                variant="outlined"
                startIcon={<AIIcon />}
                onClick={() => handleAIAssistance('style')}
                disabled={aiAssistanceMutation.isLoading}
                fullWidth
              >
                Style Tips
              </Button>
              <Button
                variant="outlined"
                startIcon={<AIIcon />}
                onClick={() => handleAIAssistance('creativity')}
                disabled={aiAssistanceMutation.isLoading}
                fullWidth
              >
                Creative Ideas
              </Button>
            </Stack>

            {aiAssistanceMutation.isLoading && (
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  AI is analyzing... This may take up to 2 minutes
                </Typography>
              </Box>
            )}

            {aiResult && (
              <Paper sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                <Typography variant="subtitle2" gutterBottom>
                  AI Suggestion ({aiResultType}):
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {aiResult}
                </Typography>
              </Paper>
            )}
          </Paper>

          {/* Guest Mode Info */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Guest Mode:</strong> Your work is temporarily stored in your browser. 
              Download or copy your text to save permanently. Register to save your work and access age-appropriate suggestions.
            </Typography>
          </Alert>
        </Box>
      </Box>
    </Box>
  );
};

export default GuestEditor;
