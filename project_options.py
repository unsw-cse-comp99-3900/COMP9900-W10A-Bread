import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout
)
from prompts import PromptsWindow  # Import the new prompts window

PROJECT_SETTINGS_FILE = "project_settings.json"  # This file stores project-specific settings

class ProjectOptionsWindow(QDialog):
    def __init__(self, project_name, parent=None):
        super().__init__(parent)
        self.project_name = project_name
        self.setWindowTitle(f"Project Options - {project_name}")
        self.resize(400, 300)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header label.
        title = QLabel("General Options")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Auto-Save option.
        self.autosave_checkbox = QCheckBox("Enable Auto-Save")
        self.autosave_checkbox.setToolTip("Toggles whether your project should be automatically saved every 5 minutes")
        layout.addWidget(self.autosave_checkbox)
        
        # (Deprecated) Model settings have been removed.
        
        # Prompts button.
        self.prompts_button = QPushButton("Prompts")
        self.prompts_button.setToolTip("Open the prompts editor window")
        self.prompts_button.clicked.connect(self.open_prompts)
        layout.addWidget(self.prompts_button)
        
        # Buttons at the bottom.
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def open_prompts(self):
        """Opens the Prompts window."""
        prompts_window = PromptsWindow(self.project_name, self)
        prompts_window.exec_()

    def load_settings(self):
        """
        Load project-specific settings from a JSON file.
        Currently, only the auto-save setting is loaded.
        """
        if os.path.exists(PROJECT_SETTINGS_FILE):
            try:
                with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    all_settings = json.load(f)
                project_settings = all_settings.get(self.project_name, {})
                self.autosave_checkbox.setChecked(project_settings.get("autosave", False))
            except Exception as e:
                print("Error loading project settings:", e)

    def save_settings(self):
        """
        Save project-specific settings to a JSON file.
        Only the auto-save setting is saved.
        """
        project_settings = {
            "autosave": self.autosave_checkbox.isChecked()
        }
        all_settings = {}
        if os.path.exists(PROJECT_SETTINGS_FILE):
            try:
                with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    all_settings = json.load(f)
            except Exception as e:
                print("Error reading project settings:", e)
        all_settings[self.project_name] = project_settings
        try:
            with open(PROJECT_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(all_settings, f, indent=4)
            self.accept()
        except Exception as e:
            print("Error saving project settings:", e)
