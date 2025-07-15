"""
Real-time AI Writing Suggestions API
Provides intelligent, contextual writing suggestions during the writing process
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import re
import hashlib
import asyncio
import google.generativeai as genai
import openai
import os
from core.age_groups import AgeGroup, AgeGroupConfig
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/api/realtime", tags=["Real-time Suggestions"])

# Initialize AI services with multiple Gemini API keys
openai_client = None
gemini_models = []
current_gemini_index = 0

try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key and not openai_api_key.startswith('#'):
        openai.api_key = openai_api_key
        openai_client = openai
        print("✅ OpenAI client initialized for real-time suggestions")
except Exception as e:
    print(f"⚠️ OpenAI initialization failed: {e}")

# Initialize multiple Gemini models with different API keys
def initialize_gemini_models():
    """Initialize Gemini models with multiple API keys"""
    global gemini_models
    gemini_models = []

    try:
        # Load API keys from environment
        gemini_keys = []
        print("🔍 Checking for Gemini API keys...")

        for i in range(1, 11):  # Load 10 API keys
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            print(f"🔑 GEMINI_API_KEY_{i}: {'Found' if key else 'Not found'}")
            if key and not key.startswith('#'):
                gemini_keys.append(key)
                print(f"✅ Added GEMINI_API_KEY_{i} to list")

        # Also try the main key for backward compatibility
        main_key = os.getenv('GEMINI_API_KEY')
        print(f"🔑 GEMINI_API_KEY: {'Found' if main_key else 'Not found'}")
        if main_key and not main_key.startswith('#') and main_key not in gemini_keys:
            gemini_keys.append(main_key)
            print("✅ Added main GEMINI_API_KEY to list")

        print(f"📊 Total API keys found: {len(gemini_keys)}")

        if gemini_keys:
            for i, key in enumerate(gemini_keys):
                try:
                    # Create a model instance for each key
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    gemini_models.append({
                        'model': model,
                        'key': key,
                        'index': i + 1,
                        'quota_exceeded': False,
                        'last_error_time': 0
                    })
                    print(f"✅ Initialized Gemini model {i+1} for real-time suggestions")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Gemini model {i+1}: {e}")

            print(f"✅ Total {len(gemini_models)} Gemini models initialized for real-time suggestions")
        else:
            print("⚠️ No valid Gemini API keys found")
            gemini_models = []
    except Exception as e:
        print(f"⚠️ Gemini initialization failed: {e}")
        gemini_models = []

# Initialize models
initialize_gemini_models()

class RealtimeSuggestionRequest(BaseModel):
    text: str
    cursor_position: int
    text_before_cursor: Optional[str] = ""
    text_after_cursor: Optional[str] = ""
    current_paragraph: Optional[str] = ""
    age_group: Optional[str] = "upper_primary"
    context: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class SuggestionItem(BaseModel):
    id: str
    type: str  # "grammar", "vocabulary", "creativity", "structure", "detail"
    priority: int  # 1-5, 1 being highest priority
    message: str
    suggestion: Optional[str] = None
    position: Optional[int] = None
    category: str  # "enhancement", "correction", "inspiration"

class RealtimeSuggestionResponse(BaseModel):
    suggestions: List[SuggestionItem]
    analysis_time_ms: int
    should_show: bool
    next_check_delay: int  # seconds

class RealtimeSuggestionEngine:
    """Core engine for generating real-time writing suggestions"""

    def __init__(self):
        # Track recent suggestions to avoid repetition
        self.recent_suggestions = {}  # {user_session: [suggestion_ids]}
        self.suggestion_history = {}  # {user_session: {text_hash: suggestions}}
        self.conversation_context = {}  # {user_session: conversation_history}

        # Age group configurations for AI prompts
        self.age_configs = {
            "early_years": {
                "complexity": "very simple",
                "vocabulary": "basic words",
                "sentence_length": "short sentences",
                "encouragement": "very positive and exciting",
                "focus": ["basic vocabulary", "simple sentences", "picture-story connection"]
            },
            "lower_primary": {
                "complexity": "simple",
                "vocabulary": "elementary words",
                "sentence_length": "simple sentences",
                "encouragement": "positive and supportive",
                "focus": ["reading foundation", "short narratives", "daily life themes"]
            },
            "upper_primary": {
                "complexity": "intermediate",
                "vocabulary": "expanded vocabulary",
                "sentence_length": "varied sentences",
                "encouragement": "constructive and helpful",
                "focus": ["complex plots", "character interactions", "adventure themes"]
            },
            "lower_secondary": {
                "complexity": "intermediate-advanced",
                "vocabulary": "sophisticated words",
                "sentence_length": "complex sentences",
                "encouragement": "analytical and supportive",
                "focus": ["critical thinking", "long narratives", "social issues"]
            },
            "upper_secondary": {
                "complexity": "advanced",
                "vocabulary": "mature vocabulary",
                "sentence_length": "sophisticated sentences",
                "encouragement": "academic and inspiring",
                "focus": ["mature themes", "philosophical concepts", "advanced writing"]
            }
        }

        self.suggestion_templates = {
            "vocabulary": {
                "preschool": [
                    "Try using a describing word! Like 'big dog' or 'happy cat'",
                    "Can you tell us what color it is?",
                    "What sound does it make?"
                ],
                "early_primary": [
                    "Try adding an adjective to make this more interesting",
                    "Can you describe how it looks or feels?",
                    "What details can you add here?"
                ],
                "late_primary": [
                    "Consider using a more vivid adjective here",
                    "Try adding sensory details - what do you see, hear, or feel?",
                    "Can you use a simile or metaphor to describe this?"
                ],
                "early_middle": [
                    "Consider using more sophisticated vocabulary",
                    "Try varying your word choices to avoid repetition",
                    "Can you use figurative language to enhance this description?"
                ],
                "late_middle": [
                    "Explore more nuanced vocabulary choices",
                    "Consider the connotations of your word choices",
                    "Try using literary devices to strengthen your expression"
                ],
                "high_school": [
                    "Consider more precise or sophisticated vocabulary",
                    "Analyze the tone and register of your word choices",
                    "Explore advanced rhetorical techniques"
                ]
            },
            "structure": {
                "preschool": [
                    "What happens next in your story?",
                    "Can you tell us more about this?"
                ],
                "early_primary": [
                    "Try starting your next sentence differently",
                    "Can you add what happened next?",
                    "Maybe add 'then' or 'next' to connect your ideas"
                ],
                "late_primary": [
                    "Consider how this sentence connects to the previous one",
                    "Try varying your sentence beginnings",
                    "Can you add a transition word here?"
                ],
                "early_middle": [
                    "Consider the flow between your paragraphs",
                    "Try using transitional phrases to connect ideas",
                    "Think about the logical progression of your argument"
                ],
                "late_middle": [
                    "Analyze the coherence of your paragraph structure",
                    "Consider using more sophisticated transitional devices",
                    "Evaluate the logical flow of your ideas"
                ],
                "high_school": [
                    "Consider the rhetorical structure of your argument",
                    "Analyze the effectiveness of your paragraph organization",
                    "Evaluate the logical progression and coherence"
                ]
            },
            "creativity": {
                "preschool": [
                    "What do you think happens next?",
                    "Can you imagine something fun here?"
                ],
                "early_primary": [
                    "What if you added something surprising here?",
                    "Can you think of an interesting detail?",
                    "What would make this part more exciting?"
                ],
                "late_primary": [
                    "Consider adding dialogue to bring this scene to life",
                    "What emotions might your character be feeling?",
                    "Can you add an unexpected twist or detail?"
                ],
                "early_middle": [
                    "Explore the emotional depth of this moment",
                    "Consider multiple perspectives on this situation",
                    "What underlying themes could you develop here?"
                ],
                "late_middle": [
                    "Delve deeper into the psychological aspects",
                    "Consider the symbolic significance of this element",
                    "Explore the broader implications of this idea"
                ],
                "high_school": [
                    "Analyze the thematic complexity of this passage",
                    "Consider the philosophical implications",
                    "Explore the cultural or historical context"
                ]
            }
        }
    
    async def analyze_text(self, request: RealtimeSuggestionRequest) -> RealtimeSuggestionResponse:
        """Analyze text and generate real-time suggestions"""
        start_time = time.time()

        text = request.text.strip()
        if len(text) < 10:  # Too short to analyze
            return RealtimeSuggestionResponse(
                suggestions=[],
                analysis_time_ms=int((time.time() - start_time) * 1000),
                should_show=False,
                next_check_delay=3
            )

        # Create session ID and text hash for tracking
        session_id = request.user_preferences.get('session_id', 'default') if request.user_preferences else 'default'
        text_hash = hash(text)

        # Temporarily disable caching to debug the issue
        # Check if we've already analyzed this exact text
        # if session_id in self.suggestion_history:
        #     if text_hash in self.suggestion_history[session_id]:
        #         cached_response = self.suggestion_history[session_id][text_hash]
        #         print(f"🔄 Returning cached response for session {session_id}, text_hash {text_hash}")
        #         print(f"📋 Cached suggestions count: {len(cached_response.suggestions)}")
        #         print(f"📋 Cached should_show: {cached_response.should_show}")
        #         return cached_response

        print(f"🔍 Analyzing new text for session {session_id}, text_hash {text_hash}, length: {len(text)}")

        suggestions = []
        age_group = request.age_group or "upper_primary"

        # Get recent suggestions for this session to avoid repetition
        recent_suggestions = self.recent_suggestions.get(session_id, [])

        # Try AI-powered suggestion first, then fall back to enhanced rule-based
        ai_suggestion = await self._generate_ai_suggestion(text, age_group, session_id, request)
        print(f"🤖 AI suggestion result: {ai_suggestion}")
        if ai_suggestion:
            suggestions.append(ai_suggestion)
            print(f"✅ Added AI suggestion to list. Total suggestions: {len(suggestions)}")
        else:
            print(f"❌ No AI suggestion, trying fallback methods...")
            # Use enhanced contextual analysis
            contextual_suggestion = self._generate_contextual_suggestion(text, age_group, session_id, request)
            if contextual_suggestion:
                suggestions.append(contextual_suggestion)
                print(f"✅ Added contextual suggestion. Total suggestions: {len(suggestions)}")
            else:
                print(f"❌ No contextual suggestion, trying rule-based...")
                # Fall back to rule-based suggestions
                vocab_suggestions = self._check_vocabulary(text, age_group, recent_suggestions)
                struct_suggestions = self._check_structure(text, age_group, recent_suggestions)
                creativity_suggestions = self._check_creativity(text, age_group, recent_suggestions)
                grammar_suggestions = self._check_grammar(text, age_group, recent_suggestions)

                suggestions.extend(vocab_suggestions)
                suggestions.extend(struct_suggestions)
                suggestions.extend(creativity_suggestions)
                suggestions.extend(grammar_suggestions)

                print(f"📝 Rule-based suggestions: vocab={len(vocab_suggestions)}, struct={len(struct_suggestions)}, creativity={len(creativity_suggestions)}, grammar={len(grammar_suggestions)}")
                print(f"✅ Total suggestions after rule-based: {len(suggestions)}")

        # Filter out recently shown suggestions (but allow AI suggestions to always show)
        suggestions = [s for s in suggestions if s.type == "ai_suggestion" or s.type not in recent_suggestions[-3:]]

        print(f"🔍 After filtering: {len(suggestions)} suggestions remaining")

        # Sort by priority and limit to top 1 suggestion to reduce noise
        suggestions.sort(key=lambda x: x.priority)
        suggestions = suggestions[:1]

        # Update recent suggestions tracking
        if suggestions:
            if session_id not in self.recent_suggestions:
                self.recent_suggestions[session_id] = []
            self.recent_suggestions[session_id].extend([s.type for s in suggestions])
            # Keep only last 5 suggestions
            self.recent_suggestions[session_id] = self.recent_suggestions[session_id][-5:]

        analysis_time = int((time.time() - start_time) * 1000)

        response = RealtimeSuggestionResponse(
            suggestions=suggestions,
            analysis_time_ms=analysis_time,
            should_show=len(suggestions) > 0,
            next_check_delay=self._calculate_next_delay(suggestions)
        )

        # Temporarily disable caching to debug the issue
        # Cache the response only if it has suggestions
        # if len(suggestions) > 0:
        #     if session_id not in self.suggestion_history:
        #         self.suggestion_history[session_id] = {}
        #     self.suggestion_history[session_id][text_hash] = response
        #     print(f"💾 Cached response with {len(suggestions)} suggestions for session {session_id}")
        # else:
        #     print(f"🚫 Not caching empty response for session {session_id}")

        print(f"📤 Returning response with {len(suggestions)} suggestions, should_show: {len(suggestions) > 0}")

        return response

    def _generate_simple_ai_suggestion(self, text: str, age_group: str, session_id: str) -> Optional[SuggestionItem]:
        """Generate contextual AI suggestion based on text content and age group"""
        try:
            # Get age configuration
            age_config = self.age_configs.get(age_group, self.age_configs["upper_primary"])

            # Analyze text content for specific suggestions
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # Generate contextual suggestions based on content
            suggestion_text = self._create_contextual_suggestion(text, words, sentences, age_config)

            if suggestion_text:
                # Update conversation context
                if session_id not in self.conversation_context:
                    self.conversation_context[session_id] = []

                self.conversation_context[session_id].append({
                    "text": text,
                    "suggestion": suggestion_text,
                    "timestamp": time.time()
                })

                # Keep only last 5 interactions
                self.conversation_context[session_id] = self.conversation_context[session_id][-5:]

                return SuggestionItem(
                    id=f"ai_{int(time.time())}",
                    type="ai_suggestion",
                    priority=1,  # High priority for AI suggestions
                    message=suggestion_text,
                    category="enhancement"
                )
        except Exception as e:
            print(f"❌ AI suggestion generation failed: {e}")
            return None

        return None

    def _create_contextual_suggestion(self, text: str, words: List[str], sentences: List[str], age_config: Dict) -> Optional[str]:
        """Create contextual suggestion based on comprehensive text analysis"""

        # Get recent context to avoid repetition
        session_id = "default"  # This should be passed from the calling function
        recent_suggestions = self.recent_suggestions.get(session_id, [])

        if len(words) < 5:
            return f"Great start! Try adding more details to make your story {age_config['encouragement']}."

        # Analyze the last sentence for specific suggestions
        last_sentence = sentences[-1] if sentences else text
        last_words = last_sentence.split()

        # Check for specific content patterns with more context
        if len(sentences) == 1 and len(words) > 10:
            if age_config["complexity"] == "very simple":
                return "You wrote a nice long sentence! What happens next in your story?"
            elif age_config["complexity"] == "simple":
                return "Good sentence! Try adding another sentence to continue your story."
            else:
                return "Consider breaking this into two sentences for better flow."

        # Check for repetitive words with specific examples
        word_count = {}
        for word in words:
            if len(word) > 3:
                word_count[word.lower()] = word_count.get(word.lower(), 0) + 1

        repeated_words = [word for word, count in word_count.items() if count > 2]
        if repeated_words and "vocabulary" not in recent_suggestions[-2:]:
            repeated_word = repeated_words[0]
            if age_config["complexity"] == "very simple":
                return f"You used '{repeated_word}' a few times. Can you think of another word?"
            else:
                return f"Try using different words instead of repeating '{repeated_word}' - it makes writing more interesting!"

        # Check for lack of descriptive words
        descriptive_words = [w for w in words if w.lower() in ['big', 'small', 'beautiful', 'scary', 'happy', 'sad', 'bright', 'dark', 'loud', 'quiet', 'soft', 'hard', 'fast', 'slow']]
        if len(descriptive_words) == 0 and len(words) > 15 and "creativity" not in recent_suggestions[-2:]:
            if age_config["complexity"] == "very simple":
                return "Try adding words that tell us how things look or feel, like 'big' or 'pretty'!"
            else:
                return "Add descriptive words to help readers picture your story better."

        # Check for dialogue opportunities
        if '"' not in text and len(words) > 20 and "dialogue" not in recent_suggestions[-2:]:
            if age_config["complexity"] in ["simple", "intermediate"]:
                return "Your story could come alive with dialogue! Try adding what someone says."
            else:
                return "Consider adding dialogue to develop your characters and advance the plot."

        # Check for emotional content
        emotion_words = [w for w in words if w.lower() in ['happy', 'sad', 'excited', 'angry', 'scared', 'surprised', 'worried', 'proud', 'confused', 'amazed']]
        if len(emotion_words) == 0 and len(words) > 25 and "emotion" not in recent_suggestions[-2:]:
            if age_config["complexity"] == "very simple":
                return "How do the people in your story feel? Try adding feeling words!"
            else:
                return "Consider exploring your characters' emotions to create deeper connections."

        # Check for sentence variety
        if len(sentences) > 2:
            sentence_starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
            if len(set(sentence_starts)) < len(sentence_starts) * 0.7 and "structure" not in recent_suggestions[-2:]:
                return "Try starting your sentences in different ways to make your writing flow better."

        # Check for story progression
        action_words = [w for w in words if w.lower() in ['went', 'ran', 'walked', 'jumped', 'said', 'looked', 'found', 'saw', 'heard']]
        if len(action_words) < 2 and len(words) > 30:
            return "Try adding more action words to show what your characters are doing."

        # Default encouragement based on length and progress
        if len(words) > 50:
            return f"You're doing great! Your story is developing well. Keep adding details!"
        elif len(words) > 30:
            return "Good progress! Try adding more details about what you see, hear, or feel."

        return None

    async def _generate_ai_suggestion(self, text: str, age_group: str, session_id: str, request: RealtimeSuggestionRequest = None) -> Optional[SuggestionItem]:
        """Generate AI-powered writing suggestion using Gemini API"""
        try:
            # Get age configuration
            age_config = self.age_configs.get(age_group, self.age_configs["upper_primary"])

            # Get conversation context
            context = self.conversation_context.get(session_id, [])

            # Create AI prompt with enhanced context
            prompt = self._create_ai_suggestion_prompt(text, age_config, context, request)

            # Call Gemini API directly
            suggestion_text = await self._call_gemini_api(prompt)

            print(f"🔍 AI suggestion result: {suggestion_text[:100] if suggestion_text else 'None'}")

            if suggestion_text:
                # Update conversation context
                if session_id not in self.conversation_context:
                    self.conversation_context[session_id] = []

                self.conversation_context[session_id].append({
                    "text": text,
                    "suggestion": suggestion_text,
                    "timestamp": time.time()
                })

                # Keep only last 5 interactions
                self.conversation_context[session_id] = self.conversation_context[session_id][-5:]

                suggestion_item = SuggestionItem(
                    id=f"ai_{int(time.time())}",
                    type="ai_suggestion",
                    priority=1,  # High priority for AI suggestions
                    message=suggestion_text,
                    category="enhancement"
                )
                print(f"✅ Created AI suggestion item: {suggestion_item.message[:50]}...")
                return suggestion_item
            else:
                print(f"❌ No suggestion text returned from Gemini API")
        except Exception as e:
            print(f"❌ AI suggestion generation failed: {e}")
            # Fallback to simple suggestion if AI fails
            return self._generate_simple_ai_suggestion(text, age_group, session_id)

        return None

    def _create_ai_suggestion_prompt(self, text: str, age_config: Dict, context: List[Dict], request: RealtimeSuggestionRequest = None) -> str:
        """Create age-appropriate AI prompt for writing suggestions with full context analysis"""

        # Build context from previous interactions to avoid repetition
        previous_suggestions = []
        if context:
            previous_suggestions = [interaction.get('suggestion', '') for interaction in context[-3:]]

        complexity = age_config["complexity"]
        vocabulary = age_config["vocabulary"]
        encouragement = age_config["encouragement"]
        focus_areas = ", ".join(age_config["focus"])

        # Analyze text structure for better context
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        word_count = len(words)

        # Determine writing stage
        writing_stage = ""
        if word_count < 10:
            writing_stage = "just starting"
        elif word_count < 30:
            writing_stage = "early development"
        elif word_count < 100:
            writing_stage = "building the story"
        else:
            writing_stage = "developing details"

        # Add variety instructions
        variety_instruction = ""
        if previous_suggestions:
            variety_instruction = f"\n\nAVOID REPEATING: {'; '.join(previous_suggestions[:2])}"

        # Get enhanced context if available
        cursor_context = ""
        writing_position = ""
        current_focus = ""

        if request:
            cursor_pos = request.cursor_position or 0
            text_before = request.text_before_cursor or ""
            text_after = request.text_after_cursor or ""
            current_para = request.current_paragraph or ""

            writing_context = request.user_preferences.get('writing_context', {}) if request.user_preferences else {}
            is_at_end = writing_context.get('is_at_end', True)

            if is_at_end:
                writing_position = "at the end, continuing the story"
                current_focus = "what to write next"
            elif cursor_pos < len(text) * 0.3:
                writing_position = "near the beginning, setting up the story"
                current_focus = "establishing characters and setting"
            elif cursor_pos < len(text) * 0.7:
                writing_position = "in the middle, developing the story"
                current_focus = "building plot and character development"
            else:
                writing_position = "near the end, wrapping up"
                current_focus = "bringing the story to a conclusion"

            if current_para:
                cursor_context = f"\nCURRENT PARAGRAPH: '{current_para[:100]}...'"

        prompt = f"""You are an expert writing coach for {complexity} level students.

FULL TEXT ANALYSIS:
"{text}"
{cursor_context}

WRITING CONTEXT:
- Word count: {word_count}
- Sentences: {len(sentences)}
- Writing stage: {writing_stage}
- Current position: {writing_position}
- Focus area: {current_focus}
- Student level: {complexity}

TASK: Analyze the ENTIRE text and current writing position to give ONE specific, actionable suggestion for what to do RIGHT NOW.

REQUIREMENTS:
- Tone: {encouragement}
- Language: {vocabulary}
- Focus: {focus_areas}
- Length: 15-25 words maximum
- Be SPECIFIC to their actual content
- Consider their current writing position
- Help them with the immediate NEXT step{variety_instruction}

ANALYSIS PRIORITIES:
1. Where they are in their story (beginning/middle/end)
2. What they just wrote (current paragraph/sentence)
3. What would logically come next
4. Specific improvements for current content
5. Age-appropriate next steps

Give ONE specific, actionable tip for their current writing position:

Suggestion:"""

        return prompt

    async def _call_ai_service(self, prompt: str) -> Optional[str]:
        """Call AI service with fallback mechanism"""

        # Try Gemini first
        if gemini_model:
            try:
                response = gemini_model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}")

        # Try OpenAI as fallback
        if openai_client:
            try:
                response = openai_client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.7
                )
                if response and response.choices:
                    return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ OpenAI failed: {e}")

        # Fallback to template-based suggestion
        return None

    async def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call Gemini API with intelligent rotation across multiple keys"""
        global current_gemini_index

        if not gemini_models:
            print("⚠️ No Gemini models available for real-time suggestions")
            return None

        # Try up to 3 different API keys
        attempts = 0
        max_attempts = min(3, len(gemini_models))

        while attempts < max_attempts:
            try:
                # Get current model
                current_model_info = gemini_models[current_gemini_index]

                # Skip if this key recently had quota exceeded
                current_time = time.time()
                if (current_model_info['quota_exceeded'] and
                    current_time - current_model_info['last_error_time'] < 3600):  # Wait 1 hour
                    print(f"⏭️ Skipping Gemini key {current_model_info['index']} (quota exceeded)")
                    current_gemini_index = (current_gemini_index + 1) % len(gemini_models)
                    attempts += 1
                    continue

                print(f"🤖 Calling Gemini API (key {current_model_info['index']}) for real-time suggestion...")

                # Configure generation parameters for better suggestions
                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=50,
                    top_p=0.8,
                    top_k=40
                )

                # Reconfigure with current key
                genai.configure(api_key=current_model_info['key'])

                # Use asyncio.wait_for with timeout for non-blocking call
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        current_model_info['model'].generate_content,
                        prompt,
                        generation_config=generation_config
                    ),
                    timeout=10.0  # 10 second timeout for real-time suggestions
                )

                if response and response.text:
                    suggestion = response.text.strip()
                    # Clean up the suggestion
                    suggestion = suggestion.replace("Suggestion:", "").strip()
                    suggestion = suggestion.replace("Writing tip:", "").strip()

                    # Reset quota exceeded flag on success
                    current_model_info['quota_exceeded'] = False

                    print(f"✅ Gemini real-time suggestion (key {current_model_info['index']}): {suggestion}")

                    # Rotate to next key for next request
                    current_gemini_index = (current_gemini_index + 1) % len(gemini_models)

                    return suggestion
                else:
                    print(f"⚠️ Gemini key {current_model_info['index']} returned empty response")

            except asyncio.TimeoutError:
                print(f"⏰ Gemini key {current_model_info['index']} timed out")
                # Try next key
                current_gemini_index = (current_gemini_index + 1) % len(gemini_models)
                attempts += 1
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                    print(f"⚠️ Gemini key {current_model_info['index']} quota exceeded: {e}")
                    # Mark this key as quota exceeded
                    current_model_info['quota_exceeded'] = True
                    current_model_info['last_error_time'] = time.time()
                else:
                    print(f"❌ Gemini key {current_model_info['index']} API call failed: {e}")

                # Try next key
                current_gemini_index = (current_gemini_index + 1) % len(gemini_models)
                attempts += 1

        print(f"❌ All Gemini API attempts failed after {attempts} tries")
        return None
    
    def _check_vocabulary(self, text: str, age_group: str, recent_suggestions: List[str]) -> List[SuggestionItem]:
        """Check for vocabulary enhancement opportunities"""
        suggestions = []

        # Skip if vocabulary suggestions were recently shown
        if "vocabulary" in recent_suggestions[-2:]:
            return suggestions

        # Check for repetitive words
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = {}
        for word in words:
            if len(word) > 3:  # Only check meaningful words
                word_count[word] = word_count.get(word, 0) + 1

        repeated_words = [word for word, count in word_count.items() if count > 2]

        # More specific and varied suggestions
        if repeated_words and len(text) > 50:
            templates = self.suggestion_templates["vocabulary"].get(age_group, [])
            if templates:
                # Use the repeated word in the suggestion
                repeated_word = repeated_words[0]
                suggestions.append(SuggestionItem(
                    id=f"vocab_repeat_{int(time.time())}",
                    type="vocabulary",
                    priority=2,
                    message=f"You used '{repeated_word}' several times. {templates[0]}",
                    category="enhancement"
                ))

        # Check for lack of descriptive words
        adjectives = re.findall(r'\b(?:big|small|good|bad|nice|pretty|ugly|fast|slow)\b', text.lower())
        if len(adjectives) < len(text.split()) * 0.1 and len(text) > 30:
            templates = self.suggestion_templates["vocabulary"].get(age_group, [])
            if len(templates) > 1:
                suggestions.append(SuggestionItem(
                    id=f"desc_{int(time.time())}",
                    type="vocabulary",
                    priority=3,
                    message=templates[1],
                    category="enhancement"
                ))

        # Check for overuse of simple words
        simple_words = re.findall(r'\b(?:said|went|got|put|came|good|nice|fun)\b', text.lower())
        if len(simple_words) > 3 and len(text) > 60:
            templates = self.suggestion_templates["vocabulary"].get(age_group, [])
            if len(templates) > 2:
                suggestions.append(SuggestionItem(
                    id=f"simple_{int(time.time())}",
                    type="vocabulary",
                    priority=3,
                    message=templates[2] if len(templates) > 2 else templates[0],
                    category="enhancement"
                ))

        return suggestions
    
    def _check_structure(self, text: str, age_group: str, recent_suggestions: List[str]) -> List[SuggestionItem]:
        """Check for structural improvements"""
        suggestions = []

        # Skip if structure suggestions were recently shown
        if "structure" in recent_suggestions[-2:]:
            return suggestions

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) > 1:
            # Check for sentence variety
            sentence_starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
            repeated_starts = [start for start in sentence_starts if sentence_starts.count(start) > 1]

            if repeated_starts:
                templates = self.suggestion_templates["structure"].get(age_group, [])
                if templates:
                    repeated_start = repeated_starts[0]
                    suggestions.append(SuggestionItem(
                        id=f"struct_variety_{int(time.time())}",
                        type="structure",
                        priority=2,
                        message=f"You started several sentences with '{repeated_start}'. {templates[0]}",
                        category="enhancement"
                    ))

        # Check for very long sentences
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        if long_sentences and len(text) > 100:
            templates = self.suggestion_templates["structure"].get(age_group, [])
            if len(templates) > 1:
                suggestions.append(SuggestionItem(
                    id=f"struct_length_{int(time.time())}",
                    type="structure",
                    priority=3,
                    message=templates[1] if len(templates) > 1 else templates[0],
                    category="enhancement"
                ))

        return suggestions
    
    def _check_creativity(self, text: str, age_group: str, recent_suggestions: List[str]) -> List[SuggestionItem]:
        """Check for creativity enhancement opportunities"""
        suggestions = []

        # Skip if creativity suggestions were recently shown
        if "creativity" in recent_suggestions[-2:]:
            return suggestions

        # Check if text lacks emotional words
        emotional_words = re.findall(r'\b(?:happy|sad|excited|angry|scared|surprised|worried|proud|amazed|confused|delighted)\b', text.lower())
        dialogue_markers = re.findall(r'["\'].*?["\']', text)

        if len(emotional_words) == 0 and len(text) > 40:
            templates = self.suggestion_templates["creativity"].get(age_group, [])
            if templates:
                suggestions.append(SuggestionItem(
                    id=f"emotion_{int(time.time())}",
                    type="creativity",
                    priority=3,
                    message=templates[0] if len(templates) > 0 else "Consider adding emotions to your story",
                    category="inspiration"
                ))

        # Check for lack of dialogue
        elif len(dialogue_markers) == 0 and len(text) > 80:
            templates = self.suggestion_templates["creativity"].get(age_group, [])
            if len(templates) > 1:
                suggestions.append(SuggestionItem(
                    id=f"dialogue_{int(time.time())}",
                    type="creativity",
                    priority=4,
                    message=templates[1] if len(templates) > 1 else "Try adding some dialogue",
                    category="inspiration"
                ))

        # Check for lack of sensory details
        sensory_words = re.findall(r'\b(?:saw|heard|felt|smelled|tasted|bright|loud|soft|rough|sweet|sour)\b', text.lower())
        if len(sensory_words) < 2 and len(text) > 60:
            templates = self.suggestion_templates["creativity"].get(age_group, [])
            if len(templates) > 2:
                suggestions.append(SuggestionItem(
                    id=f"sensory_{int(time.time())}",
                    type="creativity",
                    priority=4,
                    message=templates[2] if len(templates) > 2 else "Try adding what you see, hear, or feel",
                    category="inspiration"
                ))

        return suggestions
    
    def _check_grammar(self, text: str, age_group: str, recent_suggestions: List[str]) -> List[SuggestionItem]:
        """Check for basic grammar issues"""
        suggestions = []

        # Grammar issues are always important, don't skip based on recent suggestions

        # Check for missing capitalization at sentence start
        sentences = re.split(r'[.!?]+', text)
        uncapitalized_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence[0].isupper():
                uncapitalized_sentences.append(sentence[:10] + "...")

        if uncapitalized_sentences:
            suggestions.append(SuggestionItem(
                id=f"cap_{int(time.time())}",
                type="grammar",
                priority=1,  # Highest priority
                message=f"Remember to start sentences with a capital letter (like '{uncapitalized_sentences[0]}')",
                category="correction"
            ))

        # Check for missing periods
        elif not text.strip().endswith(('.', '!', '?')) and len(text) > 20:
            suggestions.append(SuggestionItem(
                id=f"period_{int(time.time())}",
                type="grammar",
                priority=1,
                message="Don't forget to end your sentence with a period, exclamation mark, or question mark",
                category="correction"
            ))

        # Check for double spaces
        elif '  ' in text:
            suggestions.append(SuggestionItem(
                id=f"spaces_{int(time.time())}",
                type="grammar",
                priority=2,
                message="Try using just one space between words",
                category="correction"
            ))

        return suggestions
    
    def _calculate_next_delay(self, suggestions: List[SuggestionItem]) -> int:
        """Calculate when to check next based on suggestion priority"""
        if not suggestions:
            return 5  # Check again in 5 seconds
        
        highest_priority = min(s.priority for s in suggestions)
        if highest_priority == 1:  # Grammar issues
            return 2
        elif highest_priority == 2:  # Important suggestions
            return 4
        else:  # Enhancement suggestions
            return 6

# Initialize the suggestion engine
suggestion_engine = RealtimeSuggestionEngine()

@router.post("/suggestions", response_model=RealtimeSuggestionResponse)
async def get_realtime_suggestions(request: RealtimeSuggestionRequest):
    """
    Get real-time writing suggestions based on current text
    """
    try:
        response = await suggestion_engine.analyze_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.get("/api-status")
async def get_api_status():
    """
    Get status of all Gemini API keys
    """
    try:
        status = {
            "total_keys": len(gemini_models),
            "current_key_index": current_gemini_index + 1 if gemini_models else 0,
            "keys_status": []
        }

        current_time = time.time()
        for i, model_info in enumerate(gemini_models):
            key_status = {
                "key_index": model_info['index'],
                "quota_exceeded": model_info['quota_exceeded'],
                "last_error_time": model_info['last_error_time'],
                "available": not model_info['quota_exceeded'] or (current_time - model_info['last_error_time'] > 3600),
                "key_preview": f"{model_info['key'][:10]}...{model_info['key'][-4:]}"
            }
            status["keys_status"].append(key_status)

        available_keys = sum(1 for key in status["keys_status"] if key["available"])
        status["available_keys"] = available_keys

        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting API status: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for real-time suggestions service"""
    return {"status": "healthy", "service": "realtime-suggestions"}
