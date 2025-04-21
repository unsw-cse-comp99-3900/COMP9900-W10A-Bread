from PyQt5.QtCore import QThread, pyqtSignal
from .llm_api_aggregator import WWApiAggregator

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
            for i, chunk in enumerate(WWApiAggregator.stream_prompt_to_llm(self.prompt, self.overrides, self.conversation_history)):
                if not self._is_running:  # Check if thread should stop
                    logging.debug("LLMWorker interrupted")
                    break
                if i == 0 and self.is_token_limit_error(chunk):
                    self.token_limit_exceeded.emit(chunk)
                    logging.debug("LLMWorker: Token limit error detected")
                    return
                if not chunk or not isinstance(chunk, str):
                    logging.debug(f"Invalid chunk received: '{chunk}'")
                    continue
                logging.debug(f"Emitting chunk: '{chunk[:50]}'")  # Log first 50 chars of chunk
                self.data_received.emit(chunk)
            logging.debug(f"LLMWorker: Streaming completed processing {i} chunks")
            self.finished.emit()
        except Exception as e:
            logging.error(f"LLMWorker error: {e}")
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
