import json
import os
import requests

from typing import Dict, List, Optional, Any, Type, Union
from abc import ABC, abstractmethod
from pydantic import ValidationError

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

from langchain_core.language_models.llms import LLM
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_together import ChatTogether

from .settings_manager import WWSettingsManager

# Configuration constants
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.7


class LLMProviderBase(ABC):
    """Base class for all LLM providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cached_models = None
        self.llm_instance = None
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass
    
    @property
    @abstractmethod
    def default_endpoint(self) -> str:
        """Return the default endpoint for the provider."""
        pass

    @property
    def model_list_key(self) -> str:
        """Return the key for the model name in the provider's json response."""
        return "data"

    @property
    def model_key(self) -> str:
        """Return the key for the model name in the provider's json response."""
        return "id"
    
    @property
    def model_requires_api_key(self) -> bool:
        """Return whether the provider requires an API key."""
        return False
    
    @property
    def use_reverse_sort(self) -> bool:
        """Return whether to reverse the output of the model list."""
        return False

    @abstractmethod
    def get_llm_instance(self, overrides) -> Union[LLM, BaseChatModel]:
        """Returns a configured LLM instance."""
        pass
    
    def _do_models_request(self, url: str, headers: Dict[str, str] = None) -> List[str]:
        """Send a request to the provider to fetch available models."""
        headers = {
            'Authorization': f'Bearer {self.get_api_key()}'
        }
        return requests.get(url, headers=headers)
        
    
    def get_available_models(self, do_refresh: bool = False) -> List[str]:
        """Returns a list of available models from the provider."""
        if do_refresh or self.cached_models is None:
            url = self.get_base_url()
            if url[-1] != "/":
                url += "/"
            url += "models"
            response = self._do_models_request(url)
            if response.status_code == 200:
                models_data = response.json()
                self.cached_models = [model[self.model_key] for model in models_data.get(self.model_list_key, [])]
                self.cached_models.sort(reverse=self.use_reverse_sort)
            else:
                self.cached_models = []
                    
        if do_refresh and response.status_code != 200:
            raise ResourceWarning(response.json().get("error"))
        return self.cached_models

    
    def get_current_model(self) -> str:
        """Returns the currently configured model name."""
        return self.config.get("model", "")

    def get_default_endpoint(self) -> str:
        """Returns the default endpoint for the provider."""
        return self.default_endpoint

    def get_base_url(self) -> str:
        """Returns the base URL for the provider."""
        return self.config.get("endpoint") or self.get_default_endpoint()
    
    def get_api_key(self) -> str:
        """Returns the API key for the provider."""
        return self.config.get("api_key", "")
    
    def get_timeout(self, overrides) -> int:
        """Returns the timeout setting for the provider."""
        return overrides.get("timeout", self.config.get("timeout", 30))
    
    def get_context_window(self) -> int:
        """Returns the context window size for the current model."""
        # This would ideally be retrieved dynamically based on the model
        # For the base implementation, we'll return a default value
        return 4096

 
    def get_model_endpoint(self, overrides=None) -> str:
        """Returns the model endpoint for the provider."""
        url = overrides and overrides.get("endpoint") or self.config.get("endpoint", self.get_base_url())
        return url.replace("/chat/completions", "/models")

    def test_connection(self, overrides = None) -> bool:
        """Test the connection to the provider."""
        overrides["max_tokens"] = 1 # Minimal request for testing
        if not overrides["model"]:
            overrides["model"] = "None"
        llm = self.get_llm_instance(overrides)
        if not llm:
            return False

        prompt = PromptTemplate(input_variables=[], template="testing connection")
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({})
        return True

class OpenAIProvider(LLMProviderBase):
    """OpenAI LLM provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "OpenAI"
    
    @property
    def default_endpoint(self) -> str:
        return "https://api.openai.com/v1/"
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            self.llm_instance = ChatOpenAI(
                openai_api_key=overrides.get("api_key", self.get_api_key()),
                openai_api_base=overrides.get("endpoint", self.get_base_url()),
                model_name=overrides.get("model", self.get_current_model()),
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                max_tokens=self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
                request_timeout=self.get_timeout(overrides)
            )
        return self.llm_instance

class AnthropicProvider(LLMProviderBase):
    """Anthropic LLM provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "Anthropic"
    
    @property
    def default_endpoint(self) -> str:
        return "https://api.anthropic.com/v1/"

    @property
    def model_requires_api_key(self) -> bool:
        """Return whether the provider requires an API key."""
        return True
    
    @property
    def use_reverse_sort(self) -> bool:
        """Return whether to reverse the output of the model list."""
        return True

    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            self.llm_instance = ChatAnthropic(
                anthropic_api_key=overrides.get("api_key", self.get_api_key()),
                base_url=overrides.get("endpoint", None),
                model_name=overrides.get("model", self.get_current_model() or "claude-3-haiku-20240307"),
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                max_tokens=self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
                timeout=self.get_timeout(overrides)
            )
        return self.llm_instance
    
    def _do_models_request(self, url: str, headers: Dict[str, str] = None) -> List[str]:
        """Send a request to the provider to fetch available models."""
        headers = {
            'x-api-key': self.get_api_key(),
            'anthropic-version': '2023-06-01',
#            'Authorization': f'Bearer {self.get_api_key()}',
        }
        return requests.get(url, headers=headers)

class GeminiProvider(LLMProviderBase):
    """Google Gemini provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "Gemini"
    
    @property
    def default_endpoint(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta/"
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            self.llm_instance = ChatGoogleGenerativeAI(
                google_api_key = overrides.get("api_key", self.get_api_key()),
                google_api_base=overrides.get("endpoint", self.get_base_url()),
                model = overrides.get("model", self.get_current_model() or "gemini-2.0-flash"),
                temperature = overrides.get("temperature", self.config.get("temperature", DEFAULT_TEMPERATURE)),
                max_output_tokens = overrides.get("max_tokens", self.config.get("max_tokens", DEFAULT_MAX_TOKENS)),
                timeout = self.get_timeout(overrides)
            )
        return self.llm_instance
    
    def get_available_models(self, do_refresh: bool = False) -> List[str]:
        if do_refresh or self.cached_models is None:
            try:
                # Google does not provide a public API to fetch models
                self.cached_models = [
                    "gemini-2.0-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash",
                    "gemini-1.0-pro"
                ]
            except Exception as e:
                print(f"Error fetching Gemini models: {e}")
                self.cached_models = []
        return self.cached_models


class OllamaProvider(LLMProviderBase):
    """Ollama LLM provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "Ollama"
    
    @property
    def default_endpoint(self) -> str:
        return "http://localhost:11434/v1/"
    
    def get_llm_instance(self, overrides) -> LLM:
        if not self.llm_instance:
            mymodel = overrides.get("model", self.get_current_model())
            if mymodel[0:5] in ["", "Local"]:
                mymodel = self.get_current_model()
            self.llm_instance = ChatOllama(
                model = mymodel,
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                timeout=self.get_timeout(overrides)
            )
        return self.llm_instance
    

class OpenRouterProvider(LLMProviderBase):
    """OpenRouter provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "OpenRouter"
    
    @property
    def default_endpoint(self) -> str:
        return "https://openrouter.ai/api/v1/"
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            # OpenRouter uses the same API as OpenAI
            self.llm_instance = ChatOpenAI(
                openai_api_key=overrides.get("api_key", self.get_api_key()),
                base_url=overrides.get("endpoint", self.get_base_url()),
                model_name=overrides.get("model", self.get_current_model()),
                temperature=overrides.get("temperature", self.config.get("temperature", DEFAULT_TEMPERATURE)),
                max_tokens=overrides.get("max_tokens", self.config.get("max_tokens", DEFAULT_MAX_TOKENS)),
                request_timeout=self.get_timeout(overrides)
            )
        return self.llm_instance

class TogetherAIProvider(LLMProviderBase):
    """Together AI provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "TogetherAI"
    
    @property
    def default_endpoint(self) -> str:
        return "https://api.together.xyz/v1"
    
    @property
    def model_requires_api_key(self) -> bool:
        """Return whether the provider requires an API key."""
        return True
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            self.llm_instance = ChatTogether(
                together_api_key=overrides.get("api_key", self.get_api_key()),
                base_url=overrides.get("endpoint", self.get_base_url()),
                model=overrides.get("model", self.get_current_model()),
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                max_tokens=self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
            )
        return self.llm_instance

    def get_available_models(self, do_refresh: bool = False) -> List[str]:
        """Returns a list of available models from the provider."""
        if do_refresh or self.cached_models is None:
            url = self.get_base_url()
            if url[-1] != "/":
                url += "/"
            url += "models"
            response = self._do_models_request(url)
            if response.status_code == 200:
                models_data = response.json()
                self.cached_models = [model[self.model_key] for model in models_data]
                self.cached_models.sort(reverse=self.use_reverse_sort)
            else:
                self.cached_models = []
                    
        if do_refresh and response.status_code != 200:
            raise ResourceWarning(response.json().get("error"))
        return self.cached_models
    
class LMStudioProvider(LLMProviderBase):
    """LMStudio provider implementation."""
    
    @property
    def provider_name(self) -> str:
        return "LMStudio"
    
    @property
    def default_endpoint(self) -> str:
        return "http://localhost:1234/v1"
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            # LMStudio uses the OpenAI-compatible API
            self.llm_instance = ChatOpenAI(
                openai_api_key=overrides.get("api_key", self.get_api_key() or "not-needed"),
                openai_api_base=overrides.get("endpoint", self.get_base_url()),
                model_name=overrides.get("model", self.get_current_model() or "local-model"),
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                max_tokens=self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
                request_timeout=self.get_timeout(overrides)
            )
        return self.llm_instance

class CustomProvider(LLMProviderBase):
    """Custom LLM provider implementation for local network tools."""
    
    @property
    def provider_name(self) -> str:
        return "Custom"
    
    @property
    def default_endpoint(self) -> str:
        return "http://localhost:11434/v1/"
    
    def get_api_key(self):
        return super().get_api_key() or "not-needed"
    
    def get_llm_instance(self, overrides) -> BaseChatModel:
        if not self.llm_instance:
            self.config["endpoint"] = overrides.get("endpoint", self.get_base_url())
            self.config["api_key"] = overrides.get("api_key", self.get_api_key())
            self.config["model"] = overrides.get("model", self.get_current_model())
            self.llm_instance = ChatOpenAI( # most custom models are OpenAI compatible
                base_url=self.get_base_url(),
                api_key=self.get_api_key(),
                model_name=self.get_current_model() or "custom-model",
                temperature=self.config.get("temperature", DEFAULT_TEMPERATURE),
                max_tokens=self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
                request_timeout=self.get_timeout(overrides)
            )
        return self.llm_instance

class WW_Aggregator:
    """Main aggregator class for managing LLM providers."""
    
    def __init__(self):
        self._provider_cache = {}
        self._settings = None
    
    def create_provider(self, provider_name: str, config: Dict[str, Any] = None) -> Optional[LLMProviderBase]:
        """Create a new provider instance."""
        provider_class = self._get_provider_class(provider_name)
        if not provider_class:
            return None
        
        return provider_class(config)
    
    def get_provider(self, provider_name: str) -> Optional[LLMProviderBase]:
        """Get a provider instance by name."""
        if provider_name not in self._provider_cache:
            config = self._get_provider_config(provider_name)
            if not config:
                return None
            
            provider = config.get("provider")
            provider_class = self._get_provider_class(provider)
            if not provider_class:
                return None
            
            self._provider_cache[provider_name] = provider_class(config)
        
        return self._provider_cache[provider_name]
    
    def get_active_llms(self) -> List[str]:
        """Returns a list of all configured and cached LLMs."""
        return list(self._provider_cache.keys())
    
    def _get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get the configuration for a provider from settings."""
        settings = WWSettingsManager.get_llm_configs()
        if not settings:
            return None
        
        return settings.get(provider_name)
    
    def _get_provider_class(self, provider_name: str) -> Optional[Type[LLMProviderBase]]:
        """Get the provider class based on the provider name."""
        provider_map = {
            cls().provider_name: cls
            for cls in LLMProviderBase.__subclasses__()
        }
        return provider_map.get(provider_name)

import threading
import queue

class LLMAPIAggregator:
    """Main class for the LLM API Aggregator."""
    
    def __init__(self):
        self.aggregator = WW_Aggregator()
        self.interrupt_flag = threading.Event()
    
    def get_llm_providers(self) -> List[str]:
        """Dynamically returns a list of supported LLM provider names."""
        return [cls().provider_name for cls in LLMProviderBase.__subclasses__()]
    
    def send_prompt_to_llm(
        self, 
        final_prompt: str, 
        overrides: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Send a prompt to the active LLM and return the generated text."""
        overrides = overrides or {}
        settings = WWSettingsManager.get_llm_configs()
        
        # Determine which provider to use
        provider_name = overrides.get("provider") or WWSettingsManager.get_active_llm_name()
        if provider_name == "Local": # need to rename this to Default everywhere
            provider_name = WWSettingsManager.get_active_llm_name()
            overrides = {}
        if not provider_name:
            raise ValueError("No active LLM provider specified")
        
        # Get the provider instance
        provider = self.aggregator.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found or not configured")
        
        # Get the LLM instance
        llm = provider.get_llm_instance(overrides)
        
        # Create messages format if conversation history is provided
        if conversation_history:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            messages = []
            for message in conversation_history:
                role = message.get("role", "").lower()
                content = message.get("content", "")
                
                if role == "system":
                    messages.append(SystemMessage(content=content))
                elif role == "user" or role == "human":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant" or role == "ai":
                    messages.append(AIMessage(content=content))
            
            # Add the current prompt
            messages.append(HumanMessage(content=final_prompt))
            
            # Generate response
            response = llm.invoke(messages)
            return response.content
        else:
            # Simple prompt-based invocation
            return llm.invoke(final_prompt).content

    def stream_prompt_to_llm(
        self, 
        final_prompt: str, 
        overrides: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """Stream a prompt to the active LLM and yield the generated text."""
        overrides = overrides or {}
        settings = WWSettingsManager.get_llm_configs()
        
        # Determine which provider to use
        provider_name = overrides.get("provider") or WWSettingsManager.get_active_llm_name()
        if provider_name == "Local": # need to rename this to Default everywhere
            provider_name = WWSettingsManager.get_active_llm_name()
            overrides = {}
        if not provider_name:
            raise ValueError("No active LLM provider specified")
        
        # Get the provider instance
        provider = self.aggregator.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found or not configured")
        
        # Get the LLM instance
        llm = provider.get_llm_instance(overrides)
        
        # Create messages format if conversation history is provided
        if conversation_history:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            messages = []
            for message in conversation_history:
                role = message.get("role", "").lower()
                content = message.get("content", "")
                
                if role == "system":
                    messages.append(SystemMessage(content=content))
                elif role == "user" or role == "human":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant" or role == "ai":
                    messages.append(AIMessage(content=content))
            
            # Add the current prompt
            messages.append(HumanMessage(content=final_prompt))
            
            # Generate response
            for chunk in llm.stream(messages):
                if self.interrupt_flag.is_set():
                    break
                yield chunk.content
        else:
            # Simple prompt-based invocation
            for chunk in llm.stream(final_prompt):
                if self.interrupt_flag.is_set():
                    break
                yield chunk.content

    def interrupt(self):
        """Interrupt the streaming process."""
        self.interrupt_flag.set()

WWApiAggregator = LLMAPIAggregator()


def main():
    """Example usage of the LLM API Aggregator."""
    aggregator = LLMAPIAggregator()
    
    overrides = {
        "api_key": "AIFakeKey123",
    }

    try:
        p = aggregator.aggregator.create_provider("Gemini")
        p.get_default_endpoint(overrides)
        p.get_base_url()
    except ValidationError as exc:
        print(exc.errors())
        #> 'missing'

    # Get list of supported providers
    providers = aggregator.get_llm_providers()
    print(f"Supported providers: {providers}")
    
    # Example prompt
    try:
        response = aggregator.send_prompt_to_llm("Hello, tell me a short story about a robot.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
