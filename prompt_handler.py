# prompt_handler.py
import json
import os
from llm_integration import build_final_prompt, send_prompt_to_llm


def assemble_final_prompt(action_beats, prose_prompt, pov, pov_character, tense, current_scene_text=None, extra_context=None):
    """
    Assemble the final prompt by first building the base prompt using the action beats,
    prose prompt, and context parameters, and then appending the current scene text and any extra context.
    """
    # Build the base prompt.
    final_prompt = build_final_prompt(
        action_beats, prose_prompt, pov, pov_character, tense)
    context_parts = []
    if current_scene_text:
        context_parts.append("[Current Scene]:\n" + current_scene_text)
    if extra_context:
        context_parts.append(extra_context)
    if context_parts:
        final_prompt += "\n\n" + "\n\n".join(context_parts)
    return final_prompt


def send_final_prompt(final_prompt, prompt_config=None, overrides=None):
    """
    Sends the final prompt to the LLM using settings from the prompt's configuration.
    The configuration should include keys such as "provider", "model", "timeout", and "api_key".

    If no prompt_config is provided, then any overrides passed will be used as the configuration.
    If the resulting configuration is missing an API key (and the provider isn't "Local"), 
    the function will attempt to load the API key from settings.json based on the provider.

    Additional overrides (if provided) are merged afterward.
    Returns the generated text.
    """
    # If prompt_config is not provided, treat 'overrides' as the prompt configuration.
    if prompt_config is None:
        prompt_config = overrides.copy() if overrides else {}
        overrides = {}

    # Ensure a provider is set; default to "Local"
    provider = prompt_config.get("provider", "Local")
    prompt_config["provider"] = provider

    # If API key is missing and provider is not Local, try to load it from settings.json.
    if provider != "Local" and not prompt_config.get("api_key"):
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                # Look for a configuration with a matching provider.
                for config in settings.get("llm_configs", []):
                    if config.get("provider") == provider:
                        prompt_config["api_key"] = config.get("api_key", "")
                        # Optionally, also update timeout or endpoint if needed.
                        prompt_config.setdefault(
                            "timeout", config.get("timeout", 60))
                        break
            except Exception as e:
                print("Error loading settings.json for API key:", e)

    # Build the dictionary of overrides from the prompt configuration.
    prompt_overrides = {
        "provider": prompt_config.get("provider", "Local"),
        "model": prompt_config.get("model", "Local Model"),
        "timeout": prompt_config.get("timeout", 60),
        "api_key": prompt_config.get("api_key", ""),
    }
    # Merge any additional overrides if provided.
    if overrides:
        prompt_overrides.update(overrides)
    return send_prompt_to_llm(final_prompt, overrides=prompt_overrides)
