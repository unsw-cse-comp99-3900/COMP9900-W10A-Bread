# prompt_handler.py
import json
import os
from settings.llm_api_aggregator import WWApiAggregator

def build_final_prompt(action_beats, prose_prompt, pov, pov_character, tense):
    final_prompt = prose_prompt.format(pov=pov, pov_character=pov_character, tense=tense)
    final_prompt += "\n" + action_beats
    return final_prompt

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

    # Build the dictionary of overrides from the prompt configuration.
    prompt_overrides = {
        "provider": prompt_config.get("provider", "Local"),
        "model": prompt_config.get("model", "Local Model"),
    }
    # Merge any additional overrides if provided.
    if overrides:
        prompt_overrides.update(overrides)

    try:
        # Send the prompt to the LLM API aggregator.
        return WWApiAggregator.send_prompt_to_llm(final_prompt, overrides=prompt_overrides)
    except Exception as e:
        return(f"Error sending prompt to LLM: {e}")