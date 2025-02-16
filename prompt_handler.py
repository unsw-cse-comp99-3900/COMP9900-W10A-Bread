# prompt_handler.py
from llm_integration import build_final_prompt, send_prompt_to_llm

def assemble_final_prompt(action_beats, prose_prompt, pov, pov_character, tense, current_scene_text=None, extra_context=None):
    """
    Assemble the final prompt by first building the base prompt using the action beats,
    prose prompt, and context parameters, and then appending the current scene text and any extra context.
    """
    # Build the base prompt.
    final_prompt = build_final_prompt(action_beats, prose_prompt, pov, pov_character, tense)
    context_parts = []
    if current_scene_text:
        context_parts.append("[Current Scene]:\n" + current_scene_text)
    if extra_context:
        context_parts.append(extra_context)
    if context_parts:
        final_prompt += "\n\n" + "\n\n".join(context_parts)
    return final_prompt

def send_final_prompt(final_prompt, overrides=None):
    """
    Sends the final prompt to the LLM using the provided overrides.
    Returns the generated text.
    """
    return send_prompt_to_llm(final_prompt, overrides=overrides)
