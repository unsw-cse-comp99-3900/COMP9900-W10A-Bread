import React, { useState, useEffect, useCallback } from 'react';
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
} from '@mui/material';
import {
  Save as SaveIcon,
  Chat as ChatIcon,
  AutoFixHigh as AIIcon,
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

const DocumentEditor = () => {
  const { projectId, documentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [aiAssistantOpen, setAiAssistantOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [aiResultType, setAiResultType] = useState('');

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

  // Save document mutation
  const saveDocumentMutation = useMutation(
    (data) => projectService.updateDocument(documentId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['document', documentId]);
        setHasUnsavedChanges(false);
        toast.success('Document saved!');
      },
      onError: () => {
        toast.error('Failed to save document');
      },
    }
  );

  // AI assistance mutation
  const aiAssistanceMutation = useMutation(
    (data) => aiService.getWritingAssistance(data.text, data.type, projectId),
    {
      onSuccess: (data, variables) => {
        // Display AI result in separate panel
        setAiResult(data.result);
        setAiResultType(variables.type);
        toast.success('AI analysis completed!');
      },
      onError: () => {
        toast.error('Failed to get AI assistance');
      },
    }
  );

  // Auto-save functionality
  const debouncedSave = useCallback(
    debounce((title, content) => {
      if (hasUnsavedChanges) {
        saveDocumentMutation.mutate({ title, content });
      }
    }, 2000),
    [hasUnsavedChanges, saveDocumentMutation]
  );

  useEffect(() => {
    if (hasUnsavedChanges && title && content) {
      debouncedSave(title, content);
    }
  }, [title, content, hasUnsavedChanges, debouncedSave]);

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    setHasUnsavedChanges(true);
  };

  const handleContentChange = (value) => {
    setContent(value);
    setHasUnsavedChanges(true);
  };

  const handleManualSave = () => {
    saveDocumentMutation.mutate({ title, content });
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
            Improve Text
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
            onClick={() => handleAIAssistance('analyze')}
            disabled={aiAssistanceMutation.isLoading}
          >
            Analyze
          </Button>
          {aiAssistanceMutation.isLoading && (
            <CircularProgress size={20} />
          )}
        </Stack>

        {/* Main Content Area - Two Panels */}
        <Box display="flex" gap={2} sx={{ minHeight: '500px' }}>
          {/* Left Panel - Editor */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              📝 Writing Area
            </Typography>
            <Box sx={{ minHeight: '450px', border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <ReactQuill
                theme="snow"
                value={content}
                onChange={handleContentChange}
                modules={quillModules}
                style={{ height: '450px' }}
                onChangeSelection={(range, source, editor) => {
                  if (range && range.length > 0) {
                    setSelectedText(editor.getText(range.index, range.length));
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
