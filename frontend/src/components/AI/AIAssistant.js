import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Close as CloseIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from 'react-query';
import toast from 'react-hot-toast';

import aiService from '../../services/aiService';

const AIAssistant = ({ open, onClose, projectId, documentId, context }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  // Fetch conversation history
  const { data: conversationData } = useQuery(
    ['conversation', projectId],
    () => aiService.getConversationHistory(projectId),
    {
      enabled: open && !!projectId,
      onSuccess: (data) => {
        setMessages(data.messages || []);
      },
    }
  );

  // Chat mutation
  const chatMutation = useMutation(
    (data) => aiService.chat(data.message, data.projectId, data.documentId, data.context),
    {
      onSuccess: (data) => {
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          { role: 'assistant', content: data.response }
        ]);
        setMessage('');
      },
      onError: () => {
        toast.error('Failed to get AI response');
      },
    }
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!message.trim()) return;

    chatMutation.mutate({
      message: message.trim(),
      projectId,
      documentId,
      context,
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClose = () => {
    setMessage('');
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      TransitionComponent={undefined}
      transitionDuration={0}
      PaperProps={{
        sx: { height: '80vh', display: 'flex', flexDirection: 'column' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center">
          <AIIcon sx={{ mr: 1 }} />
          AI Writing Assistant
        </Box>
        <IconButton onClick={handleClose}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
        {/* Messages */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="text.secondary">
                Start a conversation with your AI writing assistant!
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Ask for help with plot development, character creation, or writing improvement.
              </Typography>
            </Box>
          ) : (
            messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1,
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    backgroundColor: msg.role === 'user' ? 'primary.main' : 'grey.100',
                    color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  }}
                >
                  <Box display="flex" alignItems="center" mb={1}>
                    {msg.role === 'user' ? (
                      <PersonIcon sx={{ fontSize: 16, mr: 1 }} />
                    ) : (
                      <AIIcon sx={{ fontSize: 16, mr: 1 }} />
                    )}
                    <Typography variant="caption" fontWeight="bold">
                      {msg.role === 'user' ? 'You' : 'AI Assistant'}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {msg.content}
                  </Typography>
                </Paper>
              </Box>
            ))
          )}
          
          {chatMutation.isLoading && (
            <Box display="flex" justifyContent="flex-start" mb={1}>
              <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
                <Box display="flex" alignItems="center">
                  <CircularProgress size={16} sx={{ mr: 1 }} />
                  <Typography variant="body2">AI is thinking...</Typography>
                </Box>
              </Paper>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        <Divider />

        {/* Input */}
        <Box sx={{ p: 2 }}>
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask your AI assistant anything about your writing..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={chatMutation.isLoading}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!message.trim() || chatMutation.isLoading}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              <SendIcon />
            </Button>
          </Box>
          
          {/* Quick suggestions */}
          <Box mt={1}>
            <Typography variant="caption" color="text.secondary">
              Quick suggestions:
            </Typography>
            <Box display="flex" gap={1} mt={0.5} flexWrap="wrap">
              {[
                'Help me develop this character',
                'Suggest plot improvements',
                'Check my writing style',
                'Continue this scene',
              ].map((suggestion) => (
                <Button
                  key={suggestion}
                  size="small"
                  variant="outlined"
                  onClick={() => setMessage(suggestion)}
                  disabled={chatMutation.isLoading}
                  sx={{ fontSize: '0.75rem', py: 0.5 }}
                >
                  {suggestion}
                </Button>
              ))}
            </Box>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default AIAssistant;
