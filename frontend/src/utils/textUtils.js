/**
 * Text utility functions for processing and formatting text content
 */

/**
 * Clean Markdown formatting from text
 * Removes ** (bold), * (italic), and other common Markdown syntax
 * @param {string} text - The text to clean
 * @returns {string} - The cleaned text without Markdown formatting
 */
export const cleanMarkdownFormatting = (text) => {
  if (!text || typeof text !== 'string') {
    return text;
  }

  return text
    // Remove bold formatting (**text** or __text__)
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    
    // Remove italic formatting (*text* or _text_)
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/_(.*?)_/g, '$1')
    
    // Remove strikethrough (~~text~~)
    .replace(/~~(.*?)~~/g, '$1')
    
    // Remove inline code (`text`)
    .replace(/`(.*?)`/g, '$1')
    
    // Remove headers (# ## ### etc.)
    .replace(/^#{1,6}\s+/gm, '')
    
    // Remove horizontal rules (--- or ***)
    .replace(/^[-*]{3,}$/gm, '')
    
    // Remove blockquote markers (> )
    .replace(/^>\s+/gm, '')
    
    // Remove list markers (- * + or 1. 2. etc.)
    .replace(/^[\s]*[-*+]\s+/gm, '')
    .replace(/^[\s]*\d+\.\s+/gm, '')
    
    // Clean up extra whitespace
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

/**
 * Clean AI response text specifically for UI display
 * Focuses on removing common AI formatting patterns
 * @param {string} text - The AI response text
 * @returns {string} - The cleaned text
 */
export const cleanAIResponse = (text) => {
  if (!text || typeof text !== 'string') {
    return text;
  }

  return text
    // Remove common AI formatting patterns
    .replace(/\*\*(Instead of:|Try:|Consider:|Suggestion:|Note:|Example:|Tip:)\*\*/gi, '$1')
    .replace(/\*\*(.*?):\*\*/g, '$1:')
    
    // Remove bold formatting around common phrases
    .replace(/\*\*(Here's|Here are|You could|You might|Consider|Try|Instead)\*\*/gi, '$1')
    
    // Apply general markdown cleaning
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    
    // Clean up extra whitespace
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

/**
 * Format text for display in UI components
 * @param {string} text - The text to format
 * @param {Object} options - Formatting options
 * @returns {string} - The formatted text
 */
export const formatTextForDisplay = (text, options = {}) => {
  const {
    cleanMarkdown = true,
    preserveLineBreaks = true,
    maxLength = null
  } = options;

  if (!text || typeof text !== 'string') {
    return text;
  }

  let formattedText = text;

  // Clean markdown if requested
  if (cleanMarkdown) {
    formattedText = cleanAIResponse(formattedText);
  }

  // Preserve line breaks for display
  if (preserveLineBreaks) {
    formattedText = formattedText.replace(/\n/g, '\n');
  }

  // Truncate if max length specified
  if (maxLength && formattedText.length > maxLength) {
    formattedText = formattedText.substring(0, maxLength) + '...';
  }

  return formattedText;
};

/**
 * Count words in text
 * @param {string} text - The text to count
 * @returns {number} - The word count
 */
export const countWords = (text) => {
  if (!text || typeof text !== 'string') {
    return 0;
  }
  
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
};

/**
 * Extract plain text from HTML
 * @param {string} html - The HTML string
 * @returns {string} - The plain text
 */
export const stripHtmlTags = (html) => {
  if (!html || typeof html !== 'string') {
    return html;
  }
  
  return html.replace(/<[^>]*>/g, '');
};
