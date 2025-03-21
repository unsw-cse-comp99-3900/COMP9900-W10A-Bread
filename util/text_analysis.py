#!/usr/bin/env python
"""
text_analysis.py

Core functions for text analysis:
- Sentence segmentation and complexity analysis.
- Detection of weak formulations and passive constructions.
- Detection of non-standard speech verbs (as a proxy for non-standard dialogue tags).
- Filter words detection (narrative distance).
- Show vs. tell analysis.
- Verb strength analysis.
- Overused words detection.
- Sentence variety analysis.
- Dialogue balance analysis.
- Pacing analysis.
- Paragraph structure analysis.
- Pronoun clarity check.
- Character voice consistency.
"""

import spacy
import textstat
import re
import logging
from collections import Counter, defaultdict
import statistics

# Setup logging. Adjust level to DEBUG if you want to see debug output.
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to see debug output.
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load spaCy model once for efficiency.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logging.error("Error loading spaCy model", exc_info=True)
    raise e

def analyze_text(text, target_grade):
    """
    Analyzes the text by segmenting it into sentences and calculating the 
    Flesch–Kincaid grade for each. Sentences exceeding the target grade are flagged.
    Sentences with fewer than 5 words are skipped to avoid anomalous grade calculations.

    Parameters:
        text (str): The input text.
        target_grade (float): The maximum acceptable grade level.

    Returns:
        list of dict: Each dictionary contains the sentence text, its start/end
        character offsets, calculated grade, a complexity flag, and the spaCy sentence.
    """
    try:
        doc = nlp(text)
    except Exception as e:
        logging.error("Error processing text with spaCy", exc_info=True)
        raise e

    annotated_sentences = []
    for sent in doc.sents:
        try:
            sent_text = sent.text.strip()
            # Skip sentences with fewer than 5 words.
            if len(sent_text.split()) < 5:
                continue
            start = sent.start_char
            end = sent.end_char
            fk_grade = textstat.flesch_kincaid_grade(sent_text)
            is_complex = fk_grade > target_grade
            annotated_sentences.append({
                "sentence": sent_text,
                "start": start,
                "end": end,
                "grade": fk_grade,
                "complex": is_complex,
                "doc": sent  # Store the spaCy sentence (a Span object) for further analysis.
            })
        except Exception as e:
            logging.error("Error analyzing sentence: %s", sent.text, exc_info=True)
    return annotated_sentences

# List of weak formulation keywords (legacy; now expanded in detect_weak_formulations).
WEAK_KEYWORDS = {"maybe", "perhaps", "slowly", "gently", "barely", "simply", "merely"}

def detect_passive(sentence_text, tokens):
    """
    Improved detection of passive voice using dependency parsing and POS tagging.
    Flags the sentence if a passive construction with an explicit agent is detected.
    
    Returns:
        list: A list with a single tuple (0, len(sentence_text)) if passive voice is detected,
        otherwise an empty list.
    """
    tokens_list = list(tokens)
    # Check for explicit passive markers.
    for token in tokens_list:
        if token.dep_ in {"nsubjpass", "auxpass"}:
            if any(t.dep_ == "agent" or t.text.lower() == "by" for t in tokens_list):
                return [(0, len(sentence_text))]
    # Check for "be" verb pattern.
    for i in range(len(tokens_list) - 2):
        token = tokens_list[i]
        if token.lemma_ == "be" and token.tag_ in {"VB", "VBP", "VBZ", "VBD"}:
            next_token = tokens_list[i+1]
            if next_token.tag_ == "VBN":
                if tokens_list[i+2].text.lower() == "by":
                    return [(0, len(sentence_text))]
    return []

def detect_weak_formulations(sentence_text, doc):
    """
    Returns a list of (start, end) tuples for spans in the sentence considered weak formulations.
    This updated version flags:
    - Any word that appears to be an adverb (heuristic: words ending in 'ly').
    - Hedging language and qualifiers such as "maybe", "perhaps", "possibly", "apparently",
      "presumably", "i think", "i believe", "it seems", "seemingly", "somewhat", "kind of", "sort of".
    
    Parameters:
        sentence_text (str): The sentence to analyze.
        doc: The spaCy Span object corresponding to the sentence.
    
    Returns:
        List of tuples: Each tuple contains the start and end indices (relative to the sentence)
        of a weak formulation span.
    """
    spans = []
    
    # Detect adverbs via regex (words ending in "ly").
    for match in re.finditer(r'\b\w+ly\b', sentence_text, re.IGNORECASE):
        spans.append((match.start(), match.end()))
    
    # Define hedging language and qualifier phrases.
    hedging_keywords = {"maybe", "perhaps", "possibly", "apparently", "presumably", "i think", "i believe", "it seems", "seemingly"}
    qualifier_keywords = {"somewhat", "kind of", "sort of"}
    all_weak_terms = hedging_keywords.union(qualifier_keywords)
    
    # Use regex to find these phrases in the sentence.
    for term in all_weak_terms:
        # Use word boundaries to match complete words/phrases.
        pattern = r'\b' + re.escape(term) + r'\b'
        for match in re.finditer(pattern, sentence_text, re.IGNORECASE):
            spans.append((match.start(), match.end()))
    
    # Optionally, sort spans by their starting index.
    spans.sort(key=lambda span: span[0])
    return spans

def detect_nonstandard_speech_verbs(text):
    """
    Processes the text with spaCy and flags any token that is a verb of speech
    if its lemma is in our speech verbs set but not in our standard set (i.e. not "say" or "ask").

    Standard speech verbs (say/ask) are given a pass, while all other speech verbs are flagged.
    
    Returns:
        list of tuples (start_offset, end_offset, "non_standard_dialogue_tag") for each detected instance.
    """
    doc = nlp(text)
    
    # Define our sets:
    standard_verbs = {"say", "ask"}  # This covers said, asks, etc. via lemmatization.
    speech_verbs = {"say", "ask", "whisper", "murmur", "breathe", "exclaim", "shout", "chastise"}
    
    spans = []
    for token in doc:
        if token.pos_ == "VERB" and token.lemma_.lower() in speech_verbs:
            if token.lemma_.lower() not in standard_verbs:
                spans.append((token.idx, token.idx + len(token.text), "non_standard_dialogue_tag"))
    return spans

# ============= NEW ANALYSIS FUNCTIONS =============

def detect_filter_words(doc):
    """
    Detects filter words that create narrative distance.
    
    Returns:
        List of tuples (start_char, end_char, word) identifying filter words.
    """
    filter_words = {
        "saw", "heard", "felt", "noticed", "realized", "thought", "wondered",
        "watched", "looked", "listened", "smelled", "decided", "considered", 
        "seemed", "appeared", "observed", "sensed", "perceived", "imagined"
    }
    
    results = []
    for token in doc:
        if token.lemma_.lower() in filter_words:
            results.append((token.idx, token.idx + len(token.text), token.text))
    return results

def detect_telling_not_showing(doc):
    """
    Detects direct emotion statements (telling) that could be shown instead.
    
    Returns:
        List of tuples (start_char, end_char, phrase) identifying telling phrases.
    """
    emotion_words = {
        "angry", "sad", "happy", "excited", "nervous", "afraid", "worried",
        "embarrassed", "disappointed", "frustrated", "annoyed", "anxious",
        "scared", "terrified", "joyful", "depressed", "miserable", "ecstatic",
        "upset", "furious", "delighted", "shocked", "surprised", "confused",
        "proud", "ashamed", "content", "satisfied", "eager", "envious", "jealous"
    }
    
    results = []
    # Pattern: "was/felt/seemed + emotion"
    for i, token in enumerate(doc):
        if token.lemma_ in ("be", "feel", "seem", "look", "appear", "become", "get"):
            # Check next words for emotions
            for j in range(1, 4):  # Look ahead up to 3 tokens
                if i + j < len(doc) and doc[i+j].lemma_.lower() in emotion_words:
                    phrase = doc[i:i+j+1].text
                    results.append((doc[i].idx, doc[i+j].idx + len(doc[i+j].text), phrase))
                    break
    return results

def analyze_verb_strength(doc):
    """
    Identifies weak "to be" verbs and continuous tense constructions.
    
    Returns:
        List of tuples (start_char, end_char, construction, type) identifying weak verbs.
    """
    results = []
    
    for i, token in enumerate(doc):
        # Check for "was/were + verb-ing" constructions
        if token.lemma_ == "be" and token.tag_ in ("VBD", "VBZ", "VBP"):
            if i + 1 < len(doc) and doc[i+1].tag_ == "VBG":
                span_text = doc[i:i+2].text
                results.append((
                    token.idx, 
                    doc[i+1].idx + len(doc[i+1].text), 
                    span_text,
                    "continuous_tense"
                ))
        
        # Check for standalone "to be" verbs as the main verb
        elif token.lemma_ == "be" and token.dep_ == "ROOT":
            results.append((
                token.idx, 
                token.idx + len(token.text), 
                token.text, 
                "be_verb"
            ))
    
    return results

def detect_overused_words(text, doc, threshold=3, window_size=1000, ignore_common=True):
    """
    Identifies overused words and phrases within a given window.
    
    Parameters:
        text: Original text (for getting character positions)
        doc: spaCy document
        threshold: Number of occurrences to be considered overused
        window_size: Character window to check for repetition
        ignore_common: Whether to ignore common words (articles, prepositions, etc.)
    
    Returns:
        List of tuples (start_char, end_char, word, count) for each overused word.
    """
    common_words = {
        "the", "a", "an", "and", "but", "or", "in", "on", "at", "to", "of", 
        "for", "with", "by", "as", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "i", "you", "he", "she", "it", "we", "they",
        "this", "that", "these", "those", "there", "here", "my", "your", "his",
        "her", "its", "our", "their", "s", "t", "ll", "d", "m", "re"
    }
    
    word_positions = defaultdict(list)
    
    for token in doc:
        # Skip punctuation and common words if requested
        if token.is_punct or (ignore_common and token.lower_ in common_words):
            continue
        
        # Store the position of each content word
        if token.is_alpha and len(token.text) > 2:  # Skip very short words
            word_positions[token.lower_].append(token.idx)
    
    results = []
    # Find overused words within the window
    for word, positions in word_positions.items():
        for i, pos in enumerate(positions):
            # Count occurrences within window_size characters
            window_occurrences = sum(1 for p in positions if abs(p - pos) <= window_size)
            if window_occurrences >= threshold:
                # If this is the first occurrence of this word in this window
                if all(abs(p - pos) > window_size for p in positions[:i]):
                    token_obj = next((t for t in doc if t.idx == pos), None)
                    if token_obj:
                        results.append((
                            pos, pos + len(token_obj.text), word, window_occurrences
                        ))
    
    return results

def check_pronoun_clarity(doc):
    """
    Flags potentially ambiguous pronoun references.
    
    Returns:
        List of tuples (start_char, end_char, pronoun) for each ambiguous pronoun.
    """
    results = []
    
    # Track named entities and pronouns by sentence
    for sent in doc.sents:
        entities = {}  # Store entities by gender
        male_entities = []
        female_entities = []
        
        # First pass: collect entities
        for token in sent:
            # Check for proper nouns and categorize by gender context
            if token.pos_ == "PROPN" or token.ent_type_ in ("PERSON", "ORG"):
                if any(m.text.lower() in ["he", "him", "his"] for m in sent):
                    male_entities.append(token.text)
                elif any(f.text.lower() in ["she", "her", "hers"] for f in sent):
                    female_entities.append(token.text)
        
        # Second pass: check pronouns
        for token in sent:
            if token.pos_ == "PRON":
                # Check for masculine pronouns with multiple male entities
                if token.text.lower() in ["he", "him", "his", "himself"] and len(male_entities) >= 2:
                    results.append((token.idx, token.idx + len(token.text), token.text))
                # Check for feminine pronouns with multiple female entities
                elif token.text.lower() in ["she", "her", "hers", "herself"] and len(female_entities) >= 2:
                    results.append((token.idx, token.idx + len(token.text), token.text))
                # Check "they" when it might be ambiguous
                elif token.text.lower() in ["they", "them", "their"] and len(male_entities) + len(female_entities) >= 2:
                    results.append((token.idx, token.idx + len(token.text), token.text))
    
    return results

def analyze_dialogue_balance(text):
    """
    Calculates the ratio of dialogue to narrative text and identifies dialogue-heavy sections.
    
    Returns:
        Tuple of (ratio, list of sections that are dialogue-heavy)
    """
    # Find all quoted sections
    dialogue_matches = list(re.finditer(r'"[^"]*"', text))
    
    dialogue_chars = 0
    dialogue_sections = []
    
    for match in dialogue_matches:
        start, end = match.span()
        dialogue_chars += (end - start)
        dialogue_sections.append((start, end))
    
    total_chars = len(text)
    dialogue_ratio = dialogue_chars / total_chars if total_chars > 0 else 0
    
    # Find dialogue-heavy sections (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text)
    dialogue_heavy_paragraphs = []
    
    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue
            
        para_start = text.find(para)
        para_end = para_start + len(para)
        
        # Count dialogue characters in this paragraph
        para_dialogue_chars = sum(
            min(end, para_end) - max(start, para_start) 
            for start, end in dialogue_sections 
            if max(start, para_start) < min(end, para_end)
        )
        
        para_ratio = para_dialogue_chars / len(para) if len(para) > 0 else 0
        
        # Flag paragraphs that are more than 70% dialogue
        if para_ratio > 0.7 and len(para) > 100:
            dialogue_heavy_paragraphs.append((para_start, para_end))
    
    return dialogue_ratio, dialogue_heavy_paragraphs

def detect_repeated_sentence_starts(doc, threshold=3):
    """
    Detects repeated sentence starting patterns.
    
    Returns:
        List of tuples (start_char, end_char, pattern) for sentences with repetitive starts.
    """
    sentence_starters = []
    starter_positions = defaultdict(list)
    
    for sent in doc.sents:
        # Get first content word of the sentence
        first_word = None
        for token in sent:
            if token.is_alpha and not token.is_stop:
                first_word = token
                break
        
        # If we found a content word, record its lemma
        if first_word:
            starter = first_word.lemma_.lower()
            sentence_starters.append(starter)
            starter_positions[starter].append((sent.start_char, first_word.idx + len(first_word.text)))
    
    # Count occurrences of each starting pattern
    starter_counts = Counter(sentence_starters)
    
    # Return positions of repetitive starters
    results = []
    for starter, positions in starter_positions.items():
        if starter_counts[starter] >= threshold:
            for start, end in positions:
                results.append((start, end, starter))
    
    return results

def comprehensive_analysis(text, target_grade=8):
    """
    Performs a comprehensive analysis on the text, calling all analysis functions.
    
    Returns:
        Dictionary containing all analysis results.
    """
    doc = nlp(text)
    
    # Basic sentence-level analysis
    sentence_analysis = analyze_text(text, target_grade)
    
    # Additional analyses
    filter_word_spans = []
    telling_spans = []
    weak_verb_spans = []
    overused_word_spans = []
    pronoun_clarity_spans = []
    repeated_starts_spans = []
    
    # Apply document-level analyses
    overused_word_spans = detect_overused_words(text, doc)
    dialogue_ratio, dialogue_heavy_spans = analyze_dialogue_balance(text)
    pronoun_clarity_spans = check_pronoun_clarity(doc)
    repeated_starts_spans = detect_repeated_sentence_starts(doc)
    
    # Apply sentence-level analyses
    for sent_data in sentence_analysis:
        sent_doc = sent_data["doc"]
        sent_start = sent_data["start"]
        
        # Filter words (narrative distance)
        for start, end, word in detect_filter_words(sent_doc):
            filter_word_spans.append((sent_start + start, sent_start + end, word))
        
        # Show vs. Tell
        for start, end, phrase in detect_telling_not_showing(sent_doc):
            telling_spans.append((sent_start + start, sent_start + end, phrase))
        
        # Weak verbs
        for start, end, construction, verb_type in analyze_verb_strength(sent_doc):
            weak_verb_spans.append((sent_start + start, sent_start + end, construction, verb_type))
    
    results = {
        "sentence_analysis": sentence_analysis,
        "filter_words": filter_word_spans,
        "telling_not_showing": telling_spans,
        "weak_verbs": weak_verb_spans,
        "overused_words": overused_word_spans,
        "pronoun_clarity": pronoun_clarity_spans,
        "dialogue_ratio": dialogue_ratio,
        "dialogue_heavy_sections": dialogue_heavy_spans,
        "repeated_sentence_starts": repeated_starts_spans
    }
    
    return results


if __name__ == "__main__":
    sample_text = (
        '"Look at that!" he said, spreading his cards out on the table. "A full house."\n'
        '"I just feel so tired all the time," she said. "Like nothing matters anymore."\n'
        '"Look at the state of your clothes! People are going to think you have been sleeping in a barn," she chastised.\n'
        '"Look at the state of your clothes! People are going to think you have been sleeping in a barn," she said.\n\n'
        "John felt angry. He was walking slowly to the store. He watched as Mary approached. She seemed sad.\n"
        "He saw the bird fly. He heard the music playing. He felt the rain falling on his skin.\n"
        "The tall man entered the room. The tall man sat down. The tall man ordered a drink.\n"
        "He looked at her. She looked at him. They both realized they had met before."
    )
    
    # Test the new analyses
    doc = nlp(sample_text)
    print("Filter words:")
    print(detect_filter_words(doc))
    
    print("\nTelling not showing:")
    print(detect_telling_not_showing(doc))
    
    print("\nWeak verbs:")
    print(analyze_verb_strength(doc))
    
    print("\nOverused words:")
    print(detect_overused_words(sample_text, doc, threshold=2))
    
    print("\nPronoun clarity:")
    print(check_pronoun_clarity(doc))
    
    print("\nDialogue balance:")
    print(analyze_dialogue_balance(sample_text))
    
    print("\nRepeated sentence starts:")
    print(detect_repeated_sentence_starts(doc, threshold=2))
    
    print("\nComprehensive analysis:")
    results = comprehensive_analysis(sample_text)
    for key, value in results.items():
        print(f"{key}: {value}")
