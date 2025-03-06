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
from PyQt5.QtGui import QIcon  # Added import for icons
from prompts import load_project_options, get_workshop_prompts
from llm_integration import send_prompt_to_llm
from conversation_history_manager import estimate_conversation_tokens, summarize_conversation, prune_conversation_history
from embedding_manager import EmbeddingIndex  # New import for FAISS embedding integration

TOKEN_LIMIT = 2000

# --- New: Helper Functions for Compendium File Handling ---

def sanitize(text):
    return re.sub(r'\W+', '', text)

def get_compendium_filepath(project_name=None):
    """
    Build the compendium file path.
    If a project_name is provided, use Projects/<sanitized_project_name>/compendium.json.
    Otherwise, default to "compendium.json" in the current directory.
    """
    if project_name:
        project_name_sanitized = sanitize(project_name)
        return os.path.join(os.getcwd(), "Projects", project_name_sanitized, "compendium.json")
    return "compendium.json"

def get_compendium_data(project_name=None):
    """
    Load compendium data from the project-specific file if available.
    Converts legacy dictionary format to new list-of-categories format if necessary.
    """
    filename = get_compendium_filepath(project_name)
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check for legacy format: if "categories" is a dict, convert it.
            categories = data.get("categories", [])
            if isinstance(categories, dict):
                new_categories = []
                for cat, entries in categories.items():
                    new_categories.append({"name": cat, "entries": entries})
                data["categories"] = new_categories
            return data
        except Exception as e:
            print("Error loading compendium data:", e)
    return {"categories": []}

def get_compendium_text(category, entry, project_name=None):
    """
    Retrieve the compendium text for a given category and entry.
    Expects compendium data in the new format: a list of category objects.
    """
    data = get_compendium_data(project_name)
    categories = data.get("categories", [])
    for cat in categories:
        if cat.get("name") == category:
            for e in cat.get("entries", []):
                if e.get("name") == entry:
                    return e.get("content", f"[No content for {entry} in category {category}]")
    return f"[No content for {entry} in category {category}]"

def parse_compendium_references(message):
    """
    Parse compendium references from a message.
    Uses the project-specific compendium file if available.
    """
    filename = get_compendium_filepath()  # defaults to global if no project is provided
    refs = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                compendium = json.load(f)
            # Handle both legacy (dict) and new (list) formats.
            names = []
            cats = compendium.get("categories", [])
            if isinstance(cats, dict):
                names = list(cats.keys())
            elif isinstance(cats, list):
                for cat in cats:
                    for entry in cat.get("entries", []):
                        names.append(entry.get("name", ""))
            for name in names:
                if name and re.search(r'\b' + re.escape(name) + r'\b', message, re.IGNORECASE):
                    refs.append(name)
        except Exception as e:
            print("Error parsing compendium references:", e)
    return refs

# --- End Helper Functions ---

class ExtendedContextDialog(QDialog):
    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded
        self.setWindowTitle("Select Context")
        # Only resize if not embedded
        if not self.embedded:
            self.resize(500, 400)
        self.selected_contexts = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Use a QSplitter for side-by-side panels
        splitter = QSplitter(Qt.Horizontal, self)
        
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self.build_project_tree()
        self.project_tree.itemChanged.connect(self.handle_item_changed)
        splitter.addWidget(self.project_tree)
        
        self.compendium_tree = QTreeWidget()
        self.compendium_tree.setHeaderHidden(True)
        self.build_compendium_tree()
        self.compendium_tree.itemChanged.connect(self.handle_item_changed)
        splitter.addWidget(self.compendium_tree)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
        # Only add the OK button if not embedded.
        if not self.embedded:
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.on_ok)
            layout.addWidget(ok_button)

    def build_project_tree(self):
        self.project_tree.clear()
        structure = None
        if self.parent() is not None and hasattr(self.parent(), "structure"):
            structure = self.parent().structure
        if structure is None:
            structure = {"acts": []}
        for act in structure.get("acts", []):
            act_item = QTreeWidgetItem(
                self.project_tree, [act.get("name", "Unnamed Act")]
            )
            act_item.setFlags(act_item.flags() & ~Qt.ItemIsUserCheckable)
            for chapter in act.get("chapters", []):
                chap_item = QTreeWidgetItem(
                    act_item, [chapter.get("name", "Unnamed Chapter")]
                )
                chap_item.setFlags(chap_item.flags() & ~Qt.ItemIsUserCheckable)
                for scene in chapter.get("scenes", []):
                    scene_item = QTreeWidgetItem(
                        chap_item, [scene.get("name", "Unnamed Scene")]
                    )
                    # Only scene items are checkable
                    scene_item.setFlags(scene_item.flags() | Qt.ItemIsUserCheckable)
                    scene_item.setCheckState(0, Qt.Unchecked)
        self.project_tree.expandAll()

    def build_compendium_tree(self):
        self.compendium_tree.clear()
        # Use the project-specific compendium file path
        project_name = "DefaultProject"
        if self.parent() is not None and hasattr(self.parent(), "project_name"):
            project_name = self.parent().project_name
        data = get_compendium_data(project_name)
        categories = data.get("categories", [])
        for cat in categories:
            cat_name = cat.get("name", "Unnamed Category")
            entries = cat.get("entries", [])
            cat_item = QTreeWidgetItem(self.compendium_tree, [cat_name])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsUserCheckable)
            for entry in sorted(entries, key=lambda e: e.get("name", "")):
                entry_name = entry.get("name", "Unnamed Entry")
                entry_item = QTreeWidgetItem(cat_item, [entry_name])
                entry_item.setFlags(entry_item.flags() | Qt.ItemIsUserCheckable)
                entry_item.setCheckState(0, Qt.Unchecked)
                entry_item.setData(
                    0, Qt.UserRole, {"type": "compendium", "category": cat_name, "label": entry_name}
                )
        self.compendium_tree.expandAll()

    def handle_item_changed(self, item, column):
        if item.flags() & Qt.ItemIsUserCheckable:
            state = item.checkState(column)
            for i in range(item.childCount()):
                child = item.child(i)
                if child.flags() & Qt.ItemIsUserCheckable:
                    child.setCheckState(0, state)
            self.update_parent(item)

    def update_parent(self, item):
        parent = item.parent()
        if not parent or not (parent.flags() & Qt.ItemIsUserCheckable):
            return
        checked = 0
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.checkState(0) == Qt.Checked:
                checked += 1
        if checked == parent.childCount():
            parent.setCheckState(0, Qt.Checked)
        elif checked > 0:
            parent.setCheckState(0, Qt.PartiallyChecked)
        else:
            parent.setCheckState(0, Qt.Unchecked)
        self.update_parent(parent)

    def get_selected_contexts(self):
        selections = []

        def traverse(item):
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                selections.append(item.text(0))
            else:
                for i in range(item.childCount()):
                    traverse(item.child(i))
        root = self.project_tree.invisibleRootItem()
        for i in range(root.childCount()):
            traverse(root.child(i))
        for i in range(self.compendium_tree.topLevelItemCount()):
            cat_item = self.compendium_tree.topLevelItem(i)
            category = cat_item.text(0)
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                if entry_item.checkState(0) == Qt.Checked:
                    selections.append(f"{category}: {entry_item.text(0)}")
        return selections

    def on_ok(self):
        self.selected_contexts = self.get_selected_contexts()
        if not self.selected_contexts:
            QMessageBox.warning(
                self, "No Selection", "Please select at least one scene or compendium entry."
            )
            return
        self.accept()

class WorkshopWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workshop")
        # Allow the user to maximize the window by including the maximize hint.
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.resize(1000, 600)
        # Optionally, start maximized:
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        if self.parent() is not None and hasattr(self.parent(), "project_name"):
            self.project_name = self.parent().project_name
        else:
            self.project_name = "DefaultProject"
        if self.parent() is not None and hasattr(self.parent(), "structure"):
            self.structure = self.parent().structure
        else:
            self.structure = {"acts": []}
        self.workshop_prompt_config = None

        # Conversation management:
        self.conversation_history = []  # current active conversation history
        self.conversations = {}         # dict mapping conversation name -> history list
        self.current_conversation = "Chat 1"
        # Ensure there's at least a default conversation.
        self.conversations[self.current_conversation] = []

        # Initialize the embedding index for context retrieval.
        self.embedding_index = EmbeddingIndex()

        self.current_mode = "Normal"  # default mode

        # Build UI elements first.
        self.init_ui()
        # Then load saved conversations (this updates the conversation_list widget).
        self.load_conversations()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Outer splitter divides conversation list and the chat panel.
        outer_splitter = QSplitter(Qt.Horizontal)

        # --- Conversation History Panel ---
        conversation_container = QWidget()
        conversation_layout = QVBoxLayout(conversation_container)
        conversation_layout.setContentsMargins(0, 0, 0, 0)

        self.conversation_list = QListWidget()
        self.conversation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.conversation_list.customContextMenuRequested.connect(self.show_conversation_context_menu)
        self.conversation_list.itemClicked.connect(self.load_conversation_from_list)
        conversation_layout.addWidget(self.conversation_list)

        # Create and add the "New Chat" button.
        new_chat_button = QPushButton("New Chat")
        new_chat_button.clicked.connect(self.new_conversation)
        conversation_layout.addWidget(new_chat_button)

        outer_splitter.addWidget(conversation_container)
        outer_splitter.setStretchFactor(0, 1)

        # --- Chat Panel ---
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        
        # Chat log (display area)
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

        # --- Buttons and Mode/Prompt Selector ---
        buttons_layout = QHBoxLayout()

        # Add pulldown menu for mode selection (Normal, Economy, Ultra-Light)
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Normal", "Economy", "Ultra-Light"])
        self.mode_selector.currentIndexChanged.connect(self.mode_changed)
        buttons_layout.addWidget(self.mode_selector)

        # Workshop Prompt pulldown menu instead of a button.
        self.prompt_selector = QComboBox()
        prompts = get_workshop_prompts(self.project_name)
        if prompts:
            for p in prompts:
                name = p.get("name", "Unnamed")
                # Store the entire prompt configuration as the associated data.
                self.prompt_selector.addItem(name, p)
        else:
            self.prompt_selector.addItem("No Workshop Prompts")
            self.prompt_selector.setEnabled(False)
        self.prompt_selector.currentIndexChanged.connect(self.prompt_selection_changed)
        buttons_layout.addWidget(self.prompt_selector)

        # Send button: remove text and set icon from assets/icons folder
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon("assets/icons/send.svg"))
        self.send_button.clicked.connect(self.send_message)
        buttons_layout.addWidget(self.send_button)

        # Context button: remove text and set icon; update icon on toggle
        self.context_button = QPushButton()
        self.context_button.setCheckable(True)
        self.context_button.setIcon(QIcon("assets/icons/book.svg"))
        self.context_button.clicked.connect(self.toggle_context_panel)
        buttons_layout.addWidget(self.context_button)

        # Model label
        self.model_label = QLabel("Model: [None]")
        buttons_layout.addWidget(self.model_label)
        buttons_layout.addStretch()

        left_layout.addLayout(buttons_layout)
        splitter.addWidget(left_container)

        # Context panel (embedded ExtendedContextDialog)
        self.context_panel = QWidget()
        context_layout = QVBoxLayout(self.context_panel)
        context_splitter = QSplitter(Qt.Horizontal, self.context_panel)

        self.extended_context_dialog = ExtendedContextDialog(self, embedded=True)
        self.extended_context_dialog.setWindowFlags(Qt.Widget)
        context_splitter.addWidget(self.extended_context_dialog.project_tree)
        context_splitter.addWidget(self.extended_context_dialog.compendium_tree)
        context_splitter.setStretchFactor(0, 1)
        context_splitter.setStretchFactor(1, 1)
        context_layout.addWidget(context_splitter)
        self.context_panel.setLayout(context_layout)
        self.context_panel.setVisible(False)
        splitter.addWidget(self.context_panel)
        splitter.setSizes([500, 300])
        
        chat_layout.addWidget(splitter)
        outer_splitter.addWidget(chat_panel)
        outer_splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(outer_splitter)

    def prompt_selection_changed(self, index):
        """Called when a workshop prompt is selected from the pulldown menu."""
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
                        print(f"DEBUG: Found scene content: {scene.get('content')}")
                        return scene.get("content", f"[No content for scene {scene_name}]")
        print(f"DEBUG: No scene content found for: {scene_name}")
        return f"[No content for scene {scene_name}]"

    def send_message(self):
        user_message = self.chat_input.toPlainText().strip()
        if not user_message:
            return

        augmented_message = user_message

        # Add any selected contexts from the extended context dialog.
        contexts = self.extended_context_dialog.get_selected_contexts()
        print("DEBUG: Selected contexts:", contexts)
        if contexts:
            augmented_message += "\nContext:\n"
            for ctx in contexts:
                print("DEBUG: Processing context:", ctx)
                if ":" in ctx:
                    category, entry = ctx.split(":", 1)
                    category = category.strip()
                    entry = entry.strip()
                    compendium_text = get_compendium_text(category, entry, self.project_name)
                    print(f"DEBUG: Retrieved compendium text for {category} - {entry}: {compendium_text}")
                    augmented_message += f"\n[Compendium {category} - {entry}]:\n{compendium_text}\n"
                else:
                    print("DEBUG: Detected scene context:", ctx)
                    scene_text = self.get_scene_text(ctx)
                    augmented_message += f"\n[Scene {ctx}]:\n{scene_text}\n"

        # Append message to chat log.
        self.chat_log.append("You: " + user_message)
        self.chat_input.clear()
        self.chat_log.append("LLM: Generating response...")
        QApplication.processEvents()

        # Maintain conversation history.
        conversation_payload = list(self.conversation_history)
        if not conversation_payload and self.workshop_prompt_config:
            conversation_payload.append({
                "role": "system",
                "content": self.workshop_prompt_config.get("text", "")
            })
        conversation_payload.append({"role": "user", "content": augmented_message})

        # Depending on the mode, adjust overrides or summarization strategies.
        overrides = {}
        if self.workshop_prompt_config:
            overrides = {
                "provider": self.workshop_prompt_config.get("provider", "Local"),
                "model": self.workshop_prompt_config.get("model", "Local Model"),
                "max_tokens": self.workshop_prompt_config.get("max_tokens", 2000),
                "temperature": self.workshop_prompt_config.get("temperature", 1.0)
            }

        # Summarize or prune conversation if token limit is exceeded.
        if estimate_conversation_tokens(conversation_payload) > TOKEN_LIMIT:
            summary = summarize_conversation(conversation_payload)
            conversation_payload = [conversation_payload[0], {"role": "system", "content": summary}]
            self.chat_log.append("LLM: [Conversation summarized to reduce token count.]")

        # Retrieve additional context using FAISS based on the user message.
        retrieved_context = self.embedding_index.query(user_message)
        if retrieved_context:
            augmented_message += "\n[Retrieved Context]:\n" + "\n".join(retrieved_context)

        token_count = estimate_conversation_tokens(conversation_payload)
        self.model_label.setText(
            f"Model: {overrides.get('provider', 'Local')}/{overrides.get('model', 'Local Model')} ({token_count} tokens sent)"
        )

        response = send_prompt_to_llm("", overrides=overrides, conversation_history=conversation_payload)

        self.chat_log.append("LLM: " + response)
        QApplication.processEvents()

        self.conversation_history = conversation_payload
        self.conversation_history.append({"role": "assistant", "content": response})
        self.conversations[self.current_conversation] = self.conversation_history
        self.save_conversations()

        # Add the user message to the embedding index for future context retrieval.
        self.embedding_index.add_text(user_message)

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
        """Load saved conversations from a JSON file (if it exists) and update the conversation list widget."""
        if os.path.exists("conversations.json"):
            try:
                with open("conversations.json", "r", encoding="utf-8") as f:
                    self.conversations = json.load(f)
                # Update the conversation list widget
                self.conversation_list.clear()
                for conv_name in self.conversations:
                    self.conversation_list.addItem(conv_name)
                # Set the current conversation
                if self.conversations:
                    self.current_conversation = list(self.conversations.keys())[0]
                    self.conversation_history = self.conversations[self.current_conversation]
                else:
                    self.current_conversation = "Chat 1"
                    self.conversation_history = []
            except Exception as e:
                print("Error loading conversations:", e)
        else:
            # No file yet; start with a default conversation.
            self.conversations = {"Chat 1": []}
            self.current_conversation = "Chat 1"
            self.conversation_list.clear()
            self.conversation_list.addItem("Chat 1")

    def save_conversations(self):
        """Save current conversations to a JSON file."""
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
