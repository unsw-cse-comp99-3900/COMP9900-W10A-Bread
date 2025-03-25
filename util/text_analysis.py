#!/usr/bin/env python
"""
text_analysis.py

English-specific text analysis module inheriting from BaseTextAnalysis.
"""

import spacy
from .base_text_analysis import BaseTextAnalysis
import textstat

ENGLISH_DATA = {
    "passive_deps": {"nsubjpass", "auxpass"},
    "agent_markers": {"by"},
    "weak_patterns": [r'\b\w+ly\b'],
    "weak_terms": {"maybe", "perhaps", "possibly", "apparently", "presumably", "i think", "i believe", "it seems", "seemingly", "somewhat", "kind of", "sort of"},
    "standard_speech_verbs": {"say", "ask"},
    "speech_verbs": {"say", "ask", "whisper", "murmur", "breathe", "exclaim", "shout", "chastise"},
    "filter_words": {"saw", "heard", "felt", "noticed", "realized", "thought", "wondered", "watched", "looked", "listened", "smelled", "decided", "considered", "seemed", "appeared", "observed", "sensed", "perceived", "imagined"},
    "telling_verbs": {"be", "feel", "seem", "look", "appear", "become", "get"},
    "emotion_words": {"angry", "sad", "happy", "excited", "nervous", "afraid", "worried", "embarrassed", "disappointed", "frustrated", "annoyed", "anxious", "scared", "terrified", "joyful", "depressed", "miserable", "ecstatic", "upset", "furious", "delighted", "shocked", "surprised", "confused", "proud", "ashamed", "content", "satisfied", "eager", "envious", "jealous"},
    "weak_verbs": {"be"},
    "common_words": {"the", "a", "an", "and", "but", "or", "in", "on", "at", "to", "of", "for", "with", "by", "as", "is", "are", "was", "were", "be", "been", "have", "has", "had", "i", "you", "he", "she", "it", "we", "they", "this", "that", "these", "those", "there", "here", "my", "your", "his", "her", "its", "our", "their"},
    "quote_pattern": r'"[^"]*"'
}

class EnglishTextAnalysis(BaseTextAnalysis):
    def __init__(self):
        super().__init__("en_core_web_sm", ENGLISH_DATA)

    def calculate_readability(self, text):
        """Calculates readability for English using the Flesch-Kincaid method."""
        return textstat.flesch_kincaid_grade(text)

nlp = None

def initialize():
    global nlp
    analysis = EnglishTextAnalysis()
    if analysis.initialize():
        nlp = analysis.nlp
        return True
    return False

def comprehensive_analysis(text, target_grade=8):
    analysis = EnglishTextAnalysis()
    if not analysis.initialize():
        raise RuntimeError("English spaCy model not loaded.")
    return analysis.comprehensive_analysis(text, target_grade)
