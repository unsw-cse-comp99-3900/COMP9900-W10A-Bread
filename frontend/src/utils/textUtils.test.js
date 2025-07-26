/**
 * Test file for textUtils functions
 * Run with: npm test textUtils.test.js
 */

import { cleanMarkdownFormatting, cleanAIResponse, formatTextForDisplay } from './textUtils';

describe('Text Utils', () => {
  describe('cleanMarkdownFormatting', () => {
    test('removes bold formatting', () => {
      expect(cleanMarkdownFormatting('**bold text**')).toBe('bold text');
      expect(cleanMarkdownFormatting('__bold text__')).toBe('bold text');
    });

    test('removes italic formatting', () => {
      expect(cleanMarkdownFormatting('*italic text*')).toBe('italic text');
      expect(cleanMarkdownFormatting('_italic text_')).toBe('italic text');
    });

    test('removes multiple formatting', () => {
      expect(cleanMarkdownFormatting('**bold** and *italic*')).toBe('bold and italic');
    });

    test('handles empty or null input', () => {
      expect(cleanMarkdownFormatting('')).toBe('');
      expect(cleanMarkdownFormatting(null)).toBe(null);
      expect(cleanMarkdownFormatting(undefined)).toBe(undefined);
    });
  });

  describe('cleanAIResponse', () => {
    test('removes common AI formatting patterns', () => {
      expect(cleanAIResponse('**Instead of:** "old text"')).toBe('Instead of: "old text"');
      expect(cleanAIResponse('**Try:** something new')).toBe('Try: something new');
      expect(cleanAIResponse('**Consider:** this option')).toBe('Consider: this option');
    });

    test('removes bold formatting around common phrases', () => {
      expect(cleanAIResponse('**Here\'s** a suggestion')).toBe('Here\'s a suggestion');
      expect(cleanAIResponse('**You could** try this')).toBe('You could try this');
    });

    test('handles complex AI responses', () => {
      const input = '**Instead of:** "The cat sat" **try:** "The cat perched gracefully"';
      const expected = 'Instead of: "The cat sat" try: "The cat perched gracefully"';
      expect(cleanAIResponse(input)).toBe(expected);
    });

    test('preserves content without markdown', () => {
      const input = 'This is a normal sentence without any formatting.';
      expect(cleanAIResponse(input)).toBe(input);
    });
  });

  describe('formatTextForDisplay', () => {
    test('cleans markdown by default', () => {
      const input = '**Bold text** with *italic*';
      const expected = 'Bold text with italic';
      expect(formatTextForDisplay(input)).toBe(expected);
    });

    test('respects cleanMarkdown option', () => {
      const input = '**Bold text**';
      expect(formatTextForDisplay(input, { cleanMarkdown: false })).toBe('**Bold text**');
      expect(formatTextForDisplay(input, { cleanMarkdown: true })).toBe('Bold text');
    });

    test('truncates text when maxLength specified', () => {
      const input = 'This is a very long text that should be truncated';
      const result = formatTextForDisplay(input, { maxLength: 20 });
      expect(result).toBe('This is a very long ...');
      expect(result.length).toBe(23); // 20 + '...'
    });
  });
});

// Manual test examples for console testing
export const testExamples = {
  aiResponses: [
    '**Instead of:** "The cat sat on the mat" **try:** "The cat perched elegantly on the woven mat"',
    '**Consider:** Adding more descriptive language to enhance the scene.',
    '**Here\'s** a suggestion: **Try** using more vivid imagery.',
    '**Tip:** Show, don\'t tell when describing emotions.',
    'Normal text without any markdown formatting.'
  ],
  
  markdownText: [
    '**Bold text** and *italic text*',
    '# Header\n## Subheader\n### Small header',
    '`inline code` and ```code block```',
    '> Blockquote text',
    '- List item 1\n- List item 2',
    '~~strikethrough~~ text'
  ]
};

// Console test function
export const runManualTests = () => {
  console.log('=== AI Response Cleaning Tests ===');
  testExamples.aiResponses.forEach((text, index) => {
    console.log(`\nTest ${index + 1}:`);
    console.log('Original:', text);
    console.log('Cleaned: ', cleanAIResponse(text));
  });

  console.log('\n=== Markdown Cleaning Tests ===');
  testExamples.markdownText.forEach((text, index) => {
    console.log(`\nTest ${index + 1}:`);
    console.log('Original:', text);
    console.log('Cleaned: ', cleanMarkdownFormatting(text));
  });
};

// Uncomment to run manual tests in browser console
// runManualTests();
