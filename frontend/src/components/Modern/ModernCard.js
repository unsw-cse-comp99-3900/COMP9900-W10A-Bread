import React from 'react';
import { Card, CardContent, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

// 现代化卡片组件
const StyledCard = styled(Card)(({ theme, variant = 'default', hoverable = true }) => ({
  borderRadius: 20,
  border: '1px solid rgba(0, 0, 0, 0.05)',
  background: variant === 'glass' 
    ? 'rgba(255, 255, 255, 0.8)' 
    : variant === 'warm'
    ? '#FEF7ED'
    : '#FFFFFF',
  backdropFilter: variant === 'glass' ? 'blur(10px)' : 'none',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',
  
  // 顶部渐变线
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1,
    background: variant === 'accent' 
      ? 'linear-gradient(90deg, transparent, #FCD34D, transparent)'
      : variant === 'coral'
      ? 'linear-gradient(90deg, transparent, #F87171, transparent)'
      : 'linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent)',
  },
  
  // 悬停效果
  ...(hoverable && {
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      borderColor: variant === 'accent' 
        ? 'rgba(252, 211, 77, 0.3)'
        : variant === 'coral'
        ? 'rgba(248, 113, 113, 0.3)'
        : 'rgba(99, 102, 241, 0.2)',
    },
  }),
  
  // 点击效果
  '&:active': {
    transform: hoverable ? 'translateY(-2px) scale(0.98)' : 'none',
  },
}));

const ModernCard = ({ 
  children, 
  variant = 'default', 
  hoverable = true, 
  floating = false,
  onClick,
  sx = {},
  ...props 
}) => {
  return (
    <StyledCard
      variant={variant}
      hoverable={hoverable}
      onClick={onClick}
      className={floating ? 'floating-card' : ''}
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        ...sx,
      }}
      {...props}
    >
      {children}
    </StyledCard>
  );
};

// 现代化卡片内容组件
const ModernCardContent = styled(CardContent)(({ theme }) => ({
  padding: '24px',
  '&:last-child': {
    paddingBottom: '24px',
  },
}));

// 现代化卡片头部
const ModernCardHeader = ({ title, subtitle, action, icon }) => (
  <Box sx={{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'space-between',
    mb: subtitle ? 1 : 2,
  }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      {icon && (
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          width: 40,
          height: 40,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          color: 'white',
        }}>
          {icon}
        </Box>
      )}
      <Box>
        <Box sx={{ 
          fontSize: '1.125rem', 
          fontWeight: 600, 
          color: '#1F2937',
          lineHeight: 1.2,
        }}>
          {title}
        </Box>
        {subtitle && (
          <Box sx={{ 
            fontSize: '0.875rem', 
            color: '#6B7280',
            mt: 0.5,
          }}>
            {subtitle}
          </Box>
        )}
      </Box>
    </Box>
    {action && (
      <Box>{action}</Box>
    )}
  </Box>
);

// 现代化统计卡片
const ModernStatsCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'positive',
  icon,
  variant = 'default',
  animated = true,
}) => (
  <ModernCard variant={variant} hoverable>
    <ModernCardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ 
          fontSize: '0.875rem', 
          fontWeight: 500, 
          color: '#6B7280',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}>
          {title}
        </Box>
        {icon && (
          <Box sx={{ 
            color: variant === 'accent' ? '#F59E0B' : variant === 'coral' ? '#EF4444' : '#6366F1',
            opacity: 0.7,
          }}>
            {icon}
          </Box>
        )}
      </Box>
      
      <Box sx={{ 
        fontSize: '2rem', 
        fontWeight: 700, 
        color: '#1F2937',
        lineHeight: 1,
        mb: 1,
        ...(animated && { className: 'count-animation' }),
      }}>
        {value}
      </Box>
      
      {change && (
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 0.5,
          fontSize: '0.75rem',
          fontWeight: 500,
          color: changeType === 'positive' ? '#10B981' : changeType === 'negative' ? '#EF4444' : '#6B7280',
        }}>
          <span>{changeType === 'positive' ? '↗' : changeType === 'negative' ? '↘' : '→'}</span>
          {change}
        </Box>
      )}
    </ModernCardContent>
  </ModernCard>
);

export { ModernCard, ModernCardContent, ModernCardHeader, ModernStatsCard };
export default ModernCard;
