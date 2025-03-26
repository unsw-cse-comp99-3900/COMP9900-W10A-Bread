from PyQt5.QtCore import QThread, pyqtSignal
from .llm_api_aggregator import WWApiAggregator

class LLMWorker(QThread):
    data_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, prompt, overrides=None, conversation_history=None):
        super().__init__()
        self.prompt = prompt
        self.overrides = overrides
        self.conversation_history = conversation_history

    def run(self):
        try:
            for chunk in WWApiAggregator.stream_prompt_to_llm(self.prompt, self.overrides, self.conversation_history):
                self.data_received.emit(chunk)
            self.finished.emit()
        except Exception as e:
            self.data_received.emit(f"Error: {e}")
            self.finished.emit()
