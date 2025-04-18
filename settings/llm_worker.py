from PyQt5.QtCore import QThread, pyqtSignal
from .llm_api_aggregator import WWApiAggregator
from openai import OpenAIError

import logging

class LLMWorker(QThread):
    data_received = pyqtSignal(str)
    finished = pyqtSignal()
    token_limit_exceeded = pyqtSignal(str)

    def __init__(self, prompt, overrides=None, conversation_history=None):
        super().__init__()
        self.prompt = prompt
        self.overrides = overrides
        self.conversation_history = conversation_history
        self._is_running = True  # Flag to control thread execution
        logging.debug(f"LLMWorker created: {id(self)}")

    def run(self):
        logging.debug(f"LLMWorker started: {id(self)}")
        try:
            first_chunk = True
            for chunk in WWApiAggregator.stream_prompt_to_llm(self.prompt, self.overrides, self.conversation_history):
                if not self._is_running:  # Check if thread should stop
                    break
                if first_chunk:
                    if self.is_auth_error(chunk):
                        self.data_received.emit("Authentication Error: Invalid API key or JWT token")
                        return
                    if self.is_token_limit_error(chunk):
                        self.token_limit_exceeded.emit(chunk)
                        return
                self.data_received.emit(chunk)
                first_chunk = False
            self.finished.emit()
        except OpenAIError as e:
            # Handle OpenAI-specific errors (including OpenRouter)
            error_msg = str(e).lower()
            if "invalid jwt" in error_msg or "token-invalid" in error_msg or "authentication" in error_msg:
                self.data_received.emit("Authentication Error: Invalid or missing API key")
            else:
                self.data_received.emit(f"Error: {e}")
        except Exception as e:
            self.data_received.emit(f"Error: {e}")
        self.finished.emit()
        logging.debug(f"LLMWorker finished: {id(self)}")

    def stop(self):
        self._is_running = False  # Signal the thread to stop
        self.wait()  # Wait for the thread to finish
        logging.debug(f"LLMWorker stopped: {id(self)}")

    def is_auth_error(self, response):
        """Check if the response indicates an authentication error."""
        error_text = str(response).lower()
        return any(phrase in error_text for phrase in [
            "invalid jwt", "token-invalid", "authentication error", "signed-out"
        ])

    def is_token_limit_error(self, response):
        error_text = str(response).lower()
        return any(phrase in error_text for phrase in [
            "too many tokens", "exceeds token limit", "max tokens", "context length"
        ])
