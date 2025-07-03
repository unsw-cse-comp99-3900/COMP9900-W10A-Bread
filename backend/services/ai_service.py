"""
AI Service for writing assistance
"""
import openai
import google.generativeai as genai
import time
import asyncio
from typing import List, Dict, Any, Optional
from core.config import settings
from core.ai_config import AIConfig
from core.age_groups import AgeGroupConfig, AgeGroup
from .mock_ai_service import mock_ai_service

class AIService:
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        self.config = AIConfig

        if settings.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(
                    api_key=settings.openai_api_key,
                    timeout=self.config.OPENAI_TIMEOUT
                )
            except Exception:
                pass

        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                pass

    def _select_best_model(self, task_type: str, text_length: int = 0) -> str:
        """
        Intelligently select the best AI model based on task type and context

        Args:
            task_type: Type of task ('creative', 'analysis', 'continue', 'improve', 'chat')
            text_length: Length of input text for context

        Returns:
            'openai' or 'gemini' based on optimal choice for the task
        """
        # Creative writing and story continuation: Gemini excels at creative tasks
        if task_type in ['creative', 'continue', 'writing_prompts']:
            if self.gemini_client:
                return 'gemini'
            elif self.openai_client:
                return 'openai'

        # Analysis and improvement: OpenAI better for structured analysis
        elif task_type in ['analysis', 'improve', 'fix']:
            if self.openai_client:
                return 'openai'
            elif self.gemini_client:
                return 'gemini'

        # Chat and general assistance: Use available service
        elif task_type == 'chat':
            if self.openai_client:
                return 'openai'
            elif self.gemini_client:
                return 'gemini'

        # Default fallback: prefer OpenAI for consistency
        if self.openai_client:
            return 'openai'
        elif self.gemini_client:
            return 'gemini'

        return 'mock'  # Fallback to mock service
    
    def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None, task_type: str = 'chat') -> str:
        """Chat with AI assistant using intelligent model selection"""
        if not self.openai_client and not self.gemini_client:
            print("⚠️  No AI service configured, using mock AI service for demonstration")
            return mock_ai_service.chat(messages, context)

        # Add context to the conversation if provided
        if context:
            system_message = {
                "role": "system",
                "content": f"You are a creative writing assistant. Here's the context: {context}"
            }
            messages = [system_message] + messages

        # Select the best model for this task
        preferred_model = self._select_best_model(task_type)

        # Try preferred model first, then fallback
        if preferred_model == 'openai' and self.openai_client:
            try:
                response = self._chat_openai(messages)
                print(f"✅ Used OpenAI for {task_type} task")
                return response
            except Exception as e:
                print(f"OpenAI failed: {str(e)}, trying Gemini...")
                if self.gemini_client:
                    try:
                        response = self._chat_gemini(messages)
                        print(f"✅ Used Gemini as fallback for {task_type} task")
                        return response
                    except Exception as e2:
                        print(f"Gemini also failed: {str(e2)}")

        elif preferred_model == 'gemini' and self.gemini_client:
            try:
                response = self._chat_gemini(messages)
                print(f"✅ Used Gemini for {task_type} task")
                return response
            except Exception as e:
                print(f"Gemini failed: {str(e)}, trying OpenAI...")
                if self.openai_client:
                    try:
                        response = self._chat_openai(messages)
                        print(f"✅ Used OpenAI as fallback for {task_type} task")
                        return response
                    except Exception as e2:
                        print(f"OpenAI also failed: {str(e2)}")

        # If all services failed, use mock service as fallback
        print("⚠️  All AI services failed, using mock AI service for demonstration")
        return mock_ai_service.chat(messages, context)
    
    def _chat_openai(self, messages: List[Dict[str, str]]) -> str:
        """Chat using OpenAI with retry mechanism"""
        last_error = None

        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE,
                    timeout=self.config.OPENAI_TIMEOUT
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                error_str = str(e)

                # 使用配置判断是否应该重试
                if not self.config.should_retry(error_str):
                    raise Exception(f"OpenAI API error: {error_str}")

                # 如果可以重试且不是最后一次尝试
                if attempt < self.config.MAX_RETRIES - 1:
                    print(f"OpenAI attempt {attempt + 1} failed: {error_str}, retrying in {self.config.RETRY_DELAY} seconds...")
                    time.sleep(self.config.RETRY_DELAY)
                    continue

        raise Exception(f"OpenAI API error after {self.config.MAX_RETRIES} attempts: {str(last_error)}")
    
    def _chat_gemini(self, messages: List[Dict[str, str]]) -> str:
        """Chat using Google Gemini with retry mechanism"""
        last_error = None

        for attempt in range(self.config.MAX_RETRIES):
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

                # Generate response with timeout handling
                response = self.gemini_client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config.MAX_TOKENS,
                        temperature=self.config.TEMPERATURE,
                    )
                )
                return response.text

            except Exception as e:
                last_error = e
                error_str = str(e)

                # 使用配置判断是否应该重试
                if not self.config.should_retry(error_str):
                    raise Exception(f"Gemini API error: {error_str}")

                # 如果可以重试且不是最后一次尝试
                if attempt < self.config.MAX_RETRIES - 1:
                    print(f"Gemini attempt {attempt + 1} failed: {error_str}, retrying in {self.config.RETRY_DELAY} seconds...")
                    time.sleep(self.config.RETRY_DELAY)
                    continue

        raise Exception(f"Gemini API error after {self.config.MAX_RETRIES} attempts: {str(last_error)}")
    
    def writing_assistance(self, text: str, assistance_type: str, user_age_group: Optional[str] = None) -> Dict[str, Any]:
        """Provide age-appropriate writing assistance"""
        # Get age group configuration
        age_group_config = None
        if user_age_group:
            try:
                age_group_enum = AgeGroup(user_age_group)
                age_group_config = AgeGroupConfig.get_config(age_group_enum)
            except ValueError:
                # Invalid age group, use default
                age_group_config = AgeGroupConfig.get_config(AgeGroup.LATE_PRIMARY)
        else:
            # Default to late primary if no age group specified
            age_group_config = AgeGroupConfig.get_config(AgeGroup.LATE_PRIMARY)

        # Create age-appropriate prompts
        prompts = self._create_age_appropriate_prompts(text, age_group_config)

        prompt = prompts.get(assistance_type, prompts["improve"])

        # Create age-appropriate system message
        system_content = f"You are a professional writing assistant. {age_group_config.get('prompt_prefix', '')}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        # Use intelligent model selection based on assistance type
        response = self.chat(messages, task_type=assistance_type)
        
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
            "suggestions": suggestions[:age_group_config.get('max_suggestions', 5)],
            "assistance_type": assistance_type,
            "age_group": user_age_group
        }

    def _create_age_appropriate_prompts(self, text: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Create age-appropriate prompts based on configuration"""
        focus_areas = config.get("focus_areas", ["writing skills"])
        encouragement_style = config.get("encouragement_style", "positive")
        feedback_complexity = config.get("feedback_complexity", "intermediate")

        # Base prompts adapted for age group
        prompts = {
            "improve": self._create_expression_enhancement_prompt(text, config),

            "continue": self._create_continue_writing_prompt(text, config),

            "summarize": f"Please provide a summary of the following text using {feedback_complexity} language:\n\n{text}",

            "analyze": self._create_age_appropriate_analysis_prompt(text, config),

            # New modular analysis functions
            "structure": self._create_structure_analysis_prompt(text, config),
            "style": self._create_style_analysis_prompt(text, config),
            "creativity": self._create_creativity_suggestions_prompt(text, config)
        }

        return prompts

    def _create_expression_enhancement_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create age-appropriate expression enhancement prompt"""
        focus_areas = config.get("focus_areas", ["writing skills"])
        encouragement_style = config.get("encouragement_style", "positive")
        feedback_complexity = config.get("feedback_complexity", "intermediate")

        if feedback_complexity == "very simple":
            return f"""Help make this writing better by suggesting improvements to:

🎯 **Word Choice**: Suggest better, more interesting words
✨ **Sentence Style**: Help make sentences flow better
📝 **Expression**: Show how to express ideas more clearly

Please give specific suggestions, not rewritten text. Help the writer learn by explaining WHY each suggestion would improve their writing.

Text to enhance:
{text}

Remember: Give suggestions and tips, don't rewrite the text!"""

        elif feedback_complexity == "simple":
            return f"""Please provide {encouragement_style} suggestions to enhance the expression in this text, focusing on {', '.join(focus_areas[:3])}:

**What to focus on:**
1. **Word Choice & Vocabulary**: Suggest more vivid, precise, or age-appropriate words
2. **Sentence Structure**: Recommend ways to vary sentence length and style
3. **Clarity of Expression**: Help make ideas clearer and more engaging

**Important**: Provide specific improvement suggestions and explain why they would help, rather than rewriting the text. Help the student develop their own writing voice.

Text:
{text}"""

        else:  # intermediate and advanced
            return f"""Provide constructive suggestions to enhance the expression and style of this text, focusing on {', '.join(focus_areas)}:

**Enhancement Areas:**
1. **Vocabulary & Word Choice**: Suggest more precise, vivid, or sophisticated vocabulary
2. **Sentence Variety**: Recommend improvements to sentence structure and rhythm
3. **Style & Voice**: Help develop a stronger, more engaging writing voice
4. **Clarity & Flow**: Suggest ways to improve logical flow and readability

**Guidelines:**
- Provide specific, actionable suggestions rather than rewriting
- Explain the reasoning behind each suggestion
- Focus on helping the writer develop their skills
- Maintain the writer's original voice and intent
- Use {encouragement_style} and constructive language

Text to enhance:
{text}"""

    def _create_continue_writing_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create age-appropriate continue writing prompt with limited output"""
        focus_areas = config.get("focus_areas", ["writing skills"])
        encouragement_style = config.get("encouragement_style", "positive")
        feedback_complexity = config.get("feedback_complexity", "intermediate")

        if feedback_complexity == "very simple":
            return f"""Help the writer continue their story with just 1-2 sentences that:

🎯 **Keep the story going**: Add what might happen next
✨ **Match the style**: Use similar words and tone
📝 **Give ideas**: Help the writer think of what to write next

**IMPORTANT**: Write only 1-2 sentences (maximum 30 words) to help with writer's block, not to replace the student's writing.

Text to continue:
{text}

Remember: Just 1-2 short sentences to spark ideas!"""

        elif feedback_complexity == "simple":
            return f"""Please provide 1-2 sentences (maximum 40 words) to help continue this text, focusing on {', '.join(focus_areas[:2])}:

**Guidelines:**
- Write only 1-2 sentences to help overcome writer's block
- Match the existing tone and style
- Provide inspiration, not replacement text
- Keep it {encouragement_style} and age-appropriate

**Purpose**: Help the student get unstuck, not write their story for them.

Text:
{text}

Continue with just 1-2 sentences:"""

        else:  # intermediate and advanced
            return f"""Provide 1-2 sentences (maximum 50 words) to help continue this text, focusing on {', '.join(focus_areas[:2])}:

**Continuation Guidelines:**
- **Brevity**: Maximum 1-2 sentences to spark creativity
- **Consistency**: Maintain the established tone, style, and narrative voice
- **Inspiration**: Provide a creative nudge, not a complete continuation
- **Student Agency**: Help overcome writer's block while preserving the student's ownership

**Goal**: Offer just enough to help the writer move forward with their own ideas.

Text to continue:
{text}

Your 1-2 sentence continuation:"""

    def _create_structure_analysis_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create focused structure analysis prompt"""
        feedback_complexity = config.get("feedback_complexity", "intermediate")
        encouragement_style = config.get("encouragement_style", "positive")

        if feedback_complexity == "very simple":
            return f"""Look at how this text is organized and give {encouragement_style} tips:

🏗️ **Check the Structure:**
- Does it have a good beginning?
- Do the ideas connect well?
- Is it easy to follow?

Give 2-3 simple tips to make the structure better.

Text:
{text}"""

        elif feedback_complexity == "simple":
            return f"""Please give {encouragement_style} feedback on the structure of this text:

**Focus on:**
1. **Organization**: How well are ideas arranged?
2. **Flow**: Do sentences and paragraphs connect smoothly?
3. **Beginning and Ending**: Are they clear and effective?

Provide 3-4 specific suggestions to improve the structure.

Text:
{text}"""

        else:  # intermediate and advanced
            return f"""Analyze the structural elements of this text and provide {encouragement_style} feedback:

**Structure Analysis:**
1. **Overall Organization**: How effectively are ideas arranged and developed?
2. **Paragraph Structure**: Are paragraphs well-formed with clear topic sentences?
3. **Transitions**: How well do ideas flow from one to the next?
4. **Introduction/Conclusion**: How effectively do they frame the content?

**Guidelines:**
- Provide specific, actionable suggestions
- Focus on structural improvements only
- Keep feedback concise and focused
- Use {encouragement_style} language

Text:
{text}"""

    def _create_style_analysis_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create focused style analysis prompt"""
        feedback_complexity = config.get("feedback_complexity", "intermediate")
        encouragement_style = config.get("encouragement_style", "positive")

        if feedback_complexity == "very simple":
            return f"""Look at the writing style and give {encouragement_style} tips:

✨ **Check the Style:**
- Are the words interesting?
- Do sentences sound good?
- Is it fun to read?

Give 2-3 simple tips to make the style better.

Text:
{text}"""

        elif feedback_complexity == "simple":
            return f"""Please give {encouragement_style} feedback on the writing style:

**Focus on:**
1. **Word Choice**: Are words interesting and appropriate?
2. **Sentence Variety**: Are sentences different lengths and types?
3. **Voice**: Does the writing sound like the author?

Provide 3-4 specific suggestions to improve the style.

Text:
{text}"""

        else:  # intermediate and advanced
            return f"""Analyze the stylistic elements of this text and provide {encouragement_style} feedback:

**Style Analysis:**
1. **Voice & Tone**: How consistent and engaging is the writing voice?
2. **Sentence Variety**: How effectively does the writer vary sentence structure?
3. **Word Choice**: How precise and engaging is the vocabulary?
4. **Rhythm & Flow**: How well does the text read aloud?

**Guidelines:**
- Focus on style elements only
- Provide specific examples from the text
- Suggest concrete improvements
- Keep feedback encouraging and constructive

Text:
{text}"""

    def _create_creativity_suggestions_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create creativity and development suggestions prompt"""
        feedback_complexity = config.get("feedback_complexity", "intermediate")
        encouragement_style = config.get("encouragement_style", "positive")

        if feedback_complexity == "very simple":
            return f"""Give {encouragement_style} ideas to make this writing more creative:

🎨 **Creative Ideas:**
- What could make it more interesting?
- What details could be added?
- What could happen next?

Give 2-3 fun ideas to make the writing better.

Text:
{text}"""

        elif feedback_complexity == "simple":
            return f"""Please suggest {encouragement_style} ways to develop this text creatively:

**Creative Development:**
1. **Details**: What interesting details could be added?
2. **Characters**: How could characters be more interesting?
3. **Plot**: What exciting things could happen?

Provide 3-4 creative suggestions to enhance the writing.

Text:
{text}"""

        else:  # intermediate and advanced
            return f"""Provide {encouragement_style} suggestions for creative development and enhancement:

**Creative Development Areas:**
1. **Character Development**: How could characters be more complex or interesting?
2. **Setting & Atmosphere**: How could the environment be more vivid or meaningful?
3. **Plot Development**: What creative directions could the narrative take?
4. **Thematic Depth**: How could deeper themes or meanings be explored?

**Guidelines:**
- Focus on creative possibilities, not corrections
- Suggest specific enhancements
- Encourage the writer's imagination
- Provide inspiring, actionable ideas

Text:
{text}"""

    def _create_age_appropriate_analysis_prompt(self, text: str, config: Dict[str, Any]) -> str:
        """Create age-appropriate analysis prompt"""
        focus_areas = config.get("focus_areas", ["writing skills"])
        encouragement_style = config.get("encouragement_style", "positive")
        feedback_complexity = config.get("feedback_complexity", "intermediate")

        if feedback_complexity == "very simple":
            return f"""Please look at this text and give {encouragement_style} suggestions about {', '.join(focus_areas[:2])}.

Help the writer make their text better by focusing on:
- Making sentences clear and easy to read
- Using good words
- Making the story interesting

Text:
{text}"""

        elif feedback_complexity == "simple":
            return f"""Please analyze this text and provide {encouragement_style} feedback focusing on {', '.join(focus_areas[:3])}:

1. **Writing Clarity**: Are the sentences easy to understand?
2. **Word Choice**: Are the words used well?
3. **Story Flow**: Does the text flow nicely?

Please give helpful suggestions to make the writing better.

Text:
{text}"""

        elif feedback_complexity == "intermediate":
            return f"""Please analyze this text focusing on {', '.join(focus_areas)} and provide {encouragement_style} feedback:

1. **Structure**: How well is the text organized?
2. **Language**: How effective is the word choice and sentence variety?
3. **Content**: How well are ideas developed and expressed?
4. **Reader Experience**: How engaging and clear is the text?

Provide specific suggestions for improvement.

Text:
{text}"""

        else:  # advanced
            return f"""Please provide a comprehensive analysis of this text focusing on {', '.join(focus_areas)}:

1. **Structural Analysis**: Examine organization, flow, and logical development
2. **Linguistic Analysis**: Evaluate style, tone, vocabulary, and syntax
3. **Content Analysis**: Assess depth, originality, and effectiveness of arguments
4. **Critical Evaluation**: Consider audience, purpose, and overall impact

Provide detailed, constructive feedback with specific examples and actionable recommendations.

Text:
{text}"""
