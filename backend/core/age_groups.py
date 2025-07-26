"""
Age Group Configuration System - Provides appropriate AI writing suggestions for different age groups of children
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, date

class AgeGroup(Enum):
    """Age group enumeration"""
    EARLY_YEARS = "early_years"          # Ages 3-5: Preschool/Prep
    LOWER_PRIMARY = "lower_primary"      # Ages 6-9: Year 1-3
    UPPER_PRIMARY = "upper_primary"      # Ages 10-12: Year 4-6
    LOWER_SECONDARY = "lower_secondary"  # Ages 12-15: Year 7-9
    UPPER_SECONDARY = "upper_secondary"  # Ages 16-18: Year 10-12

class AgeGroupConfig:
    """Age group configuration class"""

    # Age group definitions
    AGE_RANGES = {
        AgeGroup.EARLY_YEARS: (3, 5),
        AgeGroup.LOWER_PRIMARY: (6, 9),
        AgeGroup.UPPER_PRIMARY: (10, 12),
        AgeGroup.LOWER_SECONDARY: (12, 15),
        AgeGroup.UPPER_SECONDARY: (16, 18),
    }

    # Age group display names
    AGE_GROUP_NAMES = {
        AgeGroup.EARLY_YEARS: "Early Years (Ages 3-5, Preschool/Prep)",
        AgeGroup.LOWER_PRIMARY: "Lower Primary (Ages 6-9, Year 1-3)",
        AgeGroup.UPPER_PRIMARY: "Upper Primary (Ages 10-12, Year 4-6)",
        AgeGroup.LOWER_SECONDARY: "Lower Secondary (Ages 12-15, Year 7-9)",
        AgeGroup.UPPER_SECONDARY: "Upper Secondary (Ages 16-18, Year 10-12)",
    }
    
    # AI suggestion configurations for each age group
    # Each configuration defines how AI should interact with children at different developmental stages
    AI_CONFIGS = {
        # Early Years (3-5): Preschool/Prep - Focus on basic literacy and imagination
        AgeGroup.EARLY_YEARS: {
            "language_level": "very_simple",  # Use basic vocabulary and short sentences
            "max_suggestions": 3,  # Limit suggestions to avoid overwhelming young children
            "focus_areas": ["Basic vocabulary", "Simple sentences", "Picture-story connection"],
            "encouragement_style": "Very encouraging and praising",  # Build confidence through positive reinforcement
            "feedback_complexity": "Very simple",  # Use concrete, easy-to-understand feedback
            # AI prompt prefix that sets the context for age-appropriate responses
            "prompt_prefix": "You are helping a 3-5 year old child in preschool/prep learn to write. Use simple, encouraging language with picture-story connections, ",
            "suggestion_types": ["Vocabulary suggestions", "Sentence improvement", "Imagination inspiration"],
            "avoid_topics": ["Complex grammar", "Advanced vocabulary", "Critical feedback"],  # Protect young learners from discouragement
            # Example prompts that demonstrate the encouraging, simple tone for this age group
            "example_prompts": [
                "That's a wonderful word! Can you think of other similar words?",
                "Your imagination is amazing! Can you tell me more about this story?",
                "This sentence is great! Let's make it even more fun together!"
            ]
        },

        AgeGroup.LOWER_PRIMARY: {
            "language_level": "simple",
            "max_suggestions": 4,
            "focus_areas": ["Reading foundation", "Short narratives", "Daily life themes", "Basic sentence structure"],
            "encouragement_style": "Positive encouragement",
            "feedback_complexity": "Simple",
            "prompt_prefix": "You are helping a 6-9 year old student in Year 1-3 improve their writing. Focus on building reading skills and short stories about daily life, ",
            "suggestion_types": ["Grammar correction", "Vocabulary replacement", "Sentence expansion", "Story development"],
            "avoid_topics": ["Complex rhetoric", "Deep analysis"],
            "example_prompts": [
                "You could try using this word instead - it will make your sentence more vivid!",
                "You could add an adjective here to help readers picture the scene better.",
                "Your story beginning is interesting! What happens next?"
            ]
        },

        AgeGroup.UPPER_PRIMARY: {
            "language_level": "intermediate",
            "max_suggestions": 5,
            "focus_areas": ["Complex plots", "Character interactions", "Chapter stories", "Adventure themes"],
            "encouragement_style": "Constructive encouragement",
            "feedback_complexity": "Intermediate",
            "prompt_prefix": "You are helping a 10-12 year old student in Year 4-6 improve their writing. Focus on complex plots and character development, ",
            "suggestion_types": ["Plot development", "Character building", "Chapter structure", "Adventure elements"],
            "avoid_topics": ["Overly complex literary theory"],
            "example_prompts": [
                "This character interaction is interesting! You could develop their relationship further.",
                "Your adventure plot is exciting! You could add more details about the setting.",
                "The chapter structure works well - consider adding a cliffhanger at the end."
            ]
        },
        
        AgeGroup.LOWER_SECONDARY: {
            "language_level": "intermediate_advanced",
            "max_suggestions": 6,
            "focus_areas": ["Critical thinking", "Long narratives", "Coming-of-age themes", "Social issues"],
            "encouragement_style": "Professional guidance",
            "feedback_complexity": "Intermediate-advanced",
            "prompt_prefix": "You are helping a 12-15 year old student in Year 7-9 improve their writing. Focus on developing critical thinking and exploring social themes, ",
            "suggestion_types": ["Critical analysis", "Narrative structure", "Theme development", "Social awareness"],
            "avoid_topics": ["Overly academic content"],
            "example_prompts": [
                "Your perspective on this social issue is thoughtful! You could explore different viewpoints.",
                "This coming-of-age theme is well-developed. Consider adding more emotional depth.",
                "Your critical thinking shows maturity. You could support your ideas with more examples."
            ]
        },
        
        AgeGroup.UPPER_SECONDARY: {
            "language_level": "advanced",
            "max_suggestions": 7,
            "focus_areas": ["Mature reading comprehension", "Advanced writing skills", "Youth themes", "Philosophical concepts"],
            "encouragement_style": "Inspirational guidance",
            "feedback_complexity": "Advanced",
            "prompt_prefix": "You are helping a 16-18 year old student in Year 10-12 improve their writing. Focus on mature themes and advanced writing techniques, ",
            "suggestion_types": ["Advanced analysis", "Personal style", "Philosophical exploration", "Complex narratives"],
            "avoid_topics": [],
            "example_prompts": [
                "Your exploration of this philosophical concept is sophisticated! You could develop it further.",
                "Your writing shows mature understanding. Consider exploring different narrative perspectives.",
                "You've handled complex themes well - this shows your advanced writing ability."
            ]
        }
    }
    
    @classmethod
    def get_age_group_by_age(cls, age: int) -> Optional[AgeGroup]:
        """
        Determine the appropriate age group based on a child's age.

        Args:
            age (int): The child's age in years

        Returns:
            Optional[AgeGroup]: The corresponding age group enum, or None if age is outside supported range

        Example:
            >>> AgeGroupConfig.get_age_group_by_age(7)
            <AgeGroup.LOWER_PRIMARY: 'lower_primary'>
        """
        for age_group, (min_age, max_age) in cls.AGE_RANGES.items():
            if min_age <= age <= max_age:
                return age_group
        return None

    @classmethod
    def get_age_group_by_birth_date(cls, birth_date: date) -> Optional[AgeGroup]:
        """
        Determine the appropriate age group based on a child's birth date.

        Calculates the current age and maps it to the appropriate developmental stage
        for AI writing assistance.

        Args:
            birth_date (date): The child's birth date

        Returns:
            Optional[AgeGroup]: The corresponding age group enum, or None if age is outside supported range

        Example:
            >>> from datetime import date
            >>> birth_date = date(2015, 6, 15)  # 8-year-old
            >>> AgeGroupConfig.get_age_group_by_birth_date(birth_date)
            <AgeGroup.LOWER_PRIMARY: 'lower_primary'>
        """
        today = date.today()
        # Calculate age accounting for whether birthday has occurred this year
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return cls.get_age_group_by_age(age)

    @classmethod
    def get_config(cls, age_group: AgeGroup) -> Dict:
        """
        Get the AI configuration settings for a specific age group.

        Returns the complete configuration dictionary containing language level,
        suggestion limits, focus areas, and other age-appropriate settings.

        Args:
            age_group (AgeGroup): The age group to get configuration for

        Returns:
            Dict: Configuration dictionary with AI assistance settings

        Note:
            If the age group is not found, defaults to UPPER_PRIMARY configuration
            to ensure the system always has a valid configuration.
        """
        return cls.AI_CONFIGS.get(age_group, cls.AI_CONFIGS[AgeGroup.UPPER_PRIMARY])

    @classmethod
    def get_all_age_groups(cls) -> List[Dict]:
        """
        Get information about all available age groups for UI display.

        Returns a list of dictionaries containing the value, display name,
        and age range for each supported age group.

        Returns:
            List[Dict]: List of age group information dictionaries

        Example:
            >>> groups = AgeGroupConfig.get_all_age_groups()
            >>> groups[0]
            {
                'value': 'early_years',
                'name': 'Early Years (Ages 3-5, Preschool/Prep)',
                'age_range': (3, 5)
            }
        """
        return [
            {
                "value": age_group.value,
                "name": cls.AGE_GROUP_NAMES[age_group],
                "age_range": cls.AGE_RANGES[age_group]
            }
            for age_group in AgeGroup
        ]
