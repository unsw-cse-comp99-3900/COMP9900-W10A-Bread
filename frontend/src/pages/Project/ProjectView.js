import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Fab,
  Divider,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

import projectService from '../../services/projectService';
import AIAssistant from '../../components/AI/AIAssistant';

const ProjectView = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [createDocDialogOpen, setCreateDocDialogOpen] = useState(false);
  const [aiAssistantOpen, setAiAssistantOpen] = useState(false);
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  // Fetch project details
  const { data: project, isLoading: projectLoading } = useQuery(
    ['project', projectId],
    () => projectService.getProject(projectId),
    {
      onError: () => {
        toast.error('Failed to load project');
        navigate('/dashboard');
      },
    }
  );

  // Fetch project documents
  const { data: documents, isLoading: documentsLoading } = useQuery(
    ['documents', projectId],
    () => projectService.getProjectDocuments(projectId),
    {
      enabled: !!projectId,
      onError: () => {
        toast.error('Failed to load documents');
      },
    }
  );

  // Create document mutation
  const createDocumentMutation = useMutation(
    projectService.createDocument,
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['documents', projectId]);
        setCreateDocDialogOpen(false);
        reset();
        toast.success('Document created successfully!');
      },
      onError: () => {
        toast.error('Failed to create document');
      },
    }
  );

  // Delete document mutation
  const deleteDocumentMutation = useMutation(
    projectService.deleteDocument,
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['documents', projectId]);
        toast.success('Document deleted successfully!');
      },
      onError: () => {
        toast.error('Failed to delete document');
      },
    }
  );

  const handleCreateDocument = (data) => {
    createDocumentMutation.mutate({
      ...data,
      project_id: parseInt(projectId),
    });
  };

  const handleDeleteDocument = (documentId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteDocumentMutation.mutate(documentId);
    }
  };

  const handleOpenDocument = (documentId) => {
    navigate(`/project/${projectId}/document/${documentId}`);
  };

  if (projectLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Project Info */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
              {project?.name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {project?.description || 'No description'}
            </Typography>
          </Paper>
        </Grid>

        {/* Documents List */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Documents</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDocDialogOpen(true)}
              >
                New Document
              </Button>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            {documentsLoading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : documents?.length > 0 ? (
              <List>
                {documents.map((doc) => (
                  <ListItem
                    key={doc.id}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon>
                      <DocumentIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={doc.title}
                      secondary={`Type: ${doc.document_type} | Updated: ${new Date(doc.updated_at).toLocaleDateString()}`}
                      onClick={() => handleOpenDocument(doc.id)}
                      sx={{ cursor: 'pointer' }}
                    />
                    <IconButton
                      edge="end"
                      onClick={() => handleOpenDocument(doc.id)}
                      sx={{ mr: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      color="error"
                      onClick={() => handleDeleteDocument(doc.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box textAlign="center" py={4}>
                <Typography variant="body1" color="text.secondary">
                  No documents yet. Create your first document to get started!
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Project Stats */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Project Statistics
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Documents: {documents?.length || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Created: {project?.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last Updated: {project?.updated_at ? new Date(project.updated_at).toLocaleDateString() : 'Unknown'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

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

      {/* Create Document Dialog */}
      <Dialog
        open={createDocDialogOpen}
        onClose={() => setCreateDocDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        TransitionComponent={undefined}
        transitionDuration={0}
      >
        <DialogTitle>Create New Document</DialogTitle>
        <form onSubmit={handleSubmit(handleCreateDocument)}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Document Title"
              fullWidth
              variant="outlined"
              {...register('title', { required: 'Document title is required' })}
              error={!!errors.title}
              helperText={errors.title?.message}
            />
            <TextField
              margin="dense"
              label="Document Type"
              fullWidth
              variant="outlined"
              defaultValue="scene"
              {...register('document_type')}
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDocDialogOpen(false)}>Cancel</Button>
            <Button 
              type="submit" 
              variant="contained"
              disabled={createDocumentMutation.isLoading}
            >
              {createDocumentMutation.isLoading ? <CircularProgress size={24} /> : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* AI Assistant */}
      <AIAssistant
        open={aiAssistantOpen}
        onClose={() => setAiAssistantOpen(false)}
        projectId={projectId}
      />
    </Box>
  );
};

export default ProjectView;
