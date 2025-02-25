#!/usr/bin/env python3
import os
import time
import glob
import json
import re
import threading
import pyttsx3
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMenu, QMessageBox, QApplication, QDialog, QFontDialog, QShortcut, QLabel  # NEW: Added QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QIcon, QKeySequence
from compendium import CompendiumWindow
from workshop import WorkshopWindow
from llm_integration import send_prompt_to_llm, build_final_prompt
from rewrite_feature import RewriteDialog
from backup_manager import show_backup_dialog
from summary_feature import create_summary as create_summary_feature
from prompts import load_project_options
from tree_manager import load_structure, save_structure, populate_tree, update_structure_from_tree, delete_node
from context_panel import ContextPanel
import tts_manager
import autosave_manager
from dialogs import CreateSummaryDialog
from project_ui import build_main_ui
import project_settings_manager as settings_manager
from project_structure_manager import add_act, add_chapter, add_scene, rename_item, move_item_up, move_item_down


class ProjectWindow(QMainWindow):
    def __init__(self, project_name):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle(f"Project: {project_name}")
        self.resize(900, 600)
        self.current_pov = ""
        self.current_pov_character = "Character"
        self.current_tense = "Present Tense"
        self.current_prose_prompt = None
        self.current_prose_config = None
        self.tts_playing = False
        self.structure = load_structure(self.project_name)
        self.init_ui()

        # NEW: Add status bar labels for word count and last save time.
        self.word_count_label = QLabel("Words: 0")
        self.last_save_label = QLabel("Last Saved: Never")
        self.statusBar().addPermanentWidget(self.word_count_label)
        self.statusBar().addPermanentWidget(self.last_save_label)
        # Connect editor textChanged signal to update word count.
        self.editor.textChanged.connect(self.update_word_count)

        self.load_autosave_setting()
        if self.autosave_enabled:
            self.start_autosave_timer()
        if self.tree.topLevelItemCount() > 0:
            act_item = self.tree.topLevelItem(0)
            if act_item.childCount() > 0:
                chapter_item = act_item.child(0)
                if chapter_item.childCount() > 0:
                    self.tree.setCurrentItem(chapter_item.child(0))
        self.updateSettingTooltips()
        self.populate_prompt_dropdown()

        # NEW: Bind F11 key to open focus mode
        self.focus_mode_shortcut = QShortcut(QKeySequence("F11"), self)
        self.focus_mode_shortcut.activated.connect(self.open_focus_mode)

    def updateSettingTooltips(self):
        self.pov_combo.setToolTip(f"POV: {self.current_pov}")
        self.pov_character_combo.setToolTip(
            f"POV Character: {self.current_pov_character}")
        self.tense_combo.setToolTip(f"Tense: {self.current_tense}")

    def load_autosave_setting(self):
        settings = settings_manager.load_project_settings(self.project_name)
        self.autosave_enabled = settings.get("autosave", False)
        self.current_pov = settings.get("global_pov", self.current_pov)
        self.current_pov_character = settings.get(
            "global_pov_character", self.current_pov_character)
        self.current_tense = settings.get("global_tense", self.current_tense)

    def save_global_settings(self):
        project_settings = {
            "global_pov": self.current_pov,
            "global_pov_character": self.current_pov_character,
            "global_tense": self.current_tense
        }
        settings_manager.save_project_settings(
            self.project_name, project_settings)

    def populate_tree(self):
        populate_tree(self.tree, self.structure)

    def update_structure_from_tree(self):
        self.structure = update_structure_from_tree(
            self.tree, self.project_name)

    def get_summary_filename(self, item):
        def sanitize(text):
            return re.sub(r'\W+', '', text)
        hierarchy = []
        temp = item
        while temp:
            hierarchy.insert(0, temp.text(0).strip())
            temp = temp.parent()
        sanitized = [sanitize(x) for x in hierarchy]
        filename = f"{sanitize(self.project_name)}-Summary-" + \
            "-".join(sanitized) + ".txt"
        project_folder = os.path.join(
            os.getcwd(), "Projects", sanitize(self.project_name))
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        return os.path.join(project_folder, filename)

    def init_ui(self):
        build_main_ui(self)

    # NEW: Method to update the word count label
    def update_word_count(self):
        text = self.editor.toPlainText()
        words = text.split()
        count = len(words)
        self.word_count_label.setText(f"Words: {count}")

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
            QMessageBox.warning(
                self, "Rewrite", "No text selected to rewrite.")
            return
        selected_text = cursor.selectedText()
        dialog = RewriteDialog(self.project_name, selected_text, self)
        if dialog.exec_() == QDialog.Accepted:
            cursor.insertText(dialog.rewritten_text)
            self.editor.setTextCursor(cursor)

    def open_project_options(self):
        pass

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
            self.editor.setPlaceholderText(
                f"Enter summary for {current.text(0)}...")
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
        project_folder = os.path.join(
            os.getcwd(), "Projects", sanitize(self.project_name))
        pattern = os.path.join(
            project_folder, f"{sanitize(self.project_name)}-" + "-".join(sanitized_hierarchy) + "_*.txt")
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
                add_act(self)
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
            rename_item(self, item)
        elif action == delete_action:
            delete_node(self.tree, item, self.project_name)
        elif action == move_up_action:
            move_item_up(self, item)
        elif action == move_down_action:
            move_item_down(self, item)
        elif level == 0 and 'add_chapter_action' in locals() and action == add_chapter_action:
            add_chapter(self, item)
        elif level == 1 and 'add_scene_action' in locals() and action == add_scene_action:
            add_scene(self, item)

    def start_autosave_timer(self):
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(300000)
        self.autosave_timer.timeout.connect(self.autosave_scene)
        self.autosave_timer.start()

    def manual_save_scene(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Manual Save",
                                "No scene selected for saving.")
            return
        level = 0
        temp = current_item
        while temp.parent():
            level += 1
            temp = temp.parent()
        if level < 2:
            QMessageBox.warning(self, "Manual Save",
                                "Please select a scene for manual save.")
            return
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Manual Save",
                                "There is no content to save.")
            return
        hierarchy = []
        item = current_item
        while item:
            hierarchy.insert(0, item.text(0).strip())
            item = item.parent()
        filepath = autosave_manager.save_scene(
            self.project_name, hierarchy, content)
        if filepath:
            # NEW: Update last save time label
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            self.last_save_label.setText(f"Last Saved: {now}")
            self.statusBar().showMessage("Scene manually saved", 3000)
            scene_data = current_item.data(0, Qt.UserRole)
            if not isinstance(scene_data, dict):
                scene_data = {"name": current_item.text(0)}
            scene_data["content"] = content
            current_item.setData(0, Qt.UserRole, scene_data)
            self.update_structure_from_tree()
        else:
            self.statusBar().showMessage("No changes detected. Manual save skipped.", 3000)

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
        hierarchy = []
        item = current_item
        while item:
            hierarchy.insert(0, item.text(0).strip())
            item = item.parent()
        filepath = autosave_manager.save_scene(
            self.project_name, hierarchy, content)
        if filepath:
            # NEW: Update last save time label for autosave
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            self.last_save_label.setText(f"Last Saved: {now}")
            self.statusBar().showMessage("Scene autosaved", 3000)
            scene_data = current_item.data(0, Qt.UserRole)
            if not isinstance(scene_data, dict):
                scene_data = {"name": current_item.text(0)}
            scene_data["content"] = content
            current_item.setData(0, Qt.UserRole, scene_data)
            self.update_structure_from_tree()

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
            QMessageBox.warning(self, "Backup Versions",
                                "Please select a scene to view backups.")
            return
        scene_identifier = current_item.text(0)
        backup_file_path = show_backup_dialog(
            self, self.project_name, scene_identifier)
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
                QMessageBox.information(
                    self, "Backup Loaded", f"Backup loaded from:\n{backup_file_path}")
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Error loading backup file: {e}")
        else:
            QMessageBox.information(self, "Backup", "No backup file selected.")

    def handle_pov_change(self, index):
        value = self.pov_combo.currentText()
        if value == "Custom...":
            custom, ok = QInputDialog.getText(self, "Custom POV", "Enter custom POV:",
                                              text=self.current_pov if self.current_pov not in ["First Person", "Omniscient", "Third Person Limited"] else "")
            if ok and custom.strip():
                custom = custom.strip()
                if self.pov_combo.findText(custom) == -1:
                    self.pov_combo.insertItem(0, custom)
                self.current_pov = custom
                self.pov_combo.setCurrentText(custom)
            else:
                self.pov_combo.setCurrentText(self.current_pov)
                return
        else:
            self.current_pov = value
        self.pov_combo.setToolTip(f"POV: {self.current_pov}")
        self.save_global_settings()

    def handle_pov_character_change(self, index):
        value = self.pov_character_combo.currentText()
        if value == "Custom...":
            custom, ok = QInputDialog.getText(self, "Custom POV Character", "Enter custom POV Character:",
                                              text=self.current_pov_character if self.current_pov_character not in ["Alice", "Bob", "Charlie"] else "")
            if ok and custom.strip():
                custom = custom.strip()
                if self.pov_character_combo.findText(custom) == -1:
                    self.pov_character_combo.insertItem(0, custom)
                self.current_pov_character = custom
                self.pov_character_combo.setCurrentText(custom)
            else:
                self.pov_character_combo.setCurrentText(
                    self.current_pov_character)
                return
        else:
            self.current_pov_character = value
        self.pov_character_combo.setToolTip(
            f"POV Character: {self.current_pov_character}")
        self.save_global_settings()

    def handle_tense_change(self, index):
        value = self.tense_combo.currentText()
        if value == "Custom...":
            custom, ok = QInputDialog.getText(self, "Custom Tense", "Enter custom Tense:",
                                              text=self.current_tense if self.current_tense not in ["Past Tense", "Present Tense"] else "")
            if ok and custom.strip():
                custom = custom.strip()
                if self.tense_combo.findText(custom) == -1:
                    self.tense_combo.insertItem(0, custom)
                self.current_tense = custom
                self.tense_combo.setCurrentText(custom)
            else:
                self.tense_combo.setCurrentText(self.current_tense)
                return
        else:
            self.current_tense = value
        self.tense_combo.setToolTip(f"Tense: {self.current_tense}")
        self.save_global_settings()

    def populate_prompt_dropdown(self):
        prompts_file = f"prompts_{self.project_name.replace(' ', '')}.json"
        prose_prompts = []
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prose_prompts = data.get("Prose", [])
            except Exception as e:
                print("Error loading prose prompts:", e)
        if not prose_prompts:
            prose_prompts = [{
                "name": "Default Prose Prompt",
                "text": "You are collaborating with the author to write a scene. Write the scene in {pov} point of view, from the perspective of {pov_character}, and in {tense}.",
                "provider": "Local",
                "model": "Local Model",
                "max_tokens": 200,
                "temperature": 0.7
            }]
        self.prompt_dropdown.blockSignals(True)
        self.prompt_dropdown.clear()
        self.prompt_dropdown.addItem("Select Prose Prompt")
        for prompt in prose_prompts:
            name = prompt.get("name", "Unnamed")
            self.prompt_dropdown.addItem(name)
        self.prompt_dropdown.blockSignals(False)
        self._prose_prompts = prose_prompts

    def prompt_dropdown_changed(self, index):
        if index == 0:
            return
        selected_prompt = self._prose_prompts[index -
                                              1] if index - 1 < len(self._prose_prompts) else None
        if selected_prompt:
            self.current_prose_prompt = selected_prompt.get("text", "")
            self.current_prose_config = selected_prompt
            if hasattr(self, "model_indicator"):
                self.model_indicator.setText(
                    f"[Model: {selected_prompt.get('model', 'Unknown')}]")

    def send_prompt(self):
        action_beats = self.prompt_input.toPlainText().strip()
        if not action_beats:
            QMessageBox.warning(
                self, "LLM Prompt", "Please enter some action beats before sending.")
            return
        if self.current_prose_prompt is not None:
            prose_prompt = self.current_prose_prompt
        else:
            prose_prompt = ("You are collaborating with the author to write a scene. "
                            "Write the scene in {pov} point of view, from the perspective of {pov_character}, and in {tense}.")
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
        generated_text = prompt_handler.send_final_prompt(
            final_prompt, overrides=overrides)
        self.preview_text.setPlainText(generated_text)
        self.send_button.setEnabled(True)

    def apply_preview(self):
        preview = self.preview_text.toPlainText().strip()
        if not preview:
            QMessageBox.warning(self, "Apply Preview",
                                "No preview text to apply.")
            return
        current_text = self.editor.toPlainText()
        self.editor.setPlainText(current_text + "\n" + preview)
        self.preview_text.clear()
        self.prompt_input.clear()

    def retry_prompt(self):
        self.preview_text.clear()
        self.send_prompt()

    def create_summary(self):
        default_prompt = "Enter your summarizer prompt here..."
        dialog = CreateSummaryDialog(default_prompt, self)
        if dialog.exec_() == QDialog.Accepted:
            summary_prompt = dialog.prompt
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
        fmt.setFontWeight(QFont.Normal if current_weight ==
                          QFont.Bold else QFont.Bold)
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

    def align_left(self):
        self.editor.setAlignment(Qt.AlignLeft)

    def align_center(self):
        self.editor.setAlignment(Qt.AlignCenter)

    def align_right(self):
        self.editor.setAlignment(Qt.AlignRight)

    def choose_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self, "Choose Font")
        if ok:
            self.editor.setCurrentFont(font)

    def set_font_size(self, size):
        font = self.editor.currentFont()
        font.setPointSize(size)
        self.editor.setCurrentFont(font)

    def toggle_tts(self):
        if self.tts_playing:
            tts_manager.stop()
            self.tts_playing = False
            self.tts_button.setIcon(QIcon("assets/icons/play-circle.svg"))
        else:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                text = cursor.selectedText()
                start_position = 0
            else:
                text = self.editor.toPlainText()
                start_position = cursor.position()
            if not text.strip():
                QMessageBox.warning(self, "TTS Warning",
                                    "There is no text to read.")
                return
            self.tts_playing = True
            self.tts_button.setIcon(QIcon("assets/icons/stop-circle.svg"))

            def run_speech():
                try:
                    tts_manager.speak(
                        text,
                        start_position=start_position,
                        on_complete=lambda: QTimer.singleShot(
                            0, lambda: self.tts_button.setIcon(
                                QIcon("assets/icons/play-circle.svg"))
                        )
                    )
                except Exception as e:
                    print("Error during TTS:", e)
                finally:
                    self.tts_playing = False
            threading.Thread(target=run_speech).start()

    def perform_tts(self):
        self.toggle_tts()

    # NEW: Methods for Focus Mode integration
    def open_focus_mode(self):
        scene_text = self.editor.toPlainText()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_directory = os.path.join(base_dir, "assets", "backgrounds")
        from focus_mode import FocusMode
        self.focus_window = FocusMode(image_directory, scene_text, parent=None)
        self.focus_window.on_close = self.focus_mode_closed
        self.focus_window.show()

    def focus_mode_closed(self, updated_text):
        self.editor.setPlainText(updated_text)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ProjectWindow("My Awesome Project")
    window.show()
    sys.exit(app.exec_())
