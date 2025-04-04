import json
import os
import re
import glob
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QMessageBox, QInputDialog, QTreeWidget, QTreeWidgetItem,
    QSplitter, QWidget, QScrollArea, QLabel, QApplication, QListWidget, QListWidgetItem, QMenu, QComboBox
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
import muse.prompts
from settings.llm_api_aggregator import WWApiAggregator
from settings.autosave_manager import load_latest_autosave
from .conversation_history_manager import estimate_conversation_tokens, summarize_conversation
from .embedding_manager import EmbeddingIndex
from project_window.context_panel import ContextPanel
from compendium.compendium_manager import CompendiumManager

TOKEN_LIMIT = 2000

class WorkshopWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workshop")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.resize(1000, 600)
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        self.model = getattr(parent, "model", None) if parent else None  # Access model from parent if available
        self.project_name = getattr(self.model, "project_name", "DefaultProject") if parent else "DefaultProject"
        self.structure = getattr(self.model, "structure", {"acts": []}) if parent else {"acts": []}
        self.workshop_prompt_config = None

        # Conversation management
        self.conversation_history = []
        self.conversations = {}
        self.current_conversation = "Chat 1"
        self.conversations[self.current_conversation] = []

        # Embedding index
        self.embedding_index = EmbeddingIndex()

        self.current_mode = "Normal"

        self.init_ui()
        self.load_conversations()

        # Connect model signal if available
        if self.model:
            self.model.structureChanged.connect(self.context_panel.on_structure_changed)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Outer splitter
        outer_splitter = QSplitter(Qt.Horizontal)

        # Conversation History Panel
        conversation_container = QWidget()
        conversation_layout = QVBoxLayout(conversation_container)
        conversation_layout.setContentsMargins(0, 0, 0, 0)

        self.conversation_list = QListWidget()
        self.conversation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.conversation_list.customContextMenuRequested.connect(self.show_conversation_context_menu)
        self.conversation_list.itemClicked.connect(self.load_conversation_from_list)
        conversation_layout.addWidget(self.conversation_list)

        new_chat_button = QPushButton("New Chat")
        new_chat_button.clicked.connect(self.new_conversation)
        conversation_layout.addWidget(new_chat_button)

        outer_splitter.addWidget(conversation_container)
        outer_splitter.setStretchFactor(0, 1)

        # Chat Panel
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        chat_layout.addWidget(self.chat_log)

        # Splitter for input and context panel
        splitter = QSplitter(Qt.Horizontal)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        left_layout.addWidget(self.chat_input)

        # Buttons and Mode/Prompt Selector
        buttons_layout = QHBoxLayout()

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Normal", "Economy", "Ultra-Light"])
        self.mode_selector.currentIndexChanged.connect(self.mode_changed)
        buttons_layout.addWidget(self.mode_selector)

        self.prompt_selector = QComboBox()
        prompts = muse.prompts.get_workshop_prompts(self.project_name)
        if prompts:
            for p in prompts:
                name = p.get("name", "Unnamed")
                self.prompt_selector.addItem(name, p)
        else:
            self.prompt_selector.addItem("No Workshop Prompts")
            self.prompt_selector.setEnabled(False)
        self.prompt_selector.currentIndexChanged.connect(self.prompt_selection_changed)
        buttons_layout.addWidget(self.prompt_selector)

        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon("assets/icons/send.svg"))
        self.send_button.clicked.connect(self.send_message)
        buttons_layout.addWidget(self.send_button)

        self.context_button = QPushButton()
        self.context_button.setCheckable(True)
        self.context_button.setIcon(QIcon("assets/icons/book.svg"))
        self.context_button.clicked.connect(self.toggle_context_panel)
        buttons_layout.addWidget(self.context_button)

        self.model_label = QLabel("Model: [None]")
        buttons_layout.addWidget(self.model_label)
        buttons_layout.addStretch()

        left_layout.addLayout(buttons_layout)
        splitter.addWidget(left_container)

        # Context Panel
        self.context_panel = ContextPanel(self.structure, self.project_name, parent=self)
        self.context_panel.setVisible(False)
        splitter.addWidget(self.context_panel)
        splitter.setSizes([500, 300])

        chat_layout.addWidget(splitter)
        outer_splitter.addWidget(chat_panel)
        outer_splitter.setStretchFactor(1, 3)

        main_layout.addWidget(outer_splitter)

    def prompt_selection_changed(self, index):
        if not self.prompt_selector.isEnabled():
            return
        prompt_config = self.prompt_selector.itemData(index)
        if prompt_config:
            self.workshop_prompt_config = prompt_config
            provider = prompt_config.get("provider", "Local")
            model = prompt_config.get("model", "Local Model")
            self.model_label.setText(f"Model: {provider}/{model}")

    def mode_changed(self, index):
        mode = self.mode_selector.currentText()
        print("Selected mode:", mode)
        self.current_mode = mode

    def toggle_context_panel(self):
        if self.context_panel.isVisible():
            self.context_panel.setVisible(False)
            self.context_button.setIcon(QIcon("assets/icons/book.svg"))
        else:
            self.context_panel.setVisible(True)
            self.context_button.setIcon(QIcon("assets/icons/book-open.svg"))

    def new_conversation(self):
        new_chat_number = self.conversation_list.count() + 1
        new_chat_name = f"Chat {new_chat_number}"
        self.conversations[new_chat_name] = []
        self.conversation_list.addItem(new_chat_name)
        self.current_conversation = new_chat_name
        self.conversation_history = self.conversations[new_chat_name]
        self.chat_log.clear()
        self.save_conversations()

    def get_scene_text(self, scene_name):
        print(f"DEBUG: Looking for scene content for: {scene_name}")
        for act in self.structure.get("acts", []):
            for chapter in act.get("chapters", []):
                for scene in chapter.get("scenes", []):
                    if scene.get("name", "").lower() == scene_name.lower():
                        content = load_latest_autosave(self.project_name, [act.get("name"), chapter.get("name"), scene.get("name")])
                        return content or f"[No content for scene {scene_name}]"
        print(f"DEBUG: No scene content found for: {scene_name}")
        return f"[No content for scene {scene_name}]"

    def get_item_hierarchy(self, item):
        """Helper method to get the hierarchy of a tree item (used by ContextPanel)."""
        hierarchy = []
        while item:
            hierarchy.insert(0, item.text(0))
            item = item.parent()
        return hierarchy

    def send_message(self):
        user_message = self.chat_input.toPlainText().strip()
        if not user_message:
            return

        augmented_message = user_message

        # Add selected context from ContextPanel
        context_text = self.context_panel.get_selected_context_text()
        if context_text:
            augmented_message += "\n\nContext:\n" + context_text

        self.chat_log.append("You: " + user_message)
        self.chat_input.clear()
        self.chat_log.append("LLM: Generating response...")
        QApplication.processEvents()

        conversation_payload = list(self.conversation_history)
        if not conversation_payload and self.workshop_prompt_config:
            conversation_payload.append({
                "role": "system",
                "content": self.workshop_prompt_config.get("text", "")
            })
        conversation_payload.append({"role": "user", "content": augmented_message})

        overrides = {}
        if self.workshop_prompt_config:
            overrides = {
                "provider": self.workshop_prompt_config.get("provider", "Local"),
                "model": self.workshop_prompt_config.get("model", "Local Model"),
                "max_tokens": self.workshop_prompt_config.get("max_tokens", 2000),
                "temperature": self.workshop_prompt_config.get("temperature", 1.0)
            }

        try:
            if estimate_conversation_tokens(conversation_payload) > TOKEN_LIMIT:
                summary = summarize_conversation(conversation_payload)
                conversation_payload = [conversation_payload[0], {"role": "system", "content": summary}]
                self.chat_log.append("LLM: [Conversation summarized to reduce token count.]")

            retrieved_context = self.embedding_index.query(user_message)
            if retrieved_context:
                augmented_message += "\n[Retrieved Context]:\n" + "\n".join(retrieved_context)

            token_count = estimate_conversation_tokens(conversation_payload)
            self.model_label.setText(
                f"Model: {overrides.get('provider', 'Local')}/{overrides.get('model', 'Local Model')} ({token_count} tokens sent)"
            )

            response = WWApiAggregator.send_prompt_to_llm("", overrides=overrides, conversation_history=conversation_payload)

            self.chat_log.append("LLM: " + response)
            QApplication.processEvents()

            self.conversation_history = conversation_payload
            self.conversation_history.append({"role": "assistant", "content": response})
            self.conversations[self.current_conversation] = self.conversation_history
            self.save_conversations()

            self.embedding_index.add_text(user_message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate response: {e}")

    def load_conversation_from_list(self, item: QListWidgetItem):
        selected_name = item.text()
        self.current_conversation = selected_name
        self.conversation_history = self.conversations.get(selected_name, [])
        self.chat_log.clear()
        for msg in self.conversation_history:
            role = msg.get("role", "Unknown")
            content = msg.get("content", "")
            self.chat_log.append(f"{role.capitalize()}: {content}")

    def show_conversation_context_menu(self, pos: QPoint):
        item = self.conversation_list.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.conversation_list.mapToGlobal(pos))
        if action == rename_action:
            self.rename_conversation(item)
        elif action == delete_action:
            self.delete_conversation(item)

    def rename_conversation(self, item: QListWidgetItem):
        current_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename Conversation", "Enter new conversation name:", text=current_name)
        if ok and new_name.strip():
            new_name = new_name.strip()
            self.conversations[new_name] = self.conversations.pop(current_name)
            item.setText(new_name)
            if self.current_conversation == current_name:
                self.current_conversation = new_name
            self.save_conversations()

    def delete_conversation(self, item: QListWidgetItem):
        conversation_name = item.text()
        reply = QMessageBox.question(self, "Delete Conversation", f"Are you sure you want to delete '{conversation_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = self.conversation_list.row(item)
            self.conversation_list.takeItem(row)
            if conversation_name in self.conversations:
                del self.conversations[conversation_name]
            if self.current_conversation == conversation_name:
                if self.conversation_list.count() > 0:
                    new_item = self.conversation_list.item(0)
                    self.current_conversation = new_item.text()
                    self.conversation_history = self.conversations.get(self.current_conversation, [])
                    self.load_conversation_from_list(new_item)
                else:
                    self.current_conversation = "Chat 1"
                    self.conversations[self.current_conversation] = []
                    self.conversation_list.addItem(self.current_conversation)
                    self.chat_log.clear()
            self.save_conversations()

    def load_conversations(self):
        if os.path.exists("conversations.json"):
            try:
                with open("conversations.json", "r", encoding="utf-8") as f:
                    self.conversations = json.load(f)
                self.conversation_list.clear()
                for conv_name in self.conversations:
                    self.conversation_list.addItem(conv_name)
                if self.conversations:
                    self.current_conversation = list(self.conversations.keys())[0]
                    self.conversation_history = self.conversations[self.current_conversation]
                else:
                    self.current_conversation = "Chat 1"
                    self.conversation_history = []
            except Exception as e:
                print("Error loading conversations:", e)
        else:
            self.conversations = {"Chat 1": []}
            self.current_conversation = "Chat 1"
            self.conversation_list.clear()
            self.conversation_list.addItem("Chat 1")

    def save_conversations(self):
        try:
            with open("conversations.json", "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, indent=4)
        except Exception as e:
            print("Error saving conversations:", e)

    def closeEvent(self, event):
        self.save_conversations()
        event.accept()

# For testing standalone
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = WorkshopWindow()
    window.show()
    sys.exit(app.exec_())
