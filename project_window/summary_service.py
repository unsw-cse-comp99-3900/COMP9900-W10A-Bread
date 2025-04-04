from settings.llm_worker import LLMWorker
from PyQt5.QtCore import QObject, pyqtSignal

class SummaryService(QObject):
    summary_generated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def generate_summary(self, prompt, content, overrides):
        """Generate summary using LLM."""
        final_prompt = f"### User {prompt.get('text')}\n\nContent:\n{content}"
        merged_overrides = {
            "provider": prompt.get("provider", ""),
            "model": prompt.get("model", ""),
            "max_tokens": prompt.get("max_tokens", 2000),
            "temperature": prompt.get("temperature", 1.0),
            **overrides
        }
        self.worker = LLMWorker(final_prompt, merged_overrides)
        self.worker.data_received.connect(self._on_data_received)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_data_received(self, text):
        self.summary_generated.emit(text)

    def _on_finished(self):
        # Signal completion if needed; handled by controller
        pass
