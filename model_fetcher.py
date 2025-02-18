# model_fetcher.py
import requests
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal

class ModelFetcher(QObject):
    # Signal to notify when models are updated
    models_updated = pyqtSignal(list, str)  # (model_list, error_message if any)
    
    def __init__(self):
        super().__init__()
        self.cache_file = "model_cache.json"
        self.cache_duration = timedelta(hours=24)

    def _load_cache(self, provider):
        """Load cached model data if it exists and is not expired."""
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            if provider not in cache:
                return None
            provider_cache = cache[provider]
            cache_time = datetime.fromisoformat(provider_cache['timestamp'])
            # Check if cache is expired
            if datetime.now() - cache_time > self.cache_duration:
                return None
            return provider_cache['models']
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None

    def _save_cache(self, provider, models):
        """Save models to cache with current timestamp."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
            else:
                cache = {}
            cache[provider] = {
                'timestamp': datetime.now().isoformat(),
                'models': models
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=4)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def fetch_models(self, provider, config=None, force_refresh=False):
        """Fetch models for the specified provider."""
        if not force_refresh:
            cached_models = self._load_cache(provider)
            if cached_models:
                self.models_updated.emit(cached_models, "")
                return

        if provider == "OpenRouter":
            self._fetch_openrouter_models(config)
        elif provider == "OpenAI":
            self._fetch_openai_models(config)
        elif provider == "TogetherAI":
            self._fetch_togetherai_models(config)
        else:
            self._return_default_models(provider)

    def _fetch_openrouter_models(self, config):
        """Fetch models from OpenRouter API."""
        try:
            api_key = config.get('api_key', '') if config else ''
            headers = {
                'Authorization': f'Bearer {api_key}' if api_key else '',
                'HTTP-Referer': 'http://localhost:1234',
            }
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                models_data = response.json()
                # If the response is a dict with a "data" key, use that list.
                if isinstance(models_data, dict) and "data" in models_data:
                    models_list = models_data["data"]
                elif isinstance(models_data, list):
                    models_list = models_data
                else:
                    raise ValueError(f"Expected a list or dict with 'data', but got {type(models_data).__name__}")
                # Extract the "id" from each model in the list.
                model_list = [model["id"] for model in models_list if "id" in model]
                self._save_cache("OpenRouter", model_list)
                self.models_updated.emit(model_list, "")
            else:
                error_msg = f"Error fetching models (Status {response.status_code})"
                self._return_default_models("OpenRouter", error_msg)
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self._return_default_models("OpenRouter", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._return_default_models("OpenRouter", error_msg)

    def _fetch_openai_models(self, config):
        """Fetch models dynamically from the OpenAI API."""
        try:
            api_key = config.get('api_key', '') if config else ''
            if not api_key:
                raise ValueError("API key is required for OpenAI")
            headers = {
                'Authorization': f'Bearer {api_key}',
            }
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                models_data = response.json()
                # Expecting a dict with a "data" key containing model objects
                if isinstance(models_data, dict) and "data" in models_data:
                    models_list = models_data["data"]
                elif isinstance(models_data, list):
                    models_list = models_data
                else:
                    raise ValueError(f"Unexpected response structure: {type(models_data).__name__}")
                # Extract the "id" from each model in the list
                model_list = [model["id"] for model in models_list if "id" in model]
                self._save_cache("OpenAI", model_list)
                self.models_updated.emit(model_list, "")
            else:
                error_msg = f"Error fetching models (Status {response.status_code})"
                self._return_default_models("OpenAI", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._return_default_models("OpenAI", error_msg)

    def _fetch_togetherai_models(self, config):
        """Return TogetherAI models."""
        models = [
            "togethercomputer/llama-2-70b-chat",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "NousResearch/Nous-Hermes-2-Yi-34B",
            "upstage/SOLAR-0-70b-16bit"
        ]
        self._save_cache("TogetherAI", models)
        self.models_updated.emit(models, "")

    def _return_default_models(self, provider, error_msg=""):
        """Return default models for a provider when API fails."""
        default_models = {
            "OpenRouter": [
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
                "anthropic/claude-2",
                "google/palm-2-chat-bison",
                "meta-llama/llama-2-70b-chat"
            ],
            "Local": ["Local Model"],
        }
        models = default_models.get(provider, ["Default Model"])
        self.models_updated.emit(models, error_msg)
