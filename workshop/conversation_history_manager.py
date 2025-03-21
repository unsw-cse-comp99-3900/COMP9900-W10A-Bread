import math
import tiktoken

from settings.llm_api_aggregator import WWApiAggregator

# Define the model name and get its encoding. Adjust the model name as needed.
MODEL_NAME = "gpt-3.5-turbo"
encoding = tiktoken.encoding_for_model(MODEL_NAME)

def estimate_tokens(text):
    """Estimate tokens using tiktoken for better accuracy."""
    return len(encoding.encode(text))

def estimate_conversation_tokens(conversation_history):
    total = 0
    for message in conversation_history:
        total += estimate_tokens(message.get("content", ""))
    return total

def should_preserve(text):
    """
    Check if a message contains protected text.
    For example, any text wrapped in asterisks (*) is marked as protected.
    You can enhance this function with a more complex tagging logic if needed.
    """
    return "*" in text

def summarize_conversation(conversation_history, max_tokens=500, summarization_prompt_prefix="Summarize the following conversation:"):
    # Build the conversation text while preserving protected messages.
    filtered_messages = []
    for msg in conversation_history:
        content = msg.get("content", "")
        # For now, we simply include the message as is.
        # In a more advanced version, you might choose to leave protected text unsummarized.
        filtered_messages.append(f'{msg["role"]}: {content}')
    conversation_text = "\n".join(filtered_messages)
    summarization_prompt = f"{summarization_prompt_prefix}\n{conversation_text}"
    summary = WWApiAggregator.send_prompt_to_llm(summarization_prompt, overrides={"max_tokens": max_tokens})
    return summary

def prune_conversation_history(conversation_history, token_limit):
    """
    Prune conversation history to fit within token_limit.
    This function tries to remove messages starting from index 1 (keeping the system prompt intact)
    and skips messages that are marked as protected (using our should_preserve() check).
    """
    index = 1  # Start after the system message
    # Continue while we exceed the token limit and have messages to remove.
    while estimate_conversation_tokens(conversation_history) > token_limit and index < len(conversation_history):
        content = conversation_history[index].get("content", "")
        if not should_preserve(content):
            conversation_history.pop(index)
        else:
            index += 1  # Skip protected message
    return conversation_history
