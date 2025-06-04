import os
import json
from typing import List
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, 
                             QSpinBox, QProgressBar, QSplitter, QFileDialog, QMessageBox, QGridLayout, QScrollArea, 
                             QCheckBox, QLabel)

from .rag_utils import PdfProcessor, TokenCounter, PdfProcessingWorker, SettingsManager, HistoryDialog, AppSettings, LlmClient

class LlmWorker(QThread):
    result_ready = pyqtSignal(int, str, str)
    
    def __init__(self, chunk_idx: int, prompt: str, chunk_text: str):
        super().__init__()
        self.chunk_idx = chunk_idx
        self.prompt = prompt
        self.chunk_text = chunk_text
    
    def run(self):
        full_input = f"{self.prompt}\n\n{self.chunk_text}"
        try:
            # we call LLM indirectly through LlmClient
            response, error = LlmClient.send_prompt(full_input)
            if error:
                raise RuntimeError(error)
            self.result_ready.emit(self.chunk_idx, response, "")
        except Exception as e:
            self.result_ready.emit(self.chunk_idx, "", f"Error: {str(e)}")

class ManualProcessingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_manual_tab()

    def init_manual_tab(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)

        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)

        self.manual_pdf_path_edit = QLineEdit()
        self.manual_pdf_path_edit.setPlaceholderText("Select PDF file...")
        self.manual_pdf_path_edit.textChanged.connect(self.on_manual_pdf_path_changed)
        self.manual_pdf_path_edit.returnPressed.connect(
            lambda: self.process_manual_pdf() if self.manual_process_btn.isEnabled() else None
        )

        clear_path_btn = QPushButton("×")
        clear_path_btn.setFixedWidth(24)
        clear_path_btn.setToolTip("Clear path")
        clear_path_btn.clicked.connect(lambda: self.manual_pdf_path_edit.clear())

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_manual_pdf)

        pdf_group = QGroupBox("PDF Selection")
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(self.manual_pdf_path_edit, 1)
        pdf_layout.addWidget(clear_path_btn)
        pdf_layout.addWidget(browse_btn)
        pdf_group.setLayout(pdf_layout)
        upper_layout.addWidget(pdf_group)

        settings_group = QGroupBox("Page & Token Settings")
        settings_layout = QGridLayout()
        settings_layout.addWidget(QLabel("Pages from:"), 0, 0)
        self.manual_spin_from = QSpinBox()
        self.manual_spin_from.setMinimum(0)
        settings_layout.addWidget(self.manual_spin_from, 0, 1)
        settings_layout.addWidget(QLabel("to:"), 0, 2)
        self.manual_spin_to = QSpinBox()
        self.manual_spin_to.setMinimum(0)
        settings_layout.addWidget(self.manual_spin_to, 0, 3)
        settings_layout.addWidget(QLabel("Max tokens per chunk:"), 1, 0)
        self.manual_chunk_spin = QSpinBox()
        self.manual_chunk_spin.setRange(1, 1000000)
        self.manual_chunk_spin.setValue(20000)
        settings_layout.addWidget(self.manual_chunk_spin, 1, 1)
        settings_group.setLayout(settings_layout)
        upper_layout.addWidget(settings_group)

        self.manual_process_btn = QPushButton("Process PDF")
        self.manual_process_btn.clicked.connect(self.process_manual_pdf)
        self.manual_process_btn.setEnabled(False)
        upper_layout.addWidget(self.manual_process_btn)

        self.manual_token_label = QLabel("No document selected")
        self.manual_token_label.setStyleSheet("color: #888888; font-style: italic;")
        upper_layout.addWidget(self.manual_token_label)

        self.prompt_group = QGroupBox("Default Prompt Template")
        prompt_layout = QVBoxLayout()
        
        self.individual_prompts_checkbox = QCheckBox("Use individual prompts for each chunk")
        self.individual_prompts_checkbox.toggled.connect(self.toggle_individual_prompts)
        prompt_layout.addWidget(self.individual_prompts_checkbox)
        
        self.manual_default_prompt_edit = QPlainTextEdit()
        self.manual_default_prompt_edit.setPlaceholderText("Enter default prompt for all chunks...")
        prompt_layout.addWidget(self.manual_default_prompt_edit)
        self.prompt_group.setLayout(prompt_layout)
        upper_layout.addWidget(self.prompt_group)

        splitter.addWidget(upper_widget)

        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)

        self.manual_markdown_toggle_btn = QPushButton("Show/Edit Markdown")
        self.manual_markdown_toggle_btn.setCheckable(True)
        self.manual_markdown_toggle_btn.setEnabled(False)
        self.manual_markdown_toggle_btn.clicked.connect(self.toggle_manual_markdown_view)
        lower_layout.addWidget(self.manual_markdown_toggle_btn)

        self.manual_markdown_editor = QPlainTextEdit()
        self.manual_markdown_editor.setPlaceholderText("Processed Markdown will appear here...")
        self.manual_markdown_editor.setVisible(False)
        lower_layout.addWidget(self.manual_markdown_editor)

        self.manual_progress_bar = QProgressBar()
        self.manual_progress_bar.setVisible(False)
        lower_layout.addWidget(self.manual_progress_bar)

        self.manual_prompts_container = QWidget()
        self.manual_prompts_layout = QVBoxLayout(self.manual_prompts_container)
        self.manual_prompts_layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.manual_prompts_container)
        lower_layout.addWidget(scroll)

        self.manual_send_btn = QPushButton("Send to LLM")
        self.manual_send_btn.clicked.connect(self.send_manual_to_llm)
        self.manual_send_btn.setEnabled(False)
        lower_layout.addWidget(self.manual_send_btn)

        self.manual_export_btn = QPushButton("Save Results")
        self.manual_export_btn.clicked.connect(self.export_manual_results)
        self.manual_export_btn.setVisible(False)
        lower_layout.addWidget(self.manual_export_btn)

        splitter.addWidget(lower_widget)
        layout.addWidget(splitter)

        self.manual_markdown_text = ''
        self.manual_chunks = []
        self.manual_llm_workers = []
        self.chunk_prompt_inputs = []

        if self.parent_app.settings.last_pdf_path_manual and os.path.exists(self.parent_app.settings.last_pdf_path_manual):
            self.manual_pdf_path_edit.setText(self.parent_app.settings.last_pdf_path_manual)
            self.load_manual_pdf_info()
        self.manual_chunk_spin.setValue(self.parent_app.settings.last_chunk_size)
        self.manual_default_prompt_edit.setPlainText(self.parent_app.settings.default_prompt)

    def browse_manual_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self.manual_pdf_path_edit.setText(path)
            self.load_manual_pdf_info()

    def on_manual_pdf_path_changed(self):
        path = self.manual_pdf_path_edit.text().strip()
        is_valid = path.lower().endswith('.pdf') and os.path.isfile(path)
        self.manual_process_btn.setEnabled(is_valid)
        self.manual_markdown_toggle_btn.setEnabled(False)
        self.manual_send_btn.setEnabled(False)
        if not path:
            self.manual_token_label.setText("No document selected")
            self.manual_token_label.setStyleSheet("color: #888888; font-style: italic;")
        elif is_valid:
            name = os.path.basename(path)
            self.manual_token_label.setText(f"Ready to process: {name}")
            self.manual_token_label.setStyleSheet("color: #006400; font-style: normal;")
            self.load_manual_pdf_info()
        else:
            self.manual_token_label.setText("Invalid PDF file selected")
            self.manual_token_label.setStyleSheet("color: #8B0000; font-style: italic;")

    def load_manual_pdf_info(self):
        path = self.manual_pdf_path_edit.text().strip()
        if not path.lower().endswith('.pdf') or not os.path.isfile(path):
            return
        
        page_count, error = PdfProcessor.load_document(path)
        if error:
            QMessageBox.warning(self, "PDF Error", error)
            return
        
        last_page = page_count
        self.manual_spin_from.setMaximum(last_page)
        self.manual_spin_to.setMaximum(last_page)
        
        self.manual_spin_from.setProperty("max_page", last_page)
        self.manual_spin_to.setProperty("max_page", last_page)
        
        self.manual_spin_from.setValue(1)
        self.manual_spin_to.setValue(last_page)
        
        self.parent_app.settings.last_pdf_path_manual = path
        SettingsManager.save_settings(self.parent_app.settings)

    def correct_spinbox_value(self):
        sender = self.sender()
        max_page = sender.property("max_page")
        if max_page is not None and sender.value() > max_page:
            sender.setValue(max_page)
            
        if sender == self.manual_spin_from and self.manual_spin_from.value() > self.manual_spin_to.value():
            self.manual_spin_from.setValue(self.manual_spin_to.value())
        elif sender == self.manual_spin_to and self.manual_spin_to.value() < self.manual_spin_from.value():
            self.manual_spin_to.setValue(self.manual_spin_from.value())

    def toggle_manual_markdown_view(self):
        is_visible = self.manual_markdown_editor.isVisible()
        self.manual_markdown_editor.setVisible(not is_visible)

    def process_manual_pdf(self):
        pdf_path = self.manual_pdf_path_edit.text().strip()
        if not pdf_path or not os.path.isfile(pdf_path):
            QMessageBox.warning(self, "Error", "Invalid PDF file selected.")
            return
        
        page_count, error = PdfProcessor.load_document(pdf_path)
        if error:
            QMessageBox.warning(self, "Error", f"Failed to load PDF: {error}")
            return
        
        from_page = self.manual_spin_from.value()
        to_page = self.manual_spin_to.value()
        
        if from_page > page_count:
            from_page = page_count
            self.manual_spin_from.setValue(from_page)
            
        if to_page > page_count:
            to_page = page_count
            self.manual_spin_to.setValue(to_page)
        
        if from_page > to_page:
            from_page = to_page
            self.manual_spin_from.setValue(from_page)
        
        self.parent_app.settings.last_chunk_size = self.manual_chunk_spin.value()
        self.parent_app.settings.default_prompt = self.manual_default_prompt_edit.toPlainText()
        SettingsManager.save_settings(self.parent_app.settings)
        
        pdf_from_page = from_page - 1
        pdf_to_page = to_page - 1
        pages = list(range(pdf_from_page, pdf_to_page + 1))
        
        self.manual_progress_bar.setVisible(True)
        self.manual_progress_bar.setRange(0, 0)
        self.manual_process_btn.setEnabled(False)
        
        self.manual_worker = PdfProcessingWorker(pdf_path, pages, self.manual_chunk_spin.value())
        self.manual_worker.finished.connect(self.on_manual_pdf_processing_finished)
        self.manual_worker.start()

    def on_manual_pdf_processing_finished(self, markdown: str, chunks: List[str], error: str):
        self.manual_progress_bar.setVisible(False)
        self.manual_process_btn.setEnabled(True)

        if error:
            QMessageBox.critical(self, "Processing Error", error)
            self.manual_token_label.setText("Processing failed")
            self.manual_token_label.setStyleSheet("color: #8B0000; font-style: italic;")
            return

        self.manual_markdown_text = markdown
        self.manual_chunks = chunks
        self.manual_markdown_editor.setPlainText(markdown)

        total_tokens = TokenCounter.count_tokens(markdown)
        self.manual_token_label.setText(f"Tokens: {total_tokens} | Chunks: {len(chunks)}")
        self.manual_token_label.setStyleSheet("color: #006400; font-style: normal;")

        self.manual_markdown_toggle_btn.setEnabled(True)
        self.manual_send_btn.setEnabled(True)

        self.populate_manual_prompts()

    def toggle_individual_prompts(self, checked):
        self.manual_default_prompt_edit.setVisible(not checked)
        if self.manual_chunks:
            self.populate_manual_prompts()

    def copy_prompt_to_all(self):
        if not self.chunk_prompt_inputs or len(self.chunk_prompt_inputs) <= 1:
            return
        first_prompt_text = self.chunk_prompt_inputs[0].toPlainText()
        for prompt_input in self.chunk_prompt_inputs[1:]:
            prompt_input.setPlainText(first_prompt_text)

    def populate_manual_prompts(self):
        for i in reversed(range(self.manual_prompts_layout.count())):
            w = self.manual_prompts_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        
        self.chunk_prompt_inputs = []

        for idx, chunk in enumerate(self.manual_chunks):
            chunk_group = QGroupBox(f"Chunk {idx+1}")
            chunk_layout = QVBoxLayout(chunk_group)

            text = chunk if len(chunk) <= 500 else chunk[:100] + "…"
            preview = QLabel(f"Preview: {text}")
            preview.setWordWrap(True)
            preview.setTextInteractionFlags(
                Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
            )
            preview.setFocusPolicy(Qt.StrongFocus)
            chunk_layout.addWidget(preview)
            
            if self.individual_prompts_checkbox.isChecked():
                if idx == 0:
                    prompt_header_layout = QHBoxLayout()
                    prompt_label = QLabel("Prompt:")
                    prompt_header_layout.addWidget(prompt_label)
                    
                    copy_to_all_btn = QPushButton("Copy to all")
                    copy_to_all_btn.clicked.connect(self.copy_prompt_to_all)
                    prompt_header_layout.addWidget(copy_to_all_btn, alignment=Qt.AlignRight)
                    chunk_layout.addLayout(prompt_header_layout)
                else:
                    chunk_layout.addWidget(QLabel("Prompt:"))
                
                prompt_input = QPlainTextEdit()
                prompt_input.setPlaceholderText(f"Enter prompt for chunk {idx+1}...")
                if not self.individual_prompts_checkbox.isChecked():
                    prompt_input.setPlainText(self.manual_default_prompt_edit.toPlainText())
                prompt_input.setMaximumHeight(100)
                chunk_layout.addWidget(prompt_input)
                self.chunk_prompt_inputs.append(prompt_input)
            
            self.manual_prompts_layout.addWidget(chunk_group)

    def send_manual_to_llm(self):
        if not self.manual_chunks:
            QMessageBox.warning(self, "Error", "No data to send. Process PDF first.")
            return

        for w in self.manual_llm_workers:
            if w.isRunning():
                w.quit()
                w.wait()
        
        self.manual_llm_workers = []
        self.all_llm_responses = []
        self.manual_progress_bar.setRange(0, len(self.manual_chunks))
        self.manual_progress_bar.setValue(0)
        self.manual_progress_bar.setVisible(True)
        self.manual_send_btn.setEnabled(False)
        self.manual_export_btn.setVisible(False)

        for idx, chunk in enumerate(self.manual_chunks):
            if self.individual_prompts_checkbox.isChecked() and idx < len(self.chunk_prompt_inputs):
                prompt = self.chunk_prompt_inputs[idx].toPlainText().strip()
            else:
                prompt = self.manual_default_prompt_edit.toPlainText().strip()
                
            worker = LlmWorker(idx, prompt, chunk)
            worker.result_ready.connect(self.on_manual_llm_result)
            worker.started.connect(self.parent_app.set_busy_cursor)
            worker.finished.connect(self.parent_app.restore_cursor)
            self.manual_llm_workers.append(worker)
            worker.start()

    def on_manual_llm_result(self, idx, response, error):
        container = self.manual_prompts_layout.itemAt(idx).widget()
        layout = container.layout()
        
        txt = error or response
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText(txt)
        layout.addWidget(edit)

        self.all_llm_responses.append(txt)
        self.manual_progress_bar.setValue(self.manual_progress_bar.value() + 1)

        if self.manual_progress_bar.value() == len(self.manual_chunks):
            self.manual_send_btn.setEnabled(True)
            self.manual_export_btn.setVisible(True)
            self.manual_progress_bar.setVisible(False)
            if self.parent_app.active_workers > 0:
                self.parent_app.active_workers = 0
                QtWidgets.QApplication.restoreOverrideCursor()

    def export_manual_results(self):
        if not self.manual_chunks:
            QMessageBox.warning(self, "Error", "No data to export.")
            return

        data = {
            "pdf_path": self.manual_pdf_path_edit.text(),
            "page_range": [self.manual_spin_from.value(), self.manual_spin_to.value()],
            "token_count": TokenCounter.count_tokens(self.manual_markdown_text),
            "chunks": []
        }
        for idx, chunk in enumerate(self.manual_chunks):
            data["chunks"].append({
                "chunk_idx": idx,
                "content": chunk,
                "prompt": self.manual_default_prompt_edit.toPlainText(),
                "response": self.all_llm_responses[idx] if idx < len(self.all_llm_responses) else ""
            })

        base_pdf_name = os.path.splitext(os.path.basename(self.manual_pdf_path_edit.text()))[0]
        suggested_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Save Results",
            "Enter filename (no extension):",
            text=base_pdf_name + "_rag_results"
        )
        if not ok or not suggested_name.strip():
            return
        filename = suggested_name.strip() + ".json"
        save_path = os.path.join(self.parent_app.history_dir, filename)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.parent_app.status_bar.showMessage(f"Saved JSON to {save_path}", 5000)

        combined = "\n\n".join(ch["response"] for ch in data["chunks"])
        self.parent_app.search_history.append((filename, combined))
        self.parent_app.save_history()
        self.parent_app.status_bar.showMessage(f"History updated with {filename}", 5000)