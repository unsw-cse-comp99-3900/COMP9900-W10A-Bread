"""
Writing Prompts Service - Provides age-appropriate writing guidance based on project names
"""

from typing import List, Dict, Optional
from core.age_groups import AgeGroup, AgeGroupConfig
import re

class WritingPromptsService:
    """Service for generating age-appropriate writing prompts and guidance"""
    
    # Project name keywords and their associated themes
    PROJECT_THEMES = {
        'adventure': ['journey', 'exploration', 'discovery', 'quest', 'travel'],
        'fantasy': ['magic', 'wizard', 'dragon', 'fairy', 'kingdom', 'spell'],
        'mystery': ['detective', 'clue', 'secret', 'puzzle', 'investigation'],
        'friendship': ['friend', 'buddy', 'companion', 'team', 'together'],
        'family': ['mom', 'dad', 'sister', 'brother', 'grandma', 'grandpa', 'family'],
        'school': ['school', 'teacher', 'classroom', 'student', 'homework'],
        'animal': ['dog', 'cat', 'pet', 'zoo', 'farm', 'wild', 'animal'],
        'space': ['space', 'planet', 'star', 'rocket', 'astronaut', 'alien'],
        'nature': ['forest', 'ocean', 'mountain', 'garden', 'tree', 'flower'],
        'sports': ['game', 'team', 'play', 'win', 'sport', 'ball', 'race'],
        'food': ['cook', 'eat', 'recipe', 'kitchen', 'meal', 'restaurant'],
        'holiday': ['christmas', 'birthday', 'vacation', 'celebration', 'party']
    }
    
    @classmethod
    def detect_project_theme(cls, project_name: str) -> Optional[str]:
        """Detect the main theme of a project based on its name"""
        if not project_name:
            return None
            
        project_name_lower = project_name.lower()
        
        # Check for direct theme matches
        for theme, keywords in cls.PROJECT_THEMES.items():
            for keyword in keywords:
                if keyword in project_name_lower:
                    return theme
        
        return None
    
    @classmethod
    def get_writing_prompts(cls, project_name: str, age_group: str) -> Dict[str, any]:
        """Get age-appropriate writing prompts based on project name and age group"""
        try:
            age_group_enum = AgeGroup(age_group) if age_group else AgeGroup.UPPER_PRIMARY
        except ValueError:
            age_group_enum = AgeGroup.UPPER_PRIMARY
        
        config = AgeGroupConfig.get_config(age_group_enum)
        theme = cls.detect_project_theme(project_name)
        
        prompts = cls._generate_prompts_by_age_and_theme(age_group_enum, theme, project_name, config)
        
        return {
            "prompts": prompts,
            "theme": theme,
            "age_group": age_group,
            "project_name": project_name
        }
    
    @classmethod
    def _generate_prompts_by_age_and_theme(cls, age_group: AgeGroup, theme: Optional[str], 
                                         project_name: str, config: Dict) -> List[Dict[str, str]]:
        """Generate specific prompts based on age group and theme"""
        
        if age_group == AgeGroup.EARLY_YEARS:
            return cls._get_early_years_prompts(theme, project_name)
        elif age_group == AgeGroup.LOWER_PRIMARY:
            return cls._get_lower_primary_prompts(theme, project_name)
        elif age_group == AgeGroup.UPPER_PRIMARY:
            return cls._get_upper_primary_prompts(theme, project_name)
        elif age_group == AgeGroup.LOWER_SECONDARY:
            return cls._get_lower_secondary_prompts(theme, project_name)
        else:  # UPPER_SECONDARY
            return cls._get_upper_secondary_prompts(theme, project_name)
    
    @classmethod
    def _get_early_years_prompts(cls, theme: Optional[str], project_name: str) -> List[Dict[str, str]]:
        """Writing prompts for early years children (3-5 years, Preschool/Prep)"""
        base_prompts = [
            {
                "title": "Start with What You See",
                "guidance": "Look around you! What do you see? Start by writing about one thing you can see right now.",
                "example": "Try: 'I see a...' or 'There is a...'"
            },
            {
                "title": "Tell About Your Day",
                "guidance": "What did you do today? Pick one fun thing and tell us about it!",
                "example": "Try: 'Today I...' or 'I like to...'"
            },
            {
                "title": "Your Favorite Things",
                "guidance": "What makes you happy? Write about something you really, really like!",
                "example": "Try: 'My favorite...' or 'I love...'"
            }
        ]
        
        if theme == 'animal':
            base_prompts.insert(0, {
                "title": f"Animal Story for '{project_name}'",
                "guidance": "Think of your favorite animal! What does it look like? What sound does it make?",
                "example": "Try: 'The cat says...' or 'I saw a big...'"
            })
        elif theme == 'family':
            base_prompts.insert(0, {
                "title": f"Family Story for '{project_name}'",
                "guidance": "Who is in your family? What do you like to do together?",
                "example": "Try: 'My mom...' or 'We like to...'"
            })
        
        return base_prompts[:3]  # Limit to 3 for early years

    @classmethod
    def _get_lower_primary_prompts(cls, theme: Optional[str], project_name: str) -> List[Dict[str, str]]:
        """Writing prompts for lower primary students (6-9 years, Year 1-3)"""
        base_prompts = [
            {
                "title": "Create a Simple Story",
                "guidance": "Every story needs a beginning, middle, and end. Start with 'Once upon a time' or 'One day'.",
                "example": "Think: Who is your main character? What happens to them?"
            },
            {
                "title": "Describe with Details",
                "guidance": "Use your five senses! What do you see, hear, smell, taste, or feel?",
                "example": "Instead of 'big', try 'huge' or 'enormous'. Add colors and sounds!"
            },
            {
                "title": "Write About an Experience",
                "guidance": "Think of something exciting that happened to you. Tell it like a story with details!",
                "example": "Start with when and where it happened, then tell what you did."
            }
        ]
        
        if theme == 'adventure':
            base_prompts.insert(0, {
                "title": f"Adventure Planning for '{project_name}'",
                "guidance": "Every adventure needs a brave character and an exciting place to explore!",
                "example": "Think: Where will your character go? What will they find there?"
            })
        elif theme == 'school':
            base_prompts.insert(0, {
                "title": f"School Story for '{project_name}'",
                "guidance": "What happens at school? Think about classrooms, friends, and learning!",
                "example": "You could write about a special day, a new friend, or learning something cool."
            })
        
        return base_prompts[:4]  # Limit to 4 for lower primary

    @classmethod
    def _get_upper_primary_prompts(cls, theme: Optional[str], project_name: str) -> List[Dict[str, str]]:
        """Writing prompts for upper primary students (10-12 years, Year 4-6)"""
        base_prompts = [
            {
                "title": "Develop Character and Setting",
                "guidance": "Create interesting characters with personalities. Describe where your story takes place in detail.",
                "example": "What makes your character special? What does your setting look, sound, and feel like?"
            },
            {
                "title": "Build Conflict and Resolution",
                "guidance": "Every good story has a problem that needs solving. What challenge will your character face?",
                "example": "Think about obstacles, mysteries to solve, or goals to achieve."
            },
            {
                "title": "Use Dialogue and Action",
                "guidance": "Make your characters talk to each other! Show what they do, don't just tell us.",
                "example": "Instead of 'She was angry', try 'She slammed the door and shouted, \"That's not fair!\"'"
            },
            {
                "title": "Add Descriptive Language",
                "guidance": "Use metaphors, similes, and vivid adjectives to paint pictures with words.",
                "example": "Try comparing things: 'as quiet as a mouse' or 'the wind whispered through the trees'."
            }
        ]
        
        if theme == 'mystery':
            base_prompts.insert(0, {
                "title": f"Mystery Structure for '{project_name}'",
                "guidance": "Start with a puzzling event, add clues throughout, and reveal the solution at the end!",
                "example": "What's the mystery? Who are the suspects? What clues will help solve it?"
            })
        elif theme == 'fantasy':
            base_prompts.insert(0, {
                "title": f"Fantasy World-Building for '{project_name}'",
                "guidance": "Create a magical world with its own rules. What makes it different from our world?",
                "example": "Think about magical creatures, special powers, and enchanted places."
            })
        
        return base_prompts[:5]  # Limit to 5 for upper primary

    @classmethod
    def _get_lower_secondary_prompts(cls, theme: Optional[str], project_name: str) -> List[Dict[str, str]]:
        """Writing prompts for lower secondary students (12-15 years, Year 7-9)"""
        base_prompts = [
            {
                "title": "Develop Complex Characters",
                "guidance": "Create multi-dimensional characters with strengths, flaws, and clear motivations.",
                "example": "What drives your character? What are they afraid of? How do they change throughout the story?"
            },
            {
                "title": "Establish Theme and Message",
                "guidance": "What deeper meaning or lesson do you want to explore through your story?",
                "example": "Consider themes like friendship, courage, identity, or overcoming challenges."
            },
            {
                "title": "Master Plot Structure",
                "guidance": "Use rising action, climax, and falling action to create engaging narrative tension.",
                "example": "Build suspense gradually, create a turning point, then resolve the conflict satisfyingly."
            },
            {
                "title": "Experiment with Perspective",
                "guidance": "Try different points of view (first person, third person) and narrative voices.",
                "example": "How does the story change when told from different characters' perspectives?"
            }
        ]
        
        if theme == 'friendship':
            base_prompts.insert(0, {
                "title": f"Friendship Dynamics in '{project_name}'",
                "guidance": "Explore the complexities of relationships - loyalty, conflict, growth, and understanding.",
                "example": "How do friendships change us? What challenges test true friendship?"
            })
        
        return base_prompts[:6]  # Limit to 6 for lower secondary

    @classmethod
    def _get_upper_secondary_prompts(cls, theme: Optional[str], project_name: str) -> List[Dict[str, str]]:
        """Writing prompts for upper secondary students (16-18 years, Year 10-12)"""
        base_prompts = [
            {
                "title": "Explore Social Issues",
                "guidance": "Address contemporary issues through your narrative while maintaining engaging storytelling.",
                "example": "How can your story shed light on important social, environmental, or ethical questions?"
            },
            {
                "title": "Develop Unique Voice",
                "guidance": "Cultivate a distinctive writing style that reflects your personality and perspective.",
                "example": "What makes your writing voice unique? How do you want readers to feel when they read your work?"
            },
            {
                "title": "Use Advanced Literary Techniques",
                "guidance": "Incorporate symbolism, foreshadowing, irony, and other sophisticated literary devices.",
                "example": "How can objects, colors, or events represent deeper meanings in your story?"
            },
            {
                "title": "Create Authentic Dialogue",
                "guidance": "Write conversations that reveal character, advance plot, and sound natural.",
                "example": "How do different characters speak? What do their word choices reveal about them?"
            }
        ]
        
        return base_prompts[:7]  # Limit to 7 for upper secondary

# Create service instance
writing_prompts_service = WritingPromptsService()
