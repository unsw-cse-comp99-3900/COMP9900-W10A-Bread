import json
import requests
import os
from PyQt5.QtWidgets import QMessageBox

SETTINGS_FILE = "settings.json"

def build_final_prompt(action_beats, prose_prompt, pov, pov_character, tense):
    final_prompt = prose_prompt.format(pov=pov, pov_character=pov_character, tense=tense)
    final_prompt += "\n" + action_beats
    return final_prompt

def get_llm_settings():
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "llm" in data:
                settings = data["llm"]
            elif "llm_configs" in data and "active_llm_config" in data:
                active_config = data["active_llm_config"]
                for config in data["llm_configs"]:
                    if config.get("name") == active_config:
                        settings = config
                        break
        except Exception as e:
            print("⚠️ ERROR loading LLM settings:", e)
    defaults = {
        "provider": "Local",
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model": "local-model",
        "api_key": "",
        "timeout": 30
    }
    for key, val in defaults.items():
        settings.setdefault(key, val)
    return settings

def send_prompt_to_llm(final_prompt, overrides=None, conversation_history=None):
    llm_settings = get_llm_settings()
    if overrides:
        llm_settings.update(overrides)
    
    if not llm_settings.get("provider") or not llm_settings.get("model"):
        QMessageBox.critical(None, "LLM Configuration Error", 
                             "Error: No model selected. Please select a model in the prompt settings.")
        return "[Error: No model selected]"
    
    if llm_settings.get("provider") == "Local":
        llm_settings["endpoint"] = "http://localhost:1234/v1/chat/completions"
    elif llm_settings.get("provider") == "OpenRouter":
        llm_settings["endpoint"] = "https://openrouter.ai/api/v1/chat/completions"
    elif llm_settings.get("provider") == "Ollama":
        llm_settings["endpoint"] = "http://localhost:11434/v1/chat/completions"
    
    provider = llm_settings.get("provider", "Local")
    endpoint = llm_settings.get("endpoint", "http://localhost:1234/v1/chat/completions")
    model = llm_settings.get("model", "local-model")
    api_key = llm_settings.get("api_key", "")
    timeout = llm_settings.get("timeout", 30)

    print(f"🔍 DEBUG: API Key Retrieved = '{api_key}' (length: {len(api_key)})")

    # Skip the API key check if using a local provider
    if provider not in ["Local", "Ollama"] and not api_key:
        print("❌ ERROR: API Key is missing or empty! Check settings.json.")
        return "[Error: Missing API Key]"

    headers = {
        "Content-Type": "application/json",
    }
    if provider == "OpenAI":
        headers["Authorization"] = f"Bearer {api_key}"
    elif provider in ["OpenRouter", "Custom"]:
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "max_tokens": overrides.get("max_tokens", 2000) if overrides else 2000,
        "temperature": overrides.get("temperature", 1.0) if overrides else 1.0
    }
    if conversation_history:
        payload["messages"] = conversation_history
    else:
        payload["messages"] = [{"role": "user", "content": final_prompt}]
    
    print(f"🔍 DEBUG: Headers = {headers}")
    print(f"🔍 DEBUG: Payload = {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        print(f"✅ DEBUG: Response = {json.dumps(result, indent=2)}")
        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not generated_text:
            generated_text = "[No text returned by LLM]"
        return generated_text
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e} - {response.text}")
        return f"[HTTP Error: {e}]"
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return f"[Request Error: {e}]"
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return f"[Unexpected Error: {e}]"

def get_prose_prompts(project_name):
    base_name = f"prompts_{project_name.replace(' ', '')}.json"
    try:
        with open(base_name, "r", encoding="utf-8") as f:
            prompts_data = json.load(f)
        return prompts_data.get("Prose", [])
    except Exception as e:
        print(f"⚠️ ERROR loading Prose prompts: {e}")
        return []
