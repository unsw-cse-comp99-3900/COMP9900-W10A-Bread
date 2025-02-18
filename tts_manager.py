import pyttsx3
import json, os

def get_tts_rate():
    """
    Read the settings.json file and return the desired TTS rate.
    We'll use 200 as the normal rate and 300 for fast speech.
    """
    normal_rate = 200  # Updated normal rate (default speed)
    fast_rate = 300    # Fast speech remains the same
    rate = normal_rate
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
            if settings.get("tts_fast", False):
                rate = fast_rate
        except Exception as e:
            print("Error loading TTS settings:", e)
    return rate

def get_engine():
    """
    Create and return a new pyttsx3 engine instance with the proper rate set.
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", get_tts_rate())
    return engine

# Global variable to hold the current engine.
_engine = None

def speak(text, start_position=0, on_complete=None):
    """
    Create a new engine, speak the text starting from the given cursor location,
    and then tear it down. Optionally, call on_complete() when done to update
    the TTS button (or any other UI element) back from "stop".
    """
    global _engine
    _engine = get_engine()
    # Start speaking from the provided cursor location (start_position)
    text_to_speak = text[start_position:]
    _engine.say(text_to_speak)
    _engine.runAndWait()
    # Invoke the on_complete callback if provided
    if on_complete is not None:
        on_complete()
    _engine = None

def stop():
    """
    Stop the current speech (if any) and reset the engine.
    """
    global _engine
    if _engine is not None:
        _engine.stop()
        _engine = None
