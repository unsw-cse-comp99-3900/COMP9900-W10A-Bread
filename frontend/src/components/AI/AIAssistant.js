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
import { cleanAIResponse } from '../../utils/textUtils';

const AIAssistant = ({ open, onClose, projectId, documentId, context, embedded = false, presetMessage = null }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  // Handle preset message
  useEffect(() => {
    if (presetMessage) {
      setMessage(presetMessage);
    }
  }, [presetMessage]);

  // Fetch conversation history
  const { data: conversationData } = useQuery(
    ['conversation', projectId],
    () => aiService.getConversationHistory(projectId),
    {
      enabled: (embedded || open) && !!projectId,
      onSuccess: (data) => {
        const cleanedMessages = (data.messages || []).map(msg => ({
          ...msg,
          content: msg.role === 'assistant' ? cleanAIResponse(msg.content) : msg.content
        }));
        setMessages(cleanedMessages);
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
          { role: 'assistant', content: cleanAIResponse(data.response) }
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

  // Chat content component
  const ChatContent = () => (
    <>
      {/* Messages */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          maxHeight: embedded ? '400px' : 'auto',
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
                  bgcolor: msg.role === 'user' ? 'primary.main' : 'grey.100',
                  color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <Box display="flex" alignItems="flex-start" gap={1}>
                  {msg.role === 'assistant' && <AIIcon sx={{ fontSize: 20, mt: 0.5 }} />}
                  {msg.role === 'user' && <PersonIcon sx={{ fontSize: 20, mt: 0.5 }} />}
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {msg.content}
                  </Typography>
                </Box>
              </Paper>
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box display="flex" gap={1}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="Ask your AI assistant anything about writing..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={chatMutation.isLoading}
            size="small"
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!message.trim() || chatMutation.isLoading}
            sx={{ minWidth: 'auto', px: 2 }}
          >
            {chatMutation.isLoading ? <CircularProgress size={20} /> : <SendIcon />}
          </Button>
        </Box>
      </Box>
    </>
  );

  if (embedded) {
    return (
      <Box sx={{ height: '500px', display: 'flex', flexDirection: 'column', border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
        <ChatContent />
      </Box>
    );
  }

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
        <ChatContent />
      </DialogContent>
    </Dialog>
  );
};

export default AIAssistant;
