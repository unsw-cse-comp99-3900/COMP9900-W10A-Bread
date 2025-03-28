from PyQt5.QtCore import QThread, pyqtSignal
from .llm_api_aggregator import WWApiAggregator

class LLMWorker(QThread):
    data_received = pyqtSignal(str)
    finished = pyqtSignal()
    token_limit_exceeded = pyqtSignal(str)

    def __init__(self, prompt, overrides=None, conversation_history=None):
        super().__init__()
        self.prompt = prompt
        self.overrides = overrides
        self.conversation_history = conversation_history

    def run(self):
        try:
            first_chunk = True
            for chunk in WWApiAggregator.stream_prompt_to_llm(self.prompt, self.overrides, self.conversation_history):
                if first_chunk and self.is_token_limit_error(chunk):
                    self.token_limit_exceeded.emit(chunk)
                    return
                else:
                    self.data_received.emit(chunk)
                    first_chunk = False
            self.finished.emit()
        except Exception as e:
            self.data_received.emit(f"Error: {e}")
            self.finished.emit()


    def is_token_limit_error(self, response):
        error_text = str(response).lower()
        return any(phrase in error_text for phrase in [
            "too many tokens", "exceeds token limit", "max tokens", "context length"
        ])
