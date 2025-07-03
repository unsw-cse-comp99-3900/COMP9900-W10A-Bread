import React from 'react';
import { Box } from '@mui/material';

const AIWritingIllustration = ({ width = 400, height = 300 }) => {
  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      <svg
        width={width}
        height={height}
        viewBox="0 0 400 300"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ maxWidth: '100%', height: 'auto' }}
      >
        {/* 背景渐变 */}
        <defs>
          <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366F1" stopOpacity="0.1" />
            <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.05" />
            <stop offset="100%" stopColor="#F87171" stopOpacity="0.1" />
          </linearGradient>
          
          <linearGradient id="paperGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#F9FAFB" />
          </linearGradient>
          
          <linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366F1" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
          
          <linearGradient id="penGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FCD34D" />
            <stop offset="100%" stopColor="#F59E0B" />
          </linearGradient>
          
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* 背景 */}
        <rect width="400" height="300" fill="url(#bgGradient)" rx="20" />
        
        {/* 浮动的装饰元素 */}
        <circle cx="80" cy="60" r="3" fill="#6366F1" opacity="0.3">
          <animate attributeName="cy" values="60;50;60" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx="320" cy="80" r="2" fill="#F87171" opacity="0.4">
          <animate attributeName="cy" values="80;70;80" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="350" cy="200" r="2.5" fill="#FCD34D" opacity="0.5">
          <animate attributeName="cy" values="200;190;200" dur="3.5s" repeatCount="indefinite" />
        </circle>
        
        {/* 主要文档 */}
        <rect x="120" y="80" width="160" height="200" rx="12" fill="url(#paperGradient)" 
              stroke="rgba(0,0,0,0.1)" strokeWidth="1" filter="url(#glow)" />
        
        {/* 文档内容线条 */}
        <rect x="140" y="110" width="80" height="3" rx="1.5" fill="#6366F1" opacity="0.6" />
        <rect x="140" y="125" width="100" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        <rect x="140" y="135" width="90" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        <rect x="140" y="145" width="110" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        
        <rect x="140" y="170" width="70" height="3" rx="1.5" fill="#F87171" opacity="0.6" />
        <rect x="140" y="185" width="95" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        <rect x="140" y="195" width="85" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        
        <rect x="140" y="220" width="75" height="3" rx="1.5" fill="#FCD34D" opacity="0.6" />
        <rect x="140" y="235" width="105" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        <rect x="140" y="245" width="80" height="2" rx="1" fill="#9CA3AF" opacity="0.5" />
        
        {/* AI 大脑图标 */}
        <circle cx="320" cy="140" r="25" fill="url(#aiGradient)" filter="url(#glow)">
          <animate attributeName="r" values="25;27;25" dur="2s" repeatCount="indefinite" />
        </circle>
        
        {/* AI 大脑内部结构 */}
        <circle cx="315" cy="135" r="3" fill="white" opacity="0.8" />
        <circle cx="325" cy="135" r="3" fill="white" opacity="0.8" />
        <circle cx="320" cy="145" r="2" fill="white" opacity="0.6" />
        
        {/* 连接线 */}
        <path d="M310 130 Q320 125 330 130" stroke="white" strokeWidth="1.5" fill="none" opacity="0.7" />
        <path d="M310 150 Q320 155 330 150" stroke="white" strokeWidth="1.5" fill="none" opacity="0.7" />
        
        {/* 魔法笔 */}
        <rect x="85" y="180" width="4" height="40" rx="2" fill="url(#penGradient)" 
              transform="rotate(-15 87 200)" />
        <circle cx="87" cy="175" r="3" fill="#F59E0B" transform="rotate(-15 87 200)" />
        
        {/* 魔法粒子 */}
        <circle cx="95" cy="170" r="1.5" fill="#FCD34D" opacity="0.8">
          <animate attributeName="opacity" values="0.8;0.3;0.8" dur="1.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="100" cy="165" r="1" fill="#F87171" opacity="0.6">
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="105" cy="160" r="1.2" fill="#6366F1" opacity="0.7">
          <animate attributeName="opacity" values="0.7;0.3;0.7" dur="1.8s" repeatCount="indefinite" />
        </circle>
        
        {/* AI 到文档的连接线 */}
        <path d="M295 140 Q250 120 200 140" stroke="#6366F1" strokeWidth="2" 
              fill="none" opacity="0.4" strokeDasharray="5,5">
          <animate attributeName="stroke-dashoffset" values="0;10" dur="2s" repeatCount="indefinite" />
        </path>
        
        {/* 思考泡泡 */}
        <circle cx="360" cy="120" r="8" fill="white" stroke="#6366F1" strokeWidth="1" opacity="0.8" />
        <circle cx="370" cy="110" r="5" fill="white" stroke="#6366F1" strokeWidth="1" opacity="0.6" />
        <circle cx="375" cy="100" r="3" fill="white" stroke="#6366F1" strokeWidth="1" opacity="0.4" />
        
        {/* 思考泡泡内的图标 */}
        <text x="360" y="125" textAnchor="middle" fontSize="8" fill="#6366F1">💡</text>
        
        {/* 底部装饰波浪 */}
        <path d="M0 280 Q100 270 200 280 T400 280 L400 300 L0 300 Z" 
              fill="rgba(99, 102, 241, 0.05)" />
      </svg>
    </Box>
  );
};

export default AIWritingIllustration;
