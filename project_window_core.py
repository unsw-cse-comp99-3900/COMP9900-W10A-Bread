import os
import time
import glob
import json
import re
import threading

import pyttsx3  # (Not used directly anymore for TTS, but left for legacy if needed)
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QToolBar, QAction, QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QWidget, QMessageBox, QStackedWidget,
    QInputDialog, QMenu, QComboBox, QApplication, QTabWidget
)
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat
from PyQt5.QtCore import Qt, QTimer, QEvent

from compendium import CompendiumWindow
from workshop import WorkshopWindow  # In case needed
from llm_integration import send_prompt_to_llm, get_prose_prompts, build_final_prompt
from rewrite_feature import RewriteDialog  # Using the dialog from rewrite_feature.py
from backup_manager import show_backup_dialog
from summary_feature import create_summary as create_summary_feature
from prompts import load_project_options

from tree_manager import load_structure, save_structure, populate_tree, update_structure_from_tree, delete_node
from context_panel import ContextPanel

# Import our new TTS manager module
import tts_manager

# The global PROJECT_SETTINGS_FILE remains for autosave-related settings.
PROJECT_SETTINGS_FILE = "project_settings.json"


class CreateSummaryDialog(QDialog):
    """
    A dialog for creating a summary.
    It presents an editable field with a default summarizer prompt.
    """
    def __init__(self, default_prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Summary")
        self.prompt = ""
        self.init_ui(default_prompt)
        
    def init_ui(self, default_prompt):
        layout = QVBoxLayout(self)
        label = QLabel("Edit summarizer prompt:")
        layout.addWidget(label)
        self.prompt_edit = QLineEdit(default_prompt)
        layout.addWidget(self.prompt_edit)
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Okay")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def accept(self):
        self.prompt = self.prompt_edit.text().strip()
        if not self.prompt:
            QMessageBox.warning(self, "Input Error", "The summarizer prompt cannot be empty.")
            return
        super().accept()


class ProjectWindow(QMainWindow):
    """
    Main project window with tree view, formatting and scene settings toolbars,
    scene editing, autosave, and integration with LLM/prompt functions.
    The tree structure (acts, chapters, scenes) is persisted to a project-specific file.
    Global settings for POV, POV Character, and Tense persist across sessions.
    """
    def __init__(self, project_name):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle(f"Project: {project_name}")
        self.resize(900, 600)
        # Global persistent settings (applied across all scenes)
        self.current_pov = "Third Person"
        self.current_pov_character = "Character"
        self.current_tense = "Present Tense"
        
        self.current_prose_prompt = None
        self.current_prose_config = None
        self.tts_playing = False  # Track TTS state

        # Load the persistent project structure using our tree manager.
        self.structure = load_structure(self.project_name)

        self.init_ui()
        self.load_autosave_setting()
        if self.autosave_enabled:
            self.start_autosave_timer()
        if self.tree.topLevelItemCount() > 0:
            act_item = self.tree.topLevelItem(0)
            if act_item.childCount() > 0:
                chapter_item = act_item.child(0)
                if chapter_item.childCount() > 0:
                    self.tree.setCurrentItem(chapter_item.child(0))
        # Set initial tooltips reflecting the global settings.
        self.updateSettingTooltips()
    
    def updateSettingTooltips(self):
        """Update the tooltips for the POV, POV Character, and Tense buttons."""
        self.pov_button.setToolTip(f"POV: {self.current_pov}")
        self.pov_character_button.setToolTip(f"POV Character: {self.current_pov_character}")
        self.tense_button.setToolTip(f"Tense: {self.current_tense}")
    
    def load_autosave_setting(self):
        """Load autosave and global settings from PROJECT_SETTINGS_FILE."""
        self.autosave_enabled = False
        if os.path.exists(PROJECT_SETTINGS_FILE):
            try:
                with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    all_settings = json.load(f)
                project_settings = all_settings.get(self.project_name, {})
                self.autosave_enabled = project_settings.get("autosave", False)
                # Load global settings if they exist; otherwise keep defaults.
                self.current_pov = project_settings.get("global_pov", self.current_pov)
                self.current_pov_character = project_settings.get("global_pov_character", self.current_pov_character)
                self.current_tense = project_settings.get("global_tense", self.current_tense)
            except Exception as e:
                print("Error loading project settings for autosave:", e)
    
    def save_global_settings(self):
        """Save global settings (POV, POV Character, Tense) to PROJECT_SETTINGS_FILE."""
        settings = {}
        if os.path.exists(PROJECT_SETTINGS_FILE):
            try:
                with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except Exception as e:
                print("Error loading project settings:", e)
        project_settings = settings.get(self.project_name, {})
        project_settings["global_pov"] = self.current_pov
        project_settings["global_pov_character"] = self.current_pov_character
        project_settings["global_tense"] = self.current_tense
        settings[self.project_name] = project_settings
        try:
            with open(PROJECT_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print("Error saving project settings:", e)
    
    def populate_tree(self):
        """Populate the QTreeWidget from the structure using tree_manager."""
        populate_tree(self.tree, self.structure)
    
    def update_structure_from_tree(self):
        """Update the structure from the QTreeWidget and save it via tree_manager."""
        self.structure = update_structure_from_tree(self.tree, self.project_name)
    
    def get_summary_filename(self, item):
        """
        Generate a filename for the summary based on the selected tree item.
        """
        import re, os, time
        def sanitize(text):
            return re.sub(r'\W+', '', text)
        hierarchy = []
        temp = item
        while temp:
            hierarchy.insert(0, temp.text(0).strip())
            temp = temp.parent()
        sanitized = [sanitize(x) for x in hierarchy]
        filename = f"{sanitize(self.project_name)}-Summary-" + "-".join(sanitized) + ".txt"
        project_folder = os.path.join(os.getcwd(), "Projects", sanitize(self.project_name))
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        return os.path.join(project_folder, filename)
    
    def rename_item(self, item):
        """
        Prompt the user to rename the selected item. Update the item's text
        and underlying data (ensuring that the 'name' key is updated).
        """
        current_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=current_name)
        if ok and new_name.strip():
            new_name = new_name.strip()
            item.setText(0, new_name)
            data = item.data(0, Qt.UserRole)
            if isinstance(data, dict):
                data["name"] = new_name
            else:
                data = {"name": new_name}
            item.setData(0, Qt.UserRole, data)
            self.update_structure_from_tree()
    
    def init_ui(self):
        self.setStatusBar(self.statusBar())
        
        # --- Global Toolbar (top of window) ---
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        compendium_action = QAction(QIcon.fromTheme("book"), "Compendium", self)
        compendium_action.setStatusTip("Open Compendium")
        compendium_action.triggered.connect(self.open_compendium)
        toolbar.addAction(compendium_action)
        
        prompt_options_action = QAction(QIcon.fromTheme("document-properties"), "Prompt Options", self)
        prompt_options_action.setStatusTip("Configure your writing prompts")
        prompt_options_action.triggered.connect(self.open_prompts_window)
        toolbar.addAction(prompt_options_action)
        
        workshop_action = QAction(QIcon.fromTheme("chat"), "Workshop", self)
        workshop_action.setStatusTip("Open Workshop Chat")
        workshop_action.triggered.connect(self.open_workshop)
        toolbar.addAction(workshop_action)
        
        # --- Main Layout Splitter ---
        main_splitter = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project Structure")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.populate_tree()
        self.tree.currentItemChanged.connect(self.tree_item_changed)
        main_splitter.addWidget(self.tree)
        
        top_right = QWidget()
        top_right_layout = QVBoxLayout(top_right)
        
        # --- Formatting Toolbar (above the editor) ---
        self.formatting_toolbar = QHBoxLayout()
        bold_button = QPushButton("B")
        bold_button.setCheckable(True)
        bold_button.setStyleSheet("font-weight: bold;")
        bold_button.clicked.connect(self.toggle_bold)
        self.formatting_toolbar.addWidget(bold_button)
        italic_button = QPushButton("I")
        italic_button.setCheckable(True)
        italic_button.setStyleSheet("font-style: italic;")
        italic_button.clicked.connect(self.toggle_italic)
        self.formatting_toolbar.addWidget(italic_button)
        underline_button = QPushButton("U")
        underline_button.setCheckable(True)
        underline_button.setStyleSheet("text-decoration: underline;")
        underline_button.clicked.connect(self.toggle_underline)
        self.formatting_toolbar.addWidget(underline_button)
        self.tts_button = QPushButton("TTS")
        self.tts_button.setToolTip("Read selected text (or entire scene if nothing is selected)")
        self.tts_button.clicked.connect(self.toggle_tts)
        self.formatting_toolbar.addWidget(self.tts_button)
        self.formatting_toolbar.addStretch()
        top_right_layout.addLayout(self.formatting_toolbar)
        
        # --- Editor Widget ---
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a node to edit its content...")
        top_right_layout.addWidget(self.editor)
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_editor_context_menu)
        
        # --- Scene Settings Toolbar ---
        self.scene_settings_toolbar = QWidget()
        scene_settings_layout = QHBoxLayout(self.scene_settings_toolbar)
        
        save_group = QWidget()
        save_layout = QHBoxLayout(save_group)
        self.manual_save_button = QPushButton("Manual Save")
        self.manual_save_button.setToolTip("Manually save the current scene")
        self.manual_save_button.clicked.connect(self.manual_save_scene)
        save_layout.addWidget(self.manual_save_button)
        self.oh_shit_button = QPushButton("Oh Shit")
        self.oh_shit_button.setToolTip("Show backup versions for this scene")
        self.oh_shit_button.clicked.connect(self.on_oh_shit)
        save_layout.addWidget(self.oh_shit_button)
        save_layout.addStretch()
        
        pov_group = QWidget()
        pov_layout = QHBoxLayout(pov_group)
        self.pov_button = QPushButton("POV")
        self.pov_button.setToolTip(f"POV: {self.current_pov}")
        self.pov_button.clicked.connect(self.set_pov)
        pov_layout.addWidget(self.pov_button)
        self.pov_character_button = QPushButton("POV Character")
        self.pov_character_button.setToolTip(f"POV Character: {self.current_pov_character}")
        self.pov_character_button.clicked.connect(self.set_pov_character)
        pov_layout.addWidget(self.pov_character_button)
        self.tense_button = QPushButton("Tense")
        self.tense_button.setToolTip(f"Tense: {self.current_tense}")
        self.tense_button.clicked.connect(self.set_tense)
        pov_layout.addWidget(self.tense_button)
        pov_layout.addStretch()
        
        scene_settings_layout.addWidget(save_group)
        scene_settings_layout.addSpacing(20)
        scene_settings_layout.addWidget(pov_group)
        scene_settings_layout.addStretch()
        top_right_layout.addWidget(self.scene_settings_toolbar)
        
        # --- Bottom Panel (LLM and Summary) ---
        self.bottom_stack = QStackedWidget()
        
        self.summary_panel = QWidget()
        summary_layout = QHBoxLayout(self.summary_panel)
        summary_layout.addStretch()
        self.create_summary_button = QPushButton("Create Summary")
        self.create_summary_button.clicked.connect(self.create_summary)
        summary_layout.addWidget(self.create_summary_button)
        self.save_summary_button = QPushButton("Save Summary")
        self.save_summary_button.clicked.connect(self.save_summary)
        summary_layout.addWidget(self.save_summary_button)
        summary_layout.addStretch()
        
        self.llm_panel = QWidget()
        llm_layout = QVBoxLayout(self.llm_panel)
        input_context_layout = QHBoxLayout()
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your action beats here...")
        self.prompt_input.setMinimumHeight(100)
        left_layout.addWidget(self.prompt_input)
        
        left_buttons_layout = QHBoxLayout()
        self.prompt_button = QPushButton("Prompt")
        self.prompt_button.setToolTip("Select a prose prompt")
        self.prompt_button.clicked.connect(self.select_prose_prompt)
        left_buttons_layout.addWidget(self.prompt_button)
        
        self.send_button = QPushButton("Send")
        self.send_button.setToolTip("Send the prompt to the LLM")
        self.send_button.clicked.connect(self.send_prompt)
        left_buttons_layout.addWidget(self.send_button)
        
        self.context_toggle_button = QPushButton("Context")
        self.context_toggle_button.setToolTip("Show extra context settings")
        self.context_toggle_button.setCheckable(True)
        self.context_toggle_button.clicked.connect(self.toggle_context_panel)
        left_buttons_layout.addWidget(self.context_toggle_button)
        left_buttons_layout.addStretch()
        left_layout.addLayout(left_buttons_layout)
        
        input_context_layout.addWidget(left_container, stretch=2)
        
        self.context_panel = ContextPanel(self.structure, self.project_name)
        self.context_panel.setVisible(False)
        input_context_layout.addWidget(self.context_panel, stretch=1)
        
        llm_layout.addLayout(input_context_layout)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("LLM output preview will appear here...")
        llm_layout.addWidget(self.preview_text)
        
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.setToolTip("Append the preview text to the scene")
        self.apply_button.clicked.connect(self.apply_preview)
        button_layout.addWidget(self.apply_button)
        self.retry_button = QPushButton("Retry")
        self.retry_button.setToolTip("Clear preview and re-send the prompt")
        self.retry_button.clicked.connect(self.retry_prompt)
        button_layout.addWidget(self.retry_button)
        button_layout.addStretch()
        llm_layout.addLayout(button_layout)
        
        self.bottom_stack.addWidget(self.summary_panel)
        self.bottom_stack.addWidget(self.llm_panel)
        
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(top_right)
        right_splitter.addWidget(self.bottom_stack)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(1, 1)
        self.setCentralWidget(main_splitter)
    
    def toggle_context_panel(self):
        if self.context_panel.isVisible():
            self.context_panel.setVisible(False)
            self.context_toggle_button.setText("Context")
        else:
            self.context_panel.build_project_tree()
            self.context_panel.build_compendium_tree()
            self.context_panel.setVisible(True)
            self.context_toggle_button.setText("Hide")
    
    def open_workshop(self):
        self.workshop_window = WorkshopWindow(self)
        self.workshop_window.show()
    
    def open_compendium(self):
        self.compendium_window = CompendiumWindow(self)
        self.compendium_window.exec_()
    
    def open_prompts_window(self):
        from prompts import PromptsWindow
        prompts_window = PromptsWindow(self.project_name, self)
        prompts_window.exec_()
    
    def show_editor_context_menu(self, pos):
        menu = self.editor.createStandardContextMenu()
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            rewrite_action = menu.addAction("Rewrite")
            rewrite_action.triggered.connect(self.rewrite_selected_text)
        menu.exec_(self.editor.mapToGlobal(pos))
    
    def rewrite_selected_text(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            QMessageBox.warning(self, "Rewrite", "No text selected to rewrite.")
            return
        selected_text = cursor.selectedText()
        dialog = RewriteDialog(self.project_name, selected_text, self)
        if dialog.exec_() == QDialog.Accepted:
            cursor.insertText(dialog.rewritten_text)
            self.editor.setTextCursor(cursor)
    
    def open_project_options(self):
        pass  # Deprecated.
    
    def tree_item_changed(self, current, previous):
        if current is None:
            self.editor.clear()
            self.bottom_stack.setCurrentIndex(0)
            self.scene_settings_toolbar.hide()
            return
        level = 0
        parent = current.parent()
        while parent:
            level += 1
            parent = parent.parent()
        content = current.data(0, Qt.UserRole)
        if isinstance(content, dict) and level >= 2:
            autosave_content = self.load_latest_autosave_for_item(current)
            if autosave_content is not None:
                content = autosave_content
            else:
                content = content.get("content", "")
        elif isinstance(content, dict) and level < 2:
            content = current.data(0, Qt.UserRole).get("summary", "")
        self.editor.setPlainText(content)
        if level < 2:
            self.editor.setPlaceholderText(f"Enter summary for {current.text(0)}...")
            self.bottom_stack.setCurrentIndex(0)
            self.scene_settings_toolbar.hide()
        else:
            self.editor.setPlaceholderText("Enter scene content...")
            self.bottom_stack.setCurrentIndex(1)
            self.scene_settings_toolbar.show()
        self.updateSettingTooltips()
    
    def load_latest_autosave_for_item(self, item):
        def sanitize(text):
            return re.sub(r'\W+', '', text)
        
        hierarchy = []
        current = item
        while current:
            hierarchy.insert(0, current.text(0).strip())
            current = current.parent()
        
        sanitized_hierarchy = [sanitize(x) for x in hierarchy]
        project_folder = os.path.join(os.getcwd(), "Projects", sanitize(self.project_name))
        pattern = os.path.join(project_folder, f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + "_*.txt")
        
        autosave_files = glob.glob(pattern)
        if not autosave_files:
            return None
            
        latest_file = max(autosave_files, key=os.path.getmtime)
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading autosave file {latest_file}: {e}")
            return None
    
    def show_tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        menu = QMenu()
        if item is None:
            add_act_action = menu.addAction("Add Act")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == add_act_action:
                self.add_act()
            return
        
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        move_up_action = menu.addAction("Move Up")
        move_down_action = menu.addAction("Move Down")
        
        level = 0
        temp = item
        while temp.parent():
            level += 1
            temp = temp.parent()
        
        if level == 0:
            add_chapter_action = menu.addAction("Add Chapter")
        elif level == 1:
            add_scene_action = menu.addAction("Add Scene")
            
        action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
        if action == rename_action:
            self.rename_item(item)
        elif action == delete_action:
            delete_node(self.tree, item, self.project_name)
        elif action == move_up_action:
            self.move_item_up(item)
        elif action == move_down_action:
            self.move_item_down(item)
        elif level == 0 and 'add_chapter_action' in locals() and action == add_chapter_action:
            self.add_chapter(item)
        elif level == 1 and 'add_scene_action' in locals() and action == add_scene_action:
            self.add_scene(item)
    
    def move_item_up(self, item):
        parent = item.parent() or self.tree.invisibleRootItem()
        index = parent.indexOfChild(item)
        if index > 0:
            parent.takeChild(index)
            parent.insertChild(index - 1, item)
            self.tree.setCurrentItem(item)
            self.update_structure_from_tree()
    
    def move_item_down(self, item):
        parent = item.parent() or self.tree.invisibleRootItem()
        index = parent.indexOfChild(item)
        if index < parent.childCount() - 1:
            parent.takeChild(index)
            parent.insertChild(index + 1, item)
            self.tree.setCurrentItem(item)
            self.update_structure_from_tree()
    
    def add_act(self):
        text, ok = QInputDialog.getText(self, "Add Act", "Enter act name:")
        if ok and text.strip():
            new_act = {
                "name": text.strip(),
                "summary": f"This is the summary for {text.strip()}.",
                "chapters": []
            }
            self.structure["acts"].append(new_act)
            self.populate_tree()
            save_structure(self.project_name, self.structure)
    
    def add_chapter(self, act_item):
        text, ok = QInputDialog.getText(self, "Add Chapter", "Enter chapter name:")
        if ok and text.strip():
            act_data = act_item.data(0, Qt.UserRole)
            new_chapter = {
                "name": text.strip(),
                "summary": f"This is the summary for {text.strip()}.",
                "scenes": []
            }
            if "chapters" not in act_data:
                act_data["chapters"] = []
            act_data["chapters"].append(new_chapter)
            chapter_item = QTreeWidgetItem(act_item, [text.strip()])
            chapter_item.setData(0, Qt.UserRole, new_chapter)
            self.populate_tree()
            save_structure(self.project_name, self.structure)
    
    def add_scene(self, chapter_item):
        text, ok = QInputDialog.getText(self, "Add Scene", "Enter scene name:")
        if ok and text.strip():
            chapter_data = chapter_item.data(0, Qt.UserRole)
            new_scene = {
                "name": text.strip(),
                "content": f"This is the scene content for {text.strip()}."
                # Global POV settings will be used; they are not stored per scene.
            }
            if "scenes" not in chapter_data:
                chapter_data["scenes"] = []
            chapter_data["scenes"].append(new_scene)
            scene_item = QTreeWidgetItem(chapter_item, [text.strip()])
            scene_item.setData(0, Qt.UserRole, new_scene)
            self.populate_tree()
            save_structure(self.project_name, self.structure)
    
    def manual_save_scene(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Manual Save", "No scene selected for saving.")
            return
        level = 0
        temp = current_item
        while temp.parent():
            level += 1
            temp = temp.parent()
        if level < 2:
            QMessageBox.warning(self, "Manual Save", "Please select a scene for manual save.")
            return
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Manual Save", "There is no content to save.")
            return
        
        def sanitize(text):
            return re.sub(r'\W+', '', text)
        
        hierarchy = []
        item = current_item
        while item:
            hierarchy.insert(0, item.text(0).strip())
            item = item.parent()
        
        sanitized_hierarchy = [sanitize(x) for x in hierarchy]
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + f"_{timestamp}.txt"
        project_folder = os.path.join(os.getcwd(), "Projects", sanitize(self.project_name))
        
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
            
        filepath = os.path.join(project_folder, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print("Autosaved scene to", filepath)
            self.statusBar().showMessage("Scene autosaved", 3000)
            
            scene_data = current_item.data(0, Qt.UserRole)
            if not isinstance(scene_data, dict):
                scene_data = {"name": current_item.text(0)}
            scene_data["content"] = content
            current_item.setData(0, Qt.UserRole, scene_data)
            self.update_structure_from_tree()
            
            pattern = os.path.join(project_folder, f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + "_*.txt")
            autosave_files = sorted(glob.glob(pattern))
            while len(autosave_files) > 6:
                oldest = autosave_files.pop(0)
                try:
                    os.remove(oldest)
                    print("Removed old autosave file:", oldest)
                except Exception as e:
                    print("Error removing old autosave file:", e)
        except Exception as e:
            print("Error during autosave:", e)
    
    def on_oh_shit(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Backup Versions", "No scene selected.")
            return
        level = 0
        temp = current_item
        while temp.parent():
            level += 1
            temp = temp.parent()
        if level < 2:
            QMessageBox.warning(self, "Backup Versions", "Please select a scene to view backups.")
            return
            
        scene_identifier = current_item.text(0)
        backup_file_path = show_backup_dialog(self, self.project_name, scene_identifier)
        
        if backup_file_path:
            try:
                with open(backup_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.setPlainText(content)
                
                scene_data = current_item.data(0, Qt.UserRole)
                if not isinstance(scene_data, dict):
                    scene_data = {"name": current_item.text(0)}
                scene_data["content"] = content
                current_item.setData(0, Qt.UserRole, scene_data)
                self.update_structure_from_tree()
                
                QMessageBox.information(self, "Backup Loaded", f"Backup loaded from:\n{backup_file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading backup file: {e}")
        else:
            QMessageBox.information(self, "Backup", "No backup file selected.")
    
    def set_pov(self):
        options = ["First Person", "Omniscient", "Third Person Limited", "Custom..."]
        current_value = self.current_pov
        try:
            default_index = options.index(current_value)
        except ValueError:
            default_index = 0
        item, ok = QInputDialog.getItem(self, "Select POV", "Choose POV:", options, default_index, False)
        if ok and item:
            if item == "Custom...":
                custom, ok2 = QInputDialog.getText(self, "Custom POV", "Enter custom POV:", text=(current_value if current_value not in options else ""))
                if ok2 and custom.strip():
                    self.current_pov = custom.strip()
                else:
                    return
            else:
                self.current_pov = item
            self.updateSettingTooltips()
            self.save_global_settings()
            QMessageBox.information(self, "POV Set", f"POV set to: {self.current_pov}")
    
    def set_pov_character(self):
        characters = ["Alice", "Bob", "Charlie", "Custom..."]
        current_value = self.current_pov_character
        try:
            default_index = characters.index(current_value)
        except ValueError:
            default_index = 0
        item, ok = QInputDialog.getItem(self, "Select POV Character", "Choose character:", characters, default_index, False)
        if ok and item:
            if item == "Custom...":
                custom, ok2 = QInputDialog.getText(self, "Custom POV Character", "Enter character name:", text=(current_value if current_value not in characters else ""))
                if ok2 and custom.strip():
                    self.current_pov_character = custom.strip()
                else:
                    return
            else:
                self.current_pov_character = item
            self.updateSettingTooltips()
            self.save_global_settings()
            QMessageBox.information(self, "POV Character Set", f"POV character set to: {self.current_pov_character}")
    
    def set_tense(self):
        options = ["Past Tense", "Present Tense", "Custom..."]
        current_value = self.current_tense
        try:
            default_index = options.index(current_value)
        except ValueError:
            default_index = 0
        item, ok = QInputDialog.getItem(self, "Select Tense", "Choose tense:", options, default_index, False)
        if ok and item:
            if item == "Custom...":
                custom, ok2 = QInputDialog.getText(self, "Custom Tense", "Enter tense:", text=(current_value if current_value not in options else ""))
                if ok2 and custom.strip():
                    self.current_tense = custom.strip()
                else:
                    return
            else:
                self.current_tense = item
            self.updateSettingTooltips()
            self.save_global_settings()
            QMessageBox.information(self, "Tense Set", f"Tense set to: {self.current_tense}")
    
    def select_prose_prompt(self):
        prose_prompts = get_prose_prompts(self.project_name)
        if not prose_prompts:
            default_prompt = ("You are collaborating with the author to write a scene. "
                              "Write the scene in {pov} point of view, from the perspective of {pov_character}, and in {tense}.")
            self.current_prose_prompt = default_prompt
            self.current_prose_config = None
            QMessageBox.information(self, "Default Prompt Loaded", "No custom Prose prompts found. The default prompt has been loaded.")
            return
        
        prompt_names = [p.get("name", "Unnamed") for p in prose_prompts]
        default_index = 0
        if self.current_prose_config:
            try:
                default_index = prompt_names.index(self.current_prose_config.get("name", ""))
            except ValueError:
                default_index = 0
        
        item, ok = QInputDialog.getItem(self, "Select Prose Prompt", "Choose a prompt:", prompt_names, default_index, False)
        if ok and item:
            for p in prose_prompts:
                if p.get("name", "") == item:
                    prompt_text = p.get("text", "")
                    options = load_project_options(self.project_name)
                    try:
                        prompt_text = prompt_text.format(**options)
                    except Exception as e:
                        print("Formatting prompt text failed:", e)
                    current = self.prompt_input.toPlainText()
                    if current:
                        self.prompt_input.setText(current + " " + prompt_text)
                    else:
                        self.prompt_input.setText(prompt_text)
                    self.current_prose_prompt = prompt_text
                    self.current_prose_config = p
                    break
            QMessageBox.information(self, "Prose Prompt Selected", f"Prose prompt selected:\n{self.current_prose_prompt}")
    
    def send_prompt(self):
        action_beats = self.prompt_input.toPlainText().strip()
        if not action_beats:
            QMessageBox.warning(self, "LLM Prompt", "Please enter some action beats before sending.")
            return
        
        if self.current_prose_prompt is not None:
            prose_prompt = self.current_prose_prompt
        else:
            prose_prompt = ("You are collaborating with the author to write a scene. "
                            "Write the scene in {pov} point of view, from the perspective of {pov_character}, and in {tense}.")
        print("DEBUG: Using prose prompt:", repr(self.current_prose_prompt))
        
        pov = self.current_pov or "Third Person"
        pov_character = self.current_pov_character or "Character"
        tense = self.current_tense or "Present Tense"
        
        overrides = {}
        if self.current_prose_config:
            overrides = {
                "provider": self.current_prose_config.get("provider", "Local"),
                "model": self.current_prose_config.get("model", "Local Model"),
                "max_tokens": self.current_prose_config.get("max_tokens", 200),
                "temperature": self.current_prose_config.get("temperature", 0.7)
            }
            print("DEBUG: Using overrides:", overrides)
        
        current_scene_text = None
        current_item = self.tree.currentItem()
        if current_item:
            level = 0
            temp = current_item
            while temp.parent():
                level += 1
                temp = temp.parent()
            if level >= 2:
                current_scene_text = self.editor.toPlainText().strip()
        
        extra_context = self.context_panel.get_selected_context_text()
        
        import prompt_handler
        final_prompt = prompt_handler.assemble_final_prompt(
            action_beats, prose_prompt, pov, pov_character, tense,
            current_scene_text, extra_context
        )
        
        self.send_button.setEnabled(False)
        self.preview_text.setPlainText("Generating preview...")
        QApplication.processEvents()
        
        generated_text = prompt_handler.send_final_prompt(final_prompt, overrides=overrides)
        
        self.preview_text.setPlainText(generated_text)
        self.send_button.setEnabled(True)
    
    def apply_preview(self):
        preview = self.preview_text.toPlainText().strip()
        if not preview:
            QMessageBox.warning(self, "Apply Preview", "No preview text to apply.")
            return
        current_text = self.editor.toPlainText()
        self.editor.setPlainText(current_text + "\n" + preview)
        self.preview_text.clear()
        self.prompt_input.clear()
    
    def retry_prompt(self):
        self.preview_text.clear()
        self.send_prompt()
    
    def create_summary(self):
        create_summary_feature(self)
    
    def save_summary(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Summary", "No Act or Chapter selected.")
            return
        summary_text = self.editor.toPlainText()
        
        item_data = current_item.data(0, Qt.UserRole)
        if not isinstance(item_data, dict):
            item_data = {"name": current_item.text(0)}
        item_data["summary"] = summary_text
        current_item.setData(0, Qt.UserRole, item_data)
        self.update_structure_from_tree()
        
        QMessageBox.information(self, "Summary", "Summary saved successfully.")
    
    def toggle_bold(self):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        current_weight = self.editor.fontWeight()
        fmt.setFontWeight(QFont.Normal if current_weight == QFont.Bold else QFont.Bold)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def toggle_italic(self):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def toggle_underline(self):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def toggle_tts(self):
        global tts_engine  # Not used directly anymore; managed via tts_manager.
        if self.tts_playing:
            tts_manager.stop()
            self.tts_playing = False
            self.tts_button.setText("TTS")
        else:
            text = self.editor.textCursor().selectedText()
            if not text.strip():
                text = self.editor.toPlainText()
            if not text.strip():
                QMessageBox.warning(self, "TTS Warning", "There is no text to read.")
                return
            self.tts_playing = True
            self.tts_button.setText("Stop TTS")
            def run_speech():
                try:
                    tts_manager.speak(text)
                except Exception as e:
                    print("Error during TTS:", e)
                finally:
                    self.tts_playing = False
                    QTimer.singleShot(0, lambda: self.tts_button.setText("TTS"))
            threading.Thread(target=run_speech).start()
    
    def perform_tts(self):
        self.toggle_tts()
    
    def start_autosave_timer(self):
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(300000)  # 5 minutes
        self.autosave_timer.timeout.connect(self.autosave_scene)
        self.autosave_timer.start()
    
    def autosave_scene(self):
        current_item = self.tree.currentItem()
        if not current_item:
            return
        level = 0
        temp = current_item
        while temp.parent():
            level += 1
            temp = temp.parent()
        if level < 2:
            return
        content = self.editor.toPlainText()
        if not content.strip():
            return
            
        def sanitize(text):
            return re.sub(r'\W+', '', text)
            
        hierarchy = []
        item = current_item
        while item:
            hierarchy.insert(0, item.text(0).strip())
            item = item.parent()
            
        sanitized_hierarchy = [sanitize(x) for x in hierarchy]
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + f"_{timestamp}.txt"
        project_folder = os.path.join(os.getcwd(), "Projects", sanitize(self.project_name))
        
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
            
        filepath = os.path.join(project_folder, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print("Autosaved scene to", filepath)
            self.statusBar().showMessage("Scene autosaved", 3000)
            
            scene_data = current_item.data(0, Qt.UserRole)
            if not isinstance(scene_data, dict):
                scene_data = {"name": current_item.text(0)}
            scene_data["content"] = content
            current_item.setData(0, Qt.UserRole, scene_data)
            self.update_structure_from_tree()
            
            pattern = os.path.join(project_folder, f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + "_*.txt")
            autosave_files = sorted(glob.glob(pattern))
            while len(autosave_files) > 6:
                oldest = autosave_files.pop(0)
                try:
                    os.remove(oldest)
                    print("Removed old autosave file:", oldest)
                except Exception as e:
                    print("Error removing old autosave file:", e)
        except Exception as e:
            print("Error during autosave:", e)


# For testing standalone.
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ProjectWindow("My Awesome Project")
    window.show()
    sys.exit(app.exec_())
