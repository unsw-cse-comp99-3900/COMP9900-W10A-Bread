import math
from llm_integration import send_prompt_to_llm

def estimate_tokens(text):
    return len(text.split())

def estimate_conversation_tokens(conversation_history):
    total = 0
    for message in conversation_history:
        total += estimate_tokens(message.get("content", ""))
    return total

def summarize_conversation(conversation_history, max_tokens=500, summarization_prompt_prefix="Summarize the following conversation:"):
    conversation_text = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in conversation_history])
    summarization_prompt = f"{summarization_prompt_prefix}\n{conversation_text}"
    summary = send_prompt_to_llm(summarization_prompt, overrides={"max_tokens": max_tokens})
    return summary

def prune_conversation_history(conversation_history, token_limit):
    while estimate_conversation_tokens(conversation_history) > token_limit and len(conversation_history) > 1:
        conversation_history.pop(1)
    return conversation_history
