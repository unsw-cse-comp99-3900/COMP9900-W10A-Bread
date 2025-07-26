import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
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
  Tab,
  Tabs,
  Divider,
} from '@mui/material';
import {
  AutoFixHigh as AIIcon,
  Lightbulb as LightbulbIcon,
  ExpandMore as ExpandMoreIcon,
  Home as HomeIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Chat as ChatIcon,
  Menu as MenuIcon,
  FormatBold as BoldIcon,
  FormatItalic as ItalicIcon,
  FormatUnderlined as UnderlineIcon,
  Link as LinkIcon,
  FormatListBulleted as ListIcon,
  FormatListNumbered as NumberedListIcon,
  FormatAlignLeft as AlignLeftIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from 'react-query';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import '../../styles/quill-dark.css';
import { debounce } from 'lodash';
import guestService from '../../services/guestService';
import PersistentAIAssistant from '../../components/AI/PersistentAIAssistant';
import toast from 'react-hot-toast';
import { cleanAIResponse } from '../../utils/textUtils';
import { useThemeContext } from '../../contexts/ThemeContext';

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
  const { settings, theme } = useThemeContext();
  const projectData = location.state?.projectData || { name: 'My Writing Project', description: '', sample_text: '' };
  const selectedAgeGroup = location.state?.selectedAgeGroup || 'high_school';

  // State variables
  const [content, setContent] = useState(projectData.sample_text || '');
  const [selectedText, setSelectedText] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [aiResultType, setAiResultType] = useState('');
  const [writingPrompts, setWritingPrompts] = useState([]);
  const [activeTab, setActiveTab] = useState('assistance');
  const [wordCount, setWordCount] = useState(0);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [realtimeSettings, setRealtimeSettings] = useState({
    enabled: true,
    frequency: 'medium',
    suggestionTypes: ['vocabulary', 'structure', 'creativity', 'grammar'],
    showPriority: 'all'
  });

  // Set theme data attribute for Quill editor styling
  useEffect(() => {
    if (typeof document !== 'undefined' && document.documentElement) {
      document.documentElement.setAttribute('data-theme', settings.theme);
      return () => {
        if (typeof document !== 'undefined' && document.documentElement) {
          document.documentElement.removeAttribute('data-theme');
        }
      };
    }
  }, [settings.theme]);

  // Define tabs for the right sidebar
  const tabs = [
    {
      id: "assistance",
      label: "AI Writing Tools",
      icon: EditIcon,
      color: "text-teal-600"
    },
    {
      id: "chat",
      label: "AI Chat Assistant",
      icon: ChatIcon,
      color: "text-teal-600"
    },
    {
      id: "prompts",
      label: "Writing Prompts",
      icon: LightbulbIcon,
      color: "text-gray-600"
    }
  ];

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

  // AI assistance mutation for guest mode
  const aiAssistanceMutation = useMutation(
    (data) => guestService.getWritingAssistance(data.text, data.type, selectedAgeGroup),
    {
      onSuccess: (data, variables) => {
        setAiResult(cleanAIResponse(data.result));
        setAiResultType(variables.type);
        toast.success('AI analysis completed!');
      },
      onError: (error) => {
        console.error('AI assistance error:', error);
        if (error.code === 'ECONNABORTED') {
          toast.error('AI request timeout. Please try again.');
        } else {
          toast.error('Failed to get AI assistance. Please try again.');
        }
      },
    }
  );

  // Handle content change
  const handleContentChange = useCallback((value, delta, source, editor) => {
    if (value !== content) {
      setContent(value);

      // Update word count
      const plainText = value.replace(/<[^>]*>/g, '').trim();
      const words = plainText.split(/\s+/).filter(word => word.length > 0);
      setWordCount(words.length === 1 && words[0] === "" ? 0 : words.length);

      // Update cursor position for real-time AI
      if (editor && source === 'user') {
        const selection = editor.getSelection();
        if (selection) {
          setCursorPosition(selection.index);
        }
      }
    }
  }, [content]);

  // Handle AI assistance
  const handleAIAssistance = (type) => {
    const textToAnalyze = selectedText || content;
    if (!textToAnalyze.trim()) {
      toast.error('Please select some text or write content first');
      return;
    }
    aiAssistanceMutation.mutate({ text: textToAnalyze, type });
  };

  // Handle apply AI result
  const handleApplyAIResult = () => {
    if (!aiResult) return;

    if (aiResultType === 'continue') {
      setContent(prev => prev + '\n\n' + aiResult);
    } else if (aiResultType === 'improve' && selectedText) {
      setContent(prev => prev.replace(selectedText, aiResult));
    } else {
      setContent(prev => prev + '\n\n' + aiResult);
    }

    toast.success('AI suggestion applied to document!');
  };

  // Handle download
  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([content.replace(/<[^>]*>/g, '')], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${projectData.name || 'my-writing'}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Document downloaded!');
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation */}
      <Paper sx={{ borderBottom: 1, borderColor: 'divider', px: 2, py: 1.5 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center" gap={1.5}>
            <Box 
              sx={{ 
                width: 32, 
                height: 32, 
                bgcolor: 'primary.main',
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}
            >
              <EditIcon sx={{ color: 'white', fontSize: 16 }} />
            </Box>
            <IconButton size="small">
              <MenuIcon sx={{ fontSize: 16 }} />
            </IconButton>
            <Typography variant="body1" sx={{ fontWeight: 500, color: 'text.primary' }}>
              {projectData.name} (Guest Mode)
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <Button 
              variant="text" 
              size="small" 
              startIcon={<HomeIcon />}
              onClick={() => navigate('/guest')}
              sx={{ color: 'text.secondary' }}
            >
              Back to Guest Home
            </Button>
            <Button 
              variant="contained" 
              size="small"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              sx={{ bgcolor: 'primary.main', '&:hover': { bgcolor: 'primary.dark' } }}
            >
              Download
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Guest Mode Alert */}
      <Alert severity="info" sx={{ m: 2, mb: 0 }}>
        <Typography variant="body2">
          <strong>Guest Mode:</strong> You're using WritingWay without an account. 
          Your work won't be saved automatically. 
          <Button 
            size="small" 
            onClick={() => navigate('/register')}
            sx={{ ml: 1, textTransform: 'none' }}
          >
            Register to save your work
          </Button>
        </Typography>
      </Alert>

      {/* Top Right Tab Area */}
      <Box sx={{ bgcolor: 'grey.100', borderBottom: 1, borderColor: 'grey.200' }}>
        <Box display="flex" justifyContent="flex-end">
          <Box sx={{
            width: { xs: '100%', md: '33.333%' },
            display: 'flex',
            justifyContent: 'flex-start',
            px: 2
          }}>
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                '& .MuiTab-root': {
                  minHeight: 48,
                  textTransform: 'none',
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  fontWeight: 500,
                  minWidth: { xs: 'auto', sm: 120 },
                  px: { xs: 1, sm: 2 },
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: 'teal.600',
                },
              }}
            >
              {tabs.map((tab) => {
                const IconComponent = tab.icon;
                return (
                  <Tab
                    key={tab.id}
                    value={tab.id}
                    label={
                      <Box display="flex" alignItems="center" gap={1}>
                        <IconComponent sx={{ fontSize: 16, color: 'teal.600' }} />
                        <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                          {tab.label}
                        </Box>
                      </Box>
                    }
                    sx={{
                      color: activeTab === tab.id ? 'teal.600' : 'grey.600',
                      bgcolor: activeTab === tab.id ? 'white' : 'transparent',
                    }}
                  />
                );
              })}
            </Tabs>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: { xs: 'column', md: 'row' } }}>
        {/* Editor Area */}
        <Box sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          width: { xs: '100%', md: '66.667%' }
        }}>
          <Box sx={{ flex: 1, p: 4 }}>
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

                  {writingPrompts.slice(0, 2).map((prompt, index) => (
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

            <Box sx={{ minHeight: '500px', border: 'none', borderRadius: 1 }}>
              <ReactQuill
                theme="snow"
                value={content}
                onChange={handleContentChange}
                modules={guestQuillModules}
                formats={guestQuillFormats}
                style={{ height: '500px', border: 'none' }}
                placeholder="Type or paste (Ctrl+V) your text here to start writing..."
                preserveWhitespace={false}
                onChangeSelection={(range, source, editor) => {
                  if (range && range.length > 0) {
                    const selectedText = editor.getText(range.index, range.length);
                    setSelectedText(selectedText);
                  } else {
                    setSelectedText('');
                  }
                }}
              />
            </Box>
          </Box>

          {/* Bottom Toolbar */}
          <Box sx={{ borderTop: 1, borderColor: 'grey.200', bgcolor: 'white', px: 4, py: 1.5 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box display="flex" alignItems="center" gap={1}>
                <IconButton size="small">
                  <HelpIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
                <IconButton size="small">
                  <BoldIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <ItalicIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <UnderlineIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <LinkIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <ListIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <NumberedListIcon sx={{ fontSize: 16 }} />
                </IconButton>
                <IconButton size="small">
                  <AlignLeftIcon sx={{ fontSize: 16 }} />
                </IconButton>
              </Box>

              <Box display="flex" alignItems="center" gap={2}>
                <Typography variant="body2" color="text.secondary">
                  {wordCount} words
                </Typography>
                <Button variant="text" size="small" sx={{ color: 'grey.500' }}>
                  Try "Write about your favorite adventure"
                </Button>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Right Sidebar */}
        <Box sx={{
          width: { xs: '100%', md: '33.333%' },
          bgcolor: 'white',
          borderLeft: { xs: 0, md: 1 },
          borderTop: { xs: 1, md: 0 },
          borderColor: 'grey.200',
          p: { xs: 2, sm: 3 },
          maxHeight: { xs: '50vh', md: 'auto' },
          overflow: { xs: 'auto', md: 'visible' }
        }}>
          {/* Tab Content */}
          {activeTab === 'assistance' && (
            <Box>
              {/* AI Writing Tools */}
              <Typography variant="h6" sx={{ mb: 2, fontSize: { xs: '1rem', sm: '1.125rem' } }}>
                AI Writing Tools
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                Choose how you want AI to help improve your writing.
              </Typography>

              <Box
                sx={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: 1.5,
                  justifyContent: { xs: 'center', sm: 'flex-start' }
                }}
              >
                <Button
                  variant="contained"
                  onClick={() => handleAIAssistance('improve')}
                  disabled={aiAssistanceMutation.isLoading}
                  sx={{
                    borderRadius: '20px',
                    px: 2.5,
                    py: 1,
                    textTransform: 'none',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    fontWeight: 500,
                    bgcolor: '#e3f2fd',
                    color: '#1976d2',
                    boxShadow: 'none',
                    minWidth: 'auto',
                    '&:hover': {
                      bgcolor: '#bbdefb',
                      boxShadow: '0 2px 8px rgba(25, 118, 210, 0.2)',
                      transform: 'translateY(-1px)'
                    },
                    '&:disabled': {
                      bgcolor: '#f5f5f5',
                      color: '#bdbdbd'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  Improve
                </Button>

                <Button
                  variant="contained"
                  onClick={() => handleAIAssistance('continue')}
                  disabled={aiAssistanceMutation.isLoading}
                  sx={{
                    borderRadius: '20px',
                    px: 2.5,
                    py: 1,
                    textTransform: 'none',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    fontWeight: 500,
                    bgcolor: '#f3e5f5',
                    color: '#7b1fa2',
                    boxShadow: 'none',
                    minWidth: 'auto',
                    '&:hover': {
                      bgcolor: '#e1bee7',
                      boxShadow: '0 2px 8px rgba(123, 31, 162, 0.2)',
                      transform: 'translateY(-1px)'
                    },
                    '&:disabled': {
                      bgcolor: '#f5f5f5',
                      color: '#bdbdbd'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  Continue
                </Button>

                <Button
                  variant="contained"
                  onClick={() => handleAIAssistance('structure')}
                  disabled={aiAssistanceMutation.isLoading}
                  sx={{
                    borderRadius: '20px',
                    px: 2.5,
                    py: 1,
                    textTransform: 'none',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    fontWeight: 500,
                    bgcolor: '#e8f5e8',
                    color: '#388e3c',
                    boxShadow: 'none',
                    minWidth: 'auto',
                    '&:hover': {
                      bgcolor: '#c8e6c9',
                      boxShadow: '0 2px 8px rgba(56, 142, 60, 0.2)',
                      transform: 'translateY(-1px)'
                    },
                    '&:disabled': {
                      bgcolor: '#f5f5f5',
                      color: '#bdbdbd'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  Structure
                </Button>

                <Button
                  variant="contained"
                  onClick={() => handleAIAssistance('style')}
                  disabled={aiAssistanceMutation.isLoading}
                  sx={{
                    borderRadius: '20px',
                    px: 2.5,
                    py: 1,
                    textTransform: 'none',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    fontWeight: 500,
                    bgcolor: '#fff3e0',
                    color: '#f57c00',
                    boxShadow: 'none',
                    minWidth: 'auto',
                    '&:hover': {
                      bgcolor: '#ffe0b2',
                      boxShadow: '0 2px 8px rgba(245, 124, 0, 0.2)',
                      transform: 'translateY(-1px)'
                    },
                    '&:disabled': {
                      bgcolor: '#f5f5f5',
                      color: '#bdbdbd'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  Style
                </Button>

                <Button
                  variant="contained"
                  onClick={() => handleAIAssistance('creativity')}
                  disabled={aiAssistanceMutation.isLoading}
                  sx={{
                    borderRadius: '20px',
                    px: 2.5,
                    py: 1,
                    textTransform: 'none',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    fontWeight: 500,
                    bgcolor: '#fce4ec',
                    color: '#c2185b',
                    boxShadow: 'none',
                    minWidth: 'auto',
                    '&:hover': {
                      bgcolor: '#f8bbd9',
                      boxShadow: '0 2px 8px rgba(194, 24, 91, 0.2)',
                      transform: 'translateY(-1px)'
                    },
                    '&:disabled': {
                      bgcolor: '#f5f5f5',
                      color: '#bdbdbd'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  Creative
                </Button>
              </Box>

              {aiAssistanceMutation.isLoading && (
                <Box display="flex" alignItems="center" gap={1} mt={3}>
                  <CircularProgress size={20} />
                  <Typography variant="body2" color="text.secondary">
                    AI is analyzing...
                  </Typography>
                </Box>
              )}

              {/* AI Results */}
              {aiResult && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        AI Results
                      </Typography>
                      <Button
                        size="small"
                        variant="contained"
                        onClick={handleApplyAIResult}
                        sx={{ bgcolor: 'teal.600', '&:hover': { bgcolor: 'teal.700' } }}
                      >
                        Apply
                      </Button>
                    </Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {aiResult}
                    </Typography>
                  </CardContent>
                </Card>
              )}
            </Box>
          )}

          {activeTab === 'chat' && (
            <Box>
              {/* AI Chat Assistant for Guest Mode */}
              <Typography variant="h6" sx={{ mb: 2 }}>
                AI Chat Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Ask questions about writing techniques, get creative suggestions, or discuss your story ideas.
              </Typography>

              {/* Quick Prompts Preview */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, fontSize: '0.875rem' }}>
                  Quick Prompts (Preview)
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 1,
                    maxHeight: '120px',
                    overflowY: 'auto',
                    '&::-webkit-scrollbar': {
                      width: '4px',
                    },
                    '&::-webkit-scrollbar-track': {
                      background: '#f1f1f1',
                      borderRadius: '2px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      background: '#c1c1c1',
                      borderRadius: '2px',
                    },
                    '&::-webkit-scrollbar-thumb:hover': {
                      background: '#a8a8a8',
                    },
                  }}
                >
                  {[
                    "Help me brainstorm a story idea.",
                    "How do I improve my dialogue?",
                    "Give me a plot twist.",
                    "Describe a fantasy village.",
                    "What's a good character name?",
                    "How to write better descriptions?",
                    "Create a mysterious character.",
                    "Suggest a story opening."
                  ].map((prompt, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      size="small"
                      onClick={() => navigate('/register')}
                      sx={{
                        borderRadius: '16px',
                        px: 1.5,
                        py: 0.5,
                        fontSize: '0.75rem',
                        fontWeight: 400,
                        textTransform: 'none',
                        border: '1px solid #e0e0e0',
                        bgcolor: '#fafafa',
                        color: '#999',
                        minWidth: 'auto',
                        whiteSpace: 'nowrap',
                        opacity: 0.7,
                        '&:hover': {
                          bgcolor: '#f0f0f0',
                          borderColor: '#d0d0d0',
                          opacity: 1,
                          cursor: 'pointer'
                        },
                        transition: 'all 0.2s ease-in-out'
                      }}
                    >
                      {prompt}
                    </Button>
                  ))}
                </Box>
              </Box>

              <Card sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  Chat feature is available for registered users.
                  <br />
                  <Button
                    size="small"
                    onClick={() => navigate('/register')}
                    sx={{ mt: 1, textTransform: 'none' }}
                  >
                    Register to access AI Chat
                  </Button>
                </Typography>
              </Card>
            </Box>
          )}

          {activeTab === 'prompts' && (
            <Box>
              {/* Writing Prompts */}
              <Typography variant="h6" sx={{ mb: 1 }}>
                Writing Prompts
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Get inspired with age-appropriate writing ideas for your project.
              </Typography>

              {writingPrompts.length > 0 ? (
                <Stack spacing={2}>
                  {writingPrompts.map((prompt, index) => (
                    <Card key={index} sx={{ border: 1, borderColor: 'grey.200' }}>
                      <CardContent>
                        <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 1 }}>
                          💡 {prompt.title}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          {prompt.guidance}
                        </Typography>
                        {prompt.example && (
                          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                            Example: {prompt.example}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Loading writing prompts...
                </Typography>
              )}
            </Box>
          )}
        </Box>
      </Box>

      {/* Persistent AI Assistant */}
      <PersistentAIAssistant
        text={content.replace(/<[^>]*>/g, '')} // Strip HTML tags for analysis
        cursorPosition={cursorPosition}
        ageGroup={selectedAgeGroup}
        isEnabled={realtimeSettings.enabled}
        userPreferences={realtimeSettings}
      />
    </Box>
  );
};

export default GuestEditor;
