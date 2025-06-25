"""
AI Service for writing assistance
"""
import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from core.config import settings
from .mock_ai_service import mock_ai_service

class AIService:
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None

        if settings.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            except Exception:
                pass

        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        """Chat with AI assistant"""
        if not self.openai_client and not self.gemini_client:
            raise Exception("No AI service configured. Please set API keys.")

        # Add context to the conversation if provided
        if context:
            system_message = {
                "role": "system",
                "content": f"You are a creative writing assistant. Here's the context: {context}"
            }
            messages = [system_message] + messages

        # Try OpenAI first, then Gemini
        openai_error = None
        gemini_error = None

        if self.openai_client:
            try:
                response = self._chat_openai(messages)
                return response
            except Exception as e:
                openai_error = str(e)
                print(f"OpenAI failed: {openai_error}")

        if self.gemini_client:
            try:
                return self._chat_gemini(messages)
            except Exception as e:
                gemini_error = str(e)
                print(f"Gemini failed: {gemini_error}")

        # If both services failed, use mock service as fallback
        print("⚠️  All AI services failed, using mock AI service for demonstration")
        return mock_ai_service.chat(messages, context)
    
    def _chat_openai(self, messages: List[Dict[str, str]]) -> str:
        """Chat using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _chat_gemini(self, messages: List[Dict[str, str]]) -> str:
        """Chat using Google Gemini"""
        try:
            # Convert messages to Gemini format
            prompt_parts = []

            for msg in messages:
                if msg["role"] == "system":
                    prompt_parts.append(f"System: {msg['content']}")
                elif msg["role"] == "user":
                    prompt_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    prompt_parts.append(f"Assistant: {msg['content']}")

            # Combine all parts into a single prompt
            full_prompt = "\n\n".join(prompt_parts)

            # Generate response
            response = self.gemini_client.generate_content(full_prompt)
            return response.text

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def writing_assistance(self, text: str, assistance_type: str) -> Dict[str, Any]:
        """Provide writing assistance"""
        prompts = {
            "improve": f"Please improve the following text while maintaining its original meaning and style:\n\n{text}",
            "continue": f"Please continue the following text in a natural and engaging way:\n\n{text}",
            "summarize": f"Please provide a concise summary of the following text:\n\n{text}",
            "analyze": f"""Please carefully analyze the following text and provide specific improvement suggestions. Analyze from these aspects:

1. **Text Structure Issues**: Paragraph organization, logical flow, transitions
2. **Language Expression Issues**: Word accuracy, sentence variety, grammar errors
3. **Content Depth Issues**: Adequacy of arguments, richness of details, clarity of viewpoints
4. **Reader Experience Issues**: Readability, attractiveness, comprehension difficulty
5. **Specific Improvement Suggestions**: Provide actionable modification suggestions for identified problems

Please directly point out the problems without excessive praise, focusing on how to make the text better.

Text content:
{text}"""
        }
        
        prompt = prompts.get(assistance_type, prompts["improve"])
        
        messages = [
            {"role": "system", "content": "You are a professional writing assistant."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat(messages)
        
        # For analysis, provide specific improvement suggestions
        suggestions = []
        if assistance_type == "analyze":
            # Provide targeted suggestions based on text length and content
            text_length = len(text)
            if text_length < 100:
                suggestions.extend([
                    "Text is short, consider adding more details and descriptions",
                    "Add specific examples to support your points"
                ])
            elif text_length > 1000:
                suggestions.extend([
                    "Text is long, check for redundant content",
                    "Consider using paragraphs or subheadings to improve readability"
                ])

            # General improvement suggestions
            suggestions.extend([
                "Check if sentence patterns are too monotonous, try combining long and short sentences",
                "Ensure each paragraph has a clear theme",
                "Check for grammar errors or inappropriate word usage",
                "Consider readers' background knowledge and adjust expression difficulty",
                "Add transitional words to make paragraph connections more natural"
            ])
        
        return {
            "result": response,
            "suggestions": suggestions
        }
