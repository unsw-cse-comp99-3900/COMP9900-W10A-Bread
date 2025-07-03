import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Fab,
  Chip,
  Stack,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Chat as ChatIcon,
  AutoFixHigh as AIIcon,
  ExpandMore as ExpandMoreIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { debounce } from 'lodash';
import toast from 'react-hot-toast';

import projectService from '../../services/projectService';
import aiService from '../../services/aiService';
import AIAssistant from '../../components/AI/AIAssistant';
import { useAuthStore } from '../../stores/authStore';

// Quill modules configuration - moved outside component to prevent recreation
const quillModules = {
  toolbar: [
    [{ 'header': [1, 2, 3, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    [{ 'indent': '-1'}, { 'indent': '+1' }],
    ['link'],
    ['clean']
  ],
};

// Quill formats configuration
const quillFormats = [
  'header', 'bold', 'italic', 'underline', 'strike',
  'list', 'bullet', 'indent', 'link'
];

const DocumentEditor = () => {
  const { projectId, documentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [aiAssistantOpen, setAiAssistantOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [aiResultType, setAiResultType] = useState('');
  const [writingPrompts, setWritingPrompts] = useState([]);

  // Fetch document
  const { data: document, isLoading } = useQuery(
    ['document', documentId],
    () => projectService.getDocument(documentId),
    {
      onSuccess: (data) => {
        setTitle(data.title);
        setContent(data.content || '');
      },
      onError: () => {
        toast.error('Failed to load document');
        navigate(`/project/${projectId}`);
      },
    }
  );

  // Fetch writing prompts
  const { data: promptsData } = useQuery(
    ['writing-prompts', projectId],
    () => aiService.getWritingPrompts(projectId),
    {
      onSuccess: (data) => {
        setWritingPrompts(data.prompts || []);
      },
      onError: (error) => {
        console.error('Failed to load writing prompts:', error);
      },
    }
  );

  // Save document mutation with optimized success handling
  const saveDocumentMutation = useMutation(
    (data) => projectService.updateDocument(documentId, data),
    {
      onSuccess: (response, variables) => {
        // Only invalidate queries for manual saves, not auto-saves
        // This prevents unnecessary re-fetching during typing
        if (variables.isManualSave) {
          queryClient.invalidateQueries(['document', documentId]);
          toast.success('Document saved!');
        }
        setHasUnsavedChanges(false);
      },
      onError: (error, variables) => {
        if (variables.isManualSave) {
          toast.error('Failed to save document');
        }
        console.error('Save error:', error);
      },
    }
  );

  // AI assistance mutation
  const aiAssistanceMutation = useMutation(
    (data) => aiService.getWritingAssistance(data.text, data.type, projectId, user?.age_group),
    {
      onSuccess: (data, variables) => {
        // Display AI result in separate panel
        setAiResult(data.result);
        setAiResultType(variables.type);
        toast.success('AI analysis completed!');
      },
      onError: (error) => {
        console.error('AI assistance error:', error);

        // 提供更详细的错误信息
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

  // Auto-save functionality with improved performance
  const debouncedSaveRef = useRef();

  // Create stable debounced save function
  useEffect(() => {
    debouncedSaveRef.current = debounce((titleToSave, contentToSave) => {
      // Only save if there are actual changes and content exists
      if (titleToSave && contentToSave && contentToSave.trim() !== '' && contentToSave !== '<p><br></p>') {
        saveDocumentMutation.mutate({
          title: titleToSave,
          content: contentToSave,
          isManualSave: false // Mark as auto-save
        });
      }
    }, 3000); // Increased debounce time to 3 seconds

    // Cleanup function
    return () => {
      if (debouncedSaveRef.current) {
        debouncedSaveRef.current.cancel();
      }
    };
  }, [saveDocumentMutation]);

  // Auto-save effect - only triggers when content actually changes
  useEffect(() => {
    if (hasUnsavedChanges && title && content && debouncedSaveRef.current) {
      debouncedSaveRef.current(title, content);
    }
  }, [title, content, hasUnsavedChanges]);

  const handleTitleChange = useCallback((e) => {
    const newTitle = e.target.value;
    // Only update if title actually changed
    if (newTitle !== title) {
      setTitle(newTitle);
      setHasUnsavedChanges(true);
    }
  }, [title]);

  const handleContentChange = useCallback((value) => {
    // Only update if content actually changed
    if (value !== content) {
      setContent(value);
      setHasUnsavedChanges(true);
    }
  }, [content]);

  const handleManualSave = () => {
    // Cancel any pending auto-save before manual save
    if (debouncedSaveRef.current) {
      debouncedSaveRef.current.cancel();
    }
    saveDocumentMutation.mutate({
      title,
      content,
      isManualSave: true // Mark as manual save
    });
  };

  const handleAIAssistance = (type) => {
    const textToAnalyze = selectedText || content;
    if (!textToAnalyze.trim()) {
      toast.error('Please select some text or write content first');
      return;
    }
    aiAssistanceMutation.mutate({ text: textToAnalyze, type });
  };

  const handleApplyAIResult = () => {
    if (!aiResult) return;

    if (aiResultType === 'continue') {
      // For continue, append to the end
      setContent(prev => prev + '\n\n' + aiResult);
    } else if (aiResultType === 'improve' && selectedText) {
      // For improve, replace selected text if any
      setContent(prev => prev.replace(selectedText, aiResult));
    } else {
      // For other types or no selection, append to the end
      setContent(prev => prev + '\n\n' + aiResult);
    }

    setHasUnsavedChanges(true);
    toast.success('AI suggestion applied to document!');
  };

  const handleClearAIResult = () => {
    setAiResult('');
    setAiResultType('');
  };



  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3, maxWidth: '100%' }}>
      <Paper sx={{ p: 3, minHeight: 'calc(100vh - 200px)' }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box flex={1}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Document title..."
              value={title}
              onChange={handleTitleChange}
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontSize: '1.5rem',
                  fontWeight: 'bold',
                },
              }}
            />
          </Box>
          <Box ml={2}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleManualSave}
              disabled={saveDocumentMutation.isLoading || !hasUnsavedChanges}
            >
              {saveDocumentMutation.isLoading ? <CircularProgress size={20} /> : 'Save'}
            </Button>
          </Box>
        </Box>

        {/* Status indicators */}
        <Stack direction="row" spacing={1} mb={2}>
          {hasUnsavedChanges && (
            <Chip label="Unsaved changes" color="warning" size="small" />
          )}
          {saveDocumentMutation.isLoading && (
            <Chip label="Saving..." color="info" size="small" />
          )}
        </Stack>

        {/* AI Assistance Buttons */}
        <Stack direction="row" spacing={1} mb={2}>
          <Button
            size="small"
            startIcon={<AIIcon />}
            onClick={() => handleAIAssistance('improve')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Enhance Expression
          </Button>
          <Button
            size="small"
            startIcon={<AIIcon />}
            onClick={() => handleAIAssistance('continue')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Continue Writing
          </Button>
          <Button
            size="small"
            startIcon={<AIIcon />}
            onClick={() => handleAIAssistance('structure')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Structure Check
          </Button>
          <Button
            size="small"
            startIcon={<AIIcon />}
            onClick={() => handleAIAssistance('style')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Style Tips
          </Button>
          <Button
            size="small"
            startIcon={<AIIcon />}
            onClick={() => handleAIAssistance('creativity')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Creative Ideas
          </Button>
          {aiAssistanceMutation.isLoading && (
            <Box display="flex" alignItems="center" gap={1}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                AI is analyzing... This may take up to 2 minutes
              </Typography>
            </Box>
          )}
        </Stack>

        {/* Main Content Area - Two Panels */}
        <Box display="flex" gap={2} sx={{ minHeight: '500px' }}>
          {/* Left Panel - Editor */}
          <Box flex={1}>
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
                    Need help getting started? Here are some age-appropriate writing ideas for your project:
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
                theme="snow"
                value={content}
                onChange={handleContentChange}
                modules={quillModules}
                formats={quillFormats}
                style={{ height: '450px' }}
                placeholder="Start writing your content here..."
                preserveWhitespace={false}
                onChangeSelection={(range, source, editor) => {
                  // Debounce selection changes to improve performance
                  if (range && range.length > 0) {
                    const selectedText = editor.getText(range.index, range.length);
                    if (selectedText !== selectedText) {
                      setSelectedText(selectedText);
                    }
                  } else {
                    setSelectedText('');
                  }
                }}
              />
            </Box>
          </Box>

          {/* Right Panel - AI Results */}
          <Box flex={1}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="h6">
                🤖 AI Assistant Results
              </Typography>
              {aiResult && (
                <Stack direction="row" spacing={1}>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={handleApplyAIResult}
                    disabled={!aiResult}
                  >
                    Apply to Document
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleClearAIResult}
                  >
                    Clear
                  </Button>
                </Stack>
              )}
            </Box>

            <Paper
              variant="outlined"
              sx={{
                p: 2,
                minHeight: '450px',
                maxHeight: '450px',
                overflow: 'auto',
                backgroundColor: aiResult ? '#f8f9fa' : '#fafafa'
              }}
            >
              {aiResult ? (
                <Box>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Chip
                      label={aiResultType === 'analyze' ? 'Analysis Result' :
                            aiResultType === 'improve' ? 'Improvement Suggestion' :
                            aiResultType === 'continue' ? 'Continued Content' : 'AI Result'}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6,
                      '& strong': { fontWeight: 'bold' },
                      '& em': { fontStyle: 'italic' }
                    }}
                    dangerouslySetInnerHTML={{
                      __html: aiResult.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                      .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                      .replace(/\n/g, '<br/>')
                    }}
                  />
                </Box>
              ) : (
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  justifyContent="center"
                  height="100%"
                  color="text.secondary"
                >
                  <AIIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                  <Typography variant="body1" align="center">
                    AI analysis results will appear here
                  </Typography>
                  <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                    Select text and click AI buttons above to start analysis
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>
        </Box>

        {/* Document Stats */}
        <Box mt={4} pt={2} borderTop={1} borderColor="divider">
          <Typography variant="body2" color="text.secondary">
            Words: {content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length} | 
            Characters: {content.replace(/<[^>]*>/g, '').length} |
            Last saved: {document?.updated_at ? new Date(document.updated_at).toLocaleString() : 'Never'}
          </Typography>
        </Box>
      </Paper>

      {/* AI Assistant FAB */}
      <Fab
        color="secondary"
        aria-label="ai-assistant"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={() => setAiAssistantOpen(true)}
      >
        <ChatIcon />
      </Fab>

      {/* AI Assistant */}
      <AIAssistant
        open={aiAssistantOpen}
        onClose={() => setAiAssistantOpen(false)}
        projectId={projectId}
        documentId={documentId}
        context={content}
      />
    </Box>
  );
};

export default DocumentEditor;
