import React, { useState, forwardRef } from 'react';
import { TextField, Box, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

// 现代化输入框样式
const StyledTextField = styled(TextField)(({ theme, focused, hasValue }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(0, 0, 0, 0.08)',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontSize: '1rem',
    fontWeight: 400,
    height: 48,

    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.2)',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',

      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: 'rgba(99, 102, 241, 0.3)',
      },
    },

    '&.Mui-focused': {
      backgroundColor: 'rgba(255, 255, 255, 1)',
      borderColor: '#6366F1',
      boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.1), 0 4px 12px rgba(99, 102, 241, 0.15)',

      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: '#6366F1',
        borderWidth: 1,
      },
    },
    
    '&.Mui-error': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: '#F87171',
      },
      
      '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: '#EF4444',
      },
      
      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: '#EF4444',
        boxShadow: '0 0 0 3px rgba(248, 113, 113, 0.1)',
      },
    },
  },
  
  '& .MuiOutlinedInput-notchedOutline': {
    borderColor: 'rgba(0, 0, 0, 0.1)',
    borderWidth: 1,
  },
  
  '& .MuiInputLabel-root': {
    fontSize: '0.95rem',
    fontWeight: 500,
    color: '#6B7280',
    transform: hasValue || focused ? 'translate(14px, -9px) scale(0.75)' : 'translate(14px, 14px) scale(1)',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',

    '&.Mui-focused': {
      color: '#6366F1',
      fontWeight: 600,
    },

    '&.Mui-error': {
      color: '#F87171',
    },
  },
  
  '& .MuiFormHelperText-root': {
    fontSize: '0.75rem',
    marginTop: 8,
    marginLeft: 4,
    fontWeight: 500,
    
    '&.Mui-error': {
      color: '#F87171',
    },
  },
}));

// 浮动标签容器
const FloatingLabelContainer = styled(Box)(({ theme, focused, hasValue, error }) => ({
  position: 'relative',
  marginBottom: 24,
  
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 16,
    padding: 2,
    background: focused 
      ? 'linear-gradient(135deg, #6366F1, #8B5CF6)' 
      : error 
      ? 'linear-gradient(135deg, #F87171, #EF4444)'
      : 'transparent',
    mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    maskComposite: 'exclude',
    opacity: focused ? 1 : 0,
    transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  },
}));

const ModernTextField = forwardRef(({
  label,
  value,
  onChange,
  error,
  helperText,
  type = 'text',
  required = false,
  autoFocus = false,
  sx = {},
  ...props
}, ref) => {
  const [focused, setFocused] = useState(false);
  const [internalValue, setInternalValue] = useState('');

  // 使用传入的value或内部状态
  const currentValue = value !== undefined ? value : internalValue;
  const hasValue = currentValue && currentValue.length > 0;

  const handleChange = (event) => {
    if (onChange) {
      onChange(event);
    } else {
      setInternalValue(event.target.value);
    }
  };

  return (
    <Box sx={{ mb: 2, ...sx }}>
      <StyledTextField
        ref={ref}
        fullWidth
        variant="outlined"
        label={label}
        value={currentValue}
        onChange={handleChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        error={!!error}
        helperText={helperText}
        type={type}
        required={required}
        autoFocus={autoFocus}
        focused={focused}
        hasValue={hasValue}
        InputProps={{
          sx: {
            height: 48,
            fontSize: '0.95rem',
            fontWeight: 400,
          },
        }}
        InputLabelProps={{
          shrink: false,
        }}
        FormHelperTextProps={{
          sx: {
            fontSize: '0.75rem',
            mt: 1,
            ml: 0.5,
          },
        }}
        {...props}
      />
    </Box>
  );
});

ModernTextField.displayName = 'ModernTextField';

export default ModernTextField;
