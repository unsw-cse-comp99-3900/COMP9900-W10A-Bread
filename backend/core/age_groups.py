"""
Age Group Configuration System - Provides appropriate AI writing suggestions for different age groups of children
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, date

class AgeGroup(Enum):
    """Age group enumeration"""
    PRESCHOOL = "preschool"          # Ages 3-5: Preschool stage
    EARLY_PRIMARY = "early_primary"  # Ages 6-8: Early primary school
    LATE_PRIMARY = "late_primary"    # Ages 9-11: Late primary school
    EARLY_MIDDLE = "early_middle"    # Ages 12-14: Early middle school
    LATE_MIDDLE = "late_middle"      # Ages 15-16: Late middle school
    HIGH_SCHOOL = "high_school"      # Ages 17-18: High school

class AgeGroupConfig:
    """Age group configuration class"""

    # Age group definitions
    AGE_RANGES = {
        AgeGroup.PRESCHOOL: (3, 5),
        AgeGroup.EARLY_PRIMARY: (6, 8),
        AgeGroup.LATE_PRIMARY: (9, 11),
        AgeGroup.EARLY_MIDDLE: (12, 14),
        AgeGroup.LATE_MIDDLE: (15, 16),
        AgeGroup.HIGH_SCHOOL: (17, 18),
    }

    # Age group display names
    AGE_GROUP_NAMES = {
        AgeGroup.PRESCHOOL: "Preschool (Ages 3-5)",
        AgeGroup.EARLY_PRIMARY: "Early Primary (Ages 6-8)",
        AgeGroup.LATE_PRIMARY: "Late Primary (Ages 9-11)",
        AgeGroup.EARLY_MIDDLE: "Early Middle School (Ages 12-14)",
        AgeGroup.LATE_MIDDLE: "Late Middle School (Ages 15-16)",
        AgeGroup.HIGH_SCHOOL: "High School (Ages 17-18)",
    }
    
    # AI suggestion configurations for each age group
    AI_CONFIGS = {
        AgeGroup.PRESCHOOL: {
            "language_level": "very_simple",
            "max_suggestions": 3,
            "focus_areas": ["Basic vocabulary", "Simple sentences", "Imagination"],
            "encouragement_style": "Very encouraging and praising",
            "feedback_complexity": "Very simple",
            "prompt_prefix": "You are helping a 3-5 year old child learn to write. Please use the simplest, most encouraging language, ",
            "suggestion_types": ["Vocabulary suggestions", "Sentence improvement", "Imagination inspiration"],
            "avoid_topics": ["Complex grammar", "Advanced vocabulary", "Critical feedback"],
            "example_prompts": [
                "That's a wonderful word! Can you think of other similar words?",
                "Your imagination is amazing! Can you tell me more about this story?",
                "This sentence is great! Let's make it even more fun together!"
            ]
        },
        
        AgeGroup.EARLY_PRIMARY: {
            "language_level": "simple",
            "max_suggestions": 4,
            "focus_areas": ["Basic grammar", "Vocabulary expansion", "Sentence structure", "Story logic"],
            "encouragement_style": "Positive encouragement",
            "feedback_complexity": "Simple",
            "prompt_prefix": "You are helping a 6-8 year old elementary student improve their writing. Please use simple, easy-to-understand language, ",
            "suggestion_types": ["Grammar correction", "Vocabulary replacement", "Sentence expansion", "Story development"],
            "avoid_topics": ["Complex rhetoric", "Deep analysis"],
            "example_prompts": [
                "You could try using this word instead - it will make your sentence more vivid!",
                "You could add an adjective here to help readers picture the scene better.",
                "Your story beginning is interesting! What happens next?"
            ]
        },
        
        AgeGroup.LATE_PRIMARY: {
            "language_level": "intermediate",
            "max_suggestions": 5,
            "focus_areas": ["Paragraph structure", "Literary devices", "Emotional expression", "Logical coherence"],
            "encouragement_style": "Constructive encouragement",
            "feedback_complexity": "Intermediate",
            "prompt_prefix": "You are helping a 9-11 year old upper elementary student improve their writing. Please provide specific and practical suggestions, ",
            "suggestion_types": ["Paragraph optimization", "Literary device usage", "Emotional depth", "Logic improvement"],
            "avoid_topics": ["Overly complex literary theory"],
            "example_prompts": [
                "This description is vivid! You could try adding some metaphors to make the imagery even clearer.",
                "Your article structure is clear. Adding transition sentences between paragraphs would make it even better.",
                "The emotions you express feel genuine - readers can really feel what you're feeling."
            ]
        },
        
        AgeGroup.EARLY_MIDDLE: {
            "language_level": "intermediate_advanced",
            "max_suggestions": 6,
            "focus_areas": ["Argument structure", "Genre awareness", "Deep thinking", "Expression techniques"],
            "encouragement_style": "Professional guidance",
            "feedback_complexity": "Intermediate-advanced",
            "prompt_prefix": "You are helping a 12-14 year old middle school student improve their writing. Please provide in-depth and professional suggestions, ",
            "suggestion_types": ["Argument strengthening", "Genre adjustment", "Thinking deepening", "Expression optimization"],
            "avoid_topics": ["Overly academic content"],
            "example_prompts": [
                "Your viewpoint is insightful! You could add some specific examples to support your argument.",
                "You've handled the genre well in this piece. Keep maintaining consistency in style.",
                "Your thinking is deep. You could further explore different angles of this issue."
            ]
        },
        
        AgeGroup.LATE_MIDDLE: {
            "language_level": "advanced",
            "max_suggestions": 7,
            "focus_areas": ["Critical thinking", "Literary techniques", "Personal style", "Deep analysis"],
            "encouragement_style": "Inspirational guidance",
            "feedback_complexity": "Advanced",
            "prompt_prefix": "You are helping a 15-16 year old high school student improve their writing. Please provide deep analysis and inspirational suggestions, ",
            "suggestion_types": ["Critical analysis", "Style development", "Technique application", "Thinking expansion"],
            "avoid_topics": [],
            "example_prompts": [
                "Your analysis is very deep! You could examine this issue from another perspective.",
                "Your writing shows your unique way of thinking. Continue developing your personal style.",
                "You've used this writing technique very well - it shows your literary sophistication."
            ]
        },
        
        AgeGroup.HIGH_SCHOOL: {
            "language_level": "advanced_academic",
            "max_suggestions": 8,
            "focus_areas": ["Academic writing", "Critical thinking", "Innovative expression", "In-depth research"],
            "encouragement_style": "Academic guidance",
            "feedback_complexity": "Advanced",
            "prompt_prefix": "You are helping a 17-18 year old high school graduate improve their writing. Please provide academic-level professional suggestions, ",
            "suggestion_types": ["Academic standards", "Innovative thinking", "In-depth research", "Professional expression"],
            "avoid_topics": [],
            "example_prompts": [
                "Your argument has academic value. Consider citing more authoritative sources.",
                "Your writing demonstrates mature critical thinking. Continue maintaining this analytical approach.",
                "Your expression is already quite professional. You could try more innovative writing techniques."
            ]
        }
    }
    
    @classmethod
    def get_age_group_by_age(cls, age: int) -> Optional[AgeGroup]:
        """Get age group by age"""
        for age_group, (min_age, max_age) in cls.AGE_RANGES.items():
            if min_age <= age <= max_age:
                return age_group
        return None

    @classmethod
    def get_age_group_by_birth_date(cls, birth_date: date) -> Optional[AgeGroup]:
        """Get age group by birth date"""
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return cls.get_age_group_by_age(age)

    @classmethod
    def get_config(cls, age_group: AgeGroup) -> Dict:
        """Get age group configuration"""
        return cls.AI_CONFIGS.get(age_group, cls.AI_CONFIGS[AgeGroup.LATE_PRIMARY])

    @classmethod
    def get_all_age_groups(cls) -> List[Dict]:
        """Get all age group information"""
        return [
            {
                "value": age_group.value,
                "name": cls.AGE_GROUP_NAMES[age_group],
                "age_range": cls.AGE_RANGES[age_group]
            }
            for age_group in AgeGroup
        ]
