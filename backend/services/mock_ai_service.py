"""
Mock AI Service for testing when API quotas are exhausted
"""
from typing import List, Dict, Any, Optional
import random
import time
import re

class MockAIService:
    def __init__(self):
        self._init_responses()

    def _analyze_text_issues(self, text: str) -> List[str]:
        """Analyze specific issues in the text"""
        issues = []

        # Check text length
        if len(text) < 50:
            issues.append("Text is too short, content is insufficient")
        elif len(text) > 1000:
            issues.append("Text is too long, suggest paragraphing or simplification")

        # Check sentence length
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            if avg_length > 50:
                issues.append("Average sentence length is too long, affecting reading fluency")
            elif avg_length < 10:
                issues.append("Sentences are too short, expression may be incomplete")

        # Check repeated vocabulary (for both English and Chinese)
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)  # Extract words and Chinese characters
        if len(words) > 10:
            word_freq = {}
            for word in words:
                if len(word) > 1:  # Only consider words longer than 1 character
                    word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1

            repeated_words = [word for word, freq in word_freq.items() if freq > 3]
            if repeated_words:
                issues.append(f"Excessive word repetition: {', '.join(repeated_words[:3])}")

        # Check paragraph structure
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        if len(paragraphs) == 1 and len(text) > 200:
            issues.append("Lack of paragraph separation, suggest paragraphing to improve readability")

        # Check punctuation usage
        comma_count = text.count(',') + text.count('，')
        period_count = text.count('.') + text.count('。')
        if comma_count > period_count * 2:
            issues.append("Excessive comma usage, suggest appropriate use of periods")

        return issues

    def _init_responses(self):
        """初始化模拟回复"""
        self.mock_responses = {
            "improve": [
                "This is an improved version of the text with more fluent language and clearer expression.",
                "I have optimized your text to make it more attractive and readable.",
                "After polishing, this text is now more vivid and interesting."
            ],
            "continue": [
                "Next, the story takes an unexpected turn...",
                "Suddenly, a mysterious figure appears in the scene...",
                "As time passes, the protagonist begins to realize that things are not as simple as they appear on the surface..."
            ],
            "analyze": [
                "**Structure Issues**: Lack of effective transitions between paragraphs, suggest adding connecting words. **Language Issues**: Some sentences are too long, affecting reading fluency. **Improvement Suggestions**: Break down long sentences and add logical connections between paragraphs.",
                "**Content Depth**: Viewpoints are rather superficial, lacking specific evidence support. **Language Expression**: Word repetition is frequent. **Improvement Suggestions**: Add specific cases and use synonyms to replace repeated vocabulary.",
                "**Reader Experience**: Too many technical terms may affect understanding. **Text Structure**: Lacks subheadings or paragraphing. **Improvement Suggestions**: Add term explanations and use subheadings to improve readability.",
                "**Language Issues**: Monotonous sentence patterns, mostly declarative sentences. **Content Issues**: Lacks comparison and analysis. **Improvement Suggestions**: Use interrogative and exclamatory sentences for variety, add pros and cons analysis."
            ],
            "chat": [
                "As your AI writing assistant, I'm happy to help you improve your creative work.",
                "This is a very interesting idea! Let's explore how to develop it into a complete story.",
                "I suggest you could start with the character's inner conflict, which often creates compelling plots.",
                "Consider adding some unexpected plot twists, which will make your story more engaging to readers.",
                "Your writing style is unique. I suggest maintaining this personal characteristic while paying attention to plot pacing."
            ]
        }
    
    def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        """Mock AI chat"""
        # Simulate API call delay
        time.sleep(0.5)
        
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Choose appropriate response based on message content
        if "story" in user_message.lower() or "plot" in user_message.lower():
            responses = self.mock_responses["chat"]
        elif "character" in user_message.lower() or "protagonist" in user_message.lower():
            responses = [
                "Character development is the core of a story. I suggest giving your character a clear goal and obstacles.",
                "Consider adding some unique traits or habits to your character, which will make them more three-dimensional.",
                "Character backstories often provide rich material for plot development."
            ]
        elif "beginning" in user_message.lower() or "start" in user_message.lower():
            responses = [
                "A good beginning should immediately grab the reader's attention. You can start with an engaging scene.",
                "Consider starting with dialogue or action, which is more engaging than pure description.",
                "The beginning can set up a small suspense to make readers want to continue reading."
            ]
        else:
            responses = self.mock_responses["chat"]
        
        return random.choice(responses)
    
    def writing_assistance(self, text: str, assistance_type: str) -> Dict[str, Any]:
        """Mock writing assistance"""
        # Simulate API call delay
        time.sleep(0.8)

        if assistance_type == "analyze":
            # Use intelligent analysis function
            issues = self._analyze_text_issues(text)
            if issues:
                result = f"**Issues Found:**\n" + "\n".join(f"• {issue}" for issue in issues)
                result += "\n\n**Overall Assessment:** The text has some areas for improvement. Please make targeted modifications based on the issues above."
            else:
                result = "**Analysis Result:** The text is of good overall quality with clear structure and fluent expression. Consider further improvement in detail description and argument depth."
        elif assistance_type in self.mock_responses:
            result = random.choice(self.mock_responses[assistance_type])
        else:
            result = "I have analyzed your text, here are my suggestions..."
        
        suggestions = []
        if assistance_type == "analyze":
            # Provide targeted suggestions based on text length
            text_length = len(text)
            if text_length < 50:
                suggestions.extend([
                    "Text is too short, suggest expanding content depth",
                    "Add specific detail descriptions"
                ])
            elif text_length > 500:
                suggestions.extend([
                    "Text is long, check for redundant content",
                    "Consider using subheadings for paragraphing"
                ])

            suggestions.extend([
                "Check for grammar errors or typos",
                "Ensure each paragraph has a clear central idea",
                "Avoid using too much passive voice",
                "Add specific examples to support viewpoints",
                "Check if sentence length is appropriate, avoid too long or too short",
                "Ensure logical coherence with appropriate transitions between paragraphs"
            ])
        elif assistance_type == "improve":
            suggestions = [
                "Use more precise verbs to replace generic verbs",
                "Avoid repeating the same vocabulary",
                "Try using different sentence structures",
                "Pay attention to language rhythm and cadence",
                "Remove unnecessary modifiers"
            ]
        
        return {
            "result": result,
            "suggestions": suggestions
        }

# 创建全局实例
mock_ai_service = MockAIService()
