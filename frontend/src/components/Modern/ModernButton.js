import React from 'react';
import { Button, IconButton, Fab } from '@mui/material';
import { styled } from '@mui/material/styles';

// 现代化主按钮
const StyledButton = styled(Button)(({ theme, variant, size, modernVariant = 'primary' }) => {
  const getVariantStyles = () => {
    switch (modernVariant) {
      case 'primary':
        return {
          background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          color: '#FFFFFF',
          '&:hover': {
            background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
            boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)',
          },
        };
      case 'accent':
        return {
          background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
          color: '#1F2937',
          '&:hover': {
            background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
            boxShadow: '0 8px 25px rgba(252, 211, 77, 0.3)',
          },
        };
      case 'coral':
        return {
          background: 'linear-gradient(135deg, #F87171 0%, #EF4444 100%)',
          color: '#FFFFFF',
          '&:hover': {
            background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
            boxShadow: '0 8px 25px rgba(248, 113, 113, 0.3)',
          },
        };
      case 'glass':
        return {
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          color: '#1F2937',
          '&:hover': {
            background: 'rgba(255, 255, 255, 0.9)',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
          },
        };
      case 'outline':
        return {
          background: 'transparent',
          border: '2px solid #6366F1',
          color: '#6366F1',
          '&:hover': {
            background: '#6366F1',
            color: '#FFFFFF',
            boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)',
          },
        };
      default:
        return {};
    }
  };

  return {
    borderRadius: size === 'small' ? 12 : size === 'large' ? 20 : 16,
    padding: size === 'small' ? '8px 16px' : size === 'large' ? '16px 32px' : '12px 24px',
    fontSize: size === 'small' ? '0.75rem' : size === 'large' ? '1rem' : '0.875rem',
    fontWeight: 500,
    textTransform: 'none',
    boxShadow: 'none',
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    
    // 光泽效果
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: '-100%',
      width: '100%',
      height: '100%',
      background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
      transition: 'left 0.5s',
    },
    
    '&:hover': {
      transform: 'translateY(-2px)',
      '&::before': {
        left: '100%',
      },
    },
    
    '&:active': {
      transform: 'scale(0.98)',
    },
    
    '&:disabled': {
      background: '#E5E7EB',
      color: '#9CA3AF',
      transform: 'none',
      '&:hover': {
        transform: 'none',
        boxShadow: 'none',
      },
    },
    
    ...getVariantStyles(),
  };
});

// 现代化图标按钮
const StyledIconButton = styled(IconButton)(({ theme, size, modernVariant = 'default' }) => {
  const getVariantStyles = () => {
    switch (modernVariant) {
      case 'primary':
        return {
          background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          color: '#FFFFFF',
          '&:hover': {
            background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
          },
        };
      case 'accent':
        return {
          background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
          color: '#1F2937',
          '&:hover': {
            background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
          },
        };
      case 'glass':
        return {
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          '&:hover': {
            background: 'rgba(255, 255, 255, 0.9)',
          },
        };
      default:
        return {
          background: 'rgba(99, 102, 241, 0.1)',
          color: '#6366F1',
          '&:hover': {
            background: 'rgba(99, 102, 241, 0.2)',
          },
        };
    }
  };

  return {
    borderRadius: size === 'small' ? 8 : size === 'large' ? 16 : 12,
    width: size === 'small' ? 32 : size === 'large' ? 48 : 40,
    height: size === 'small' ? 32 : size === 'large' ? 48 : 40,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    
    '&:hover': {
      transform: 'scale(1.05)',
    },
    
    '&:active': {
      transform: 'scale(0.95)',
    },
    
    ...getVariantStyles(),
  };
});

// 现代化浮动按钮
const StyledFab = styled(Fab)(({ theme, modernVariant = 'primary' }) => {
  const getVariantStyles = () => {
    switch (modernVariant) {
      case 'primary':
        return {
          background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
          },
        };
      case 'accent':
        return {
          background: 'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
          color: '#1F2937',
          '&:hover': {
            background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
          },
        };
      case 'coral':
        return {
          background: 'linear-gradient(135deg, #F87171 0%, #EF4444 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
          },
        };
      default:
        return {};
    }
  };

  return {
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    },
    
    '&:active': {
      transform: 'scale(0.95)',
    },
    
    ...getVariantStyles(),
  };
});

// 主按钮组件
const ModernButton = ({ 
  children, 
  modernVariant = 'primary', 
  size = 'medium',
  loading = false,
  ...props 
}) => {
  return (
    <StyledButton
      modernVariant={modernVariant}
      size={size}
      disabled={loading}
      {...props}
    >
      {loading ? (
        <div className="loading-spin" style={{ 
          width: 16, 
          height: 16, 
          border: '2px solid currentColor', 
          borderTop: '2px solid transparent', 
          borderRadius: '50%' 
        }} />
      ) : (
        children
      )}
    </StyledButton>
  );
};

// 图标按钮组件
const ModernIconButton = ({ 
  children, 
  modernVariant = 'default', 
  size = 'medium',
  ...props 
}) => {
  return (
    <StyledIconButton
      modernVariant={modernVariant}
      size={size}
      {...props}
    >
      {children}
    </StyledIconButton>
  );
};

// 浮动按钮组件
const ModernFab = ({ 
  children, 
  modernVariant = 'primary',
  ...props 
}) => {
  return (
    <StyledFab
      modernVariant={modernVariant}
      {...props}
    >
      {children}
    </StyledFab>
  );
};

export { ModernButton, ModernIconButton, ModernFab };
export default ModernButton;
