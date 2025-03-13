import sys
import json
import os, urllib
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QVBoxLayout,
                             QCheckBox, QComboBox, QLabel, QLineEdit,
                             QPushButton, QFormLayout, QColorDialog,
                             QSizePolicy, QHBoxLayout, QSpinBox, QDialog,
                             QMessageBox, QListWidget, QListWidgetItem,
                             QScrollArea, QFrame, QRadioButton, QGroupBox,
                             QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPalette, QColor, QIntValidator, QFont
from PyQt5.QtCore import Qt

from theme_manager import ThemeManager
from llm_api_aggregator import WWApiAggregator
from settings_manager import WWSettingsManager

# Placeholder for language-dependent labels.  Replace with actual loading
# from a file.
UI_LABELS = {
    "en": {
        "general_tab": "General",
        "fast_tts": "Fast Text to Speech",
        "enable_autosave": "Enable Auto-Save",
        "language": "Language",
        "appearance_tab": "Appearance",
        "theme": "Theme",
        "background_color": "Background Color",
        "text_size": "Text Size",
        "provider_tab": "Providers",
        "provider": "Provider",
        "endpoint_url": "Endpoint URL",
        "model": "Model",
        "api_key": "API Key",
        "timeout": "Timeout (seconds)",
        "test": "Test",
        "save": "Save",
        "close": "Close",
        "discard": "Discard",
        "cancel": "Cancel",
        "delete": "Delete",
        "choose": "Choose a provider...",
        "name": "Name",
        "default_provider": "Default Provider",
        "reveal": "Reveal",
        "hide": "Hide",
        "api_key_required": "API Key Required",
        "test_successful": "Connection successful!",
        "test_failed": "Connection failed: {}",
        "delete_confirmation": "Are you sure you want to delete the selected provider?",
        "delete_title": "Confirm Deletion",
        "new_provider": "New Provider",
        "edit_provider": "Edit Provider",
        "providers_list": "Configured Providers",
        "leave_empty": "Leave empty for default",
        "refresh_models": "Refresh Model List",
        "edit": "Edit",
        "provider_details": "Provider Details",
        "add": "Add",
        "update": "Update",
        "save_successful": "Settings saved successfully.",
        "unsaved_warning": "You have unsaved changes. Do you want to save them before closing?"
    },
    # Add other languages as needed
}

# Placeholder for available languages
LANGUAGES = ["en", "de", "es", "fr", "pt", "ja", "zh", "ko"]

class ProviderDialog(QDialog):
    def __init__(self, parent=None, provider_name=None, provider_data=None, providers=None, labels=None, is_default=False):
        super().__init__(parent)
        self.provider_name = provider_name
        self.provider_data = provider_data
        self.providers = providers or []
        self.labels = labels
        self.is_default = is_default
        self.is_edit_mode = provider_name is not None
        
        if self.is_edit_mode:
            self.setWindowTitle(self.labels["edit_provider"])
        else:
            self.setWindowTitle(self.labels["new_provider"])
            
        self.resize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Provider Details Group
        group_box = QGroupBox(self.labels["provider_details"])
        form_layout = QFormLayout()
        

        # Provider Type
        self.provider_label = QLabel(self.labels["provider"])
        self.provider_combobox = QComboBox()
        self.provider_combobox.addItems(self.providers)
        self.provider_combobox.currentIndexChanged.connect(self.provider_selected)
        form_layout.addRow(self.provider_label, self.provider_combobox)

        # Provider Name
        self.name_label = QLabel(self.labels["name"])
        self.name_input = QLineEdit()
        self.name_input.setMinimumWidth(230)
        form_layout.addRow(self.name_label, self.name_input)
                
        # Endpoint URL
        self.endpoint_url_label = QLabel(self.labels["endpoint_url"])
        self.endpoint_url_input = QLineEdit()
        self.endpoint_url_input.setToolTip(self.labels["leave_empty"])
        self.endpoint_url_input.setMinimumWidth(300)
        form_layout.addRow(self.endpoint_url_label, self.endpoint_url_input)
        
        # Model
        self.model_label = QLabel(self.labels["model"])
        self.refresh_button = QPushButton("↻")  # Refresh symbol
        self.refresh_button.setToolTip(self.labels["refresh_models"])
        self.refresh_button.setMaximumWidth(30)
        self.refresh_button.clicked.connect(self.refresh_models)
        self.model_combobox = QComboBox()
        self.model_combobox.setMinimumWidth(250)
        self.model_combobox.setEditable(True)

        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_combobox)
        model_layout.addWidget(self.refresh_button)
        form_layout.addRow(self.model_label, model_layout)
        
        # API Key
        self.api_key_label = QLabel(self.labels["api_key"])
        self.api_key_input = QLineEdit()
        self.api_key_input.setMinimumWidth(200)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.reveal_button = QPushButton(self.labels["reveal"])
        self.reveal_button.setCheckable(True)
        self.reveal_button.toggled.connect(self.toggle_reveal_api_key)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.reveal_button)
        form_layout.addRow(self.api_key_label, api_key_layout)
        
        # Timeout
        self.timeout_label = QLabel(self.labels["timeout"])
        self.timeout_input = QLineEdit()
        self.timeout_input.setValidator(QIntValidator(30, 600))
        self.timeout_input.setMaximumWidth(40)
        form_layout.addRow(self.timeout_label, self.timeout_input)
        
        # Default Provider Checkbox
        self.default_checkbox = QCheckBox(self.labels["default_provider"])
        self.default_checkbox.setChecked(self.is_default)
        form_layout.addRow("", self.default_checkbox)
        
        # Test Connection Button
        self.test_button = QPushButton(self.labels["test"])
        self.test_button.clicked.connect(self.test_provider_connection)
        form_layout.addRow("", self.test_button)
        
        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        
        # Dialog Buttons
        self.button_box = QDialogButtonBox()
        if self.is_edit_mode:
            self.button_box.addButton(self.labels["update"], QDialogButtonBox.AcceptRole)
        else:
            self.button_box.addButton(self.labels["add"], QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.labels["close"], QDialogButtonBox.RejectRole)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.timeout_input.setText(str(30))  # Default timeout value


        # Load data if editing
        if self.is_edit_mode and self.provider_data:
            self.name_input.setText(self.provider_name)
            self.name_input.setEnabled(False)  # Don't allow name change in edit mode
            
            provider_type = self.provider_data.get("provider", "")
            index = self.provider_combobox.findText(provider_type)
            if index >= 0:
                self.provider_combobox.setCurrentIndex(index)
            
            self.endpoint_url_input.setText(self.provider_data.get("endpoint", "Default"))
            self.api_key_input.setText(self.provider_data.get("api_key", ""))
            self.timeout_input.setText(str(self.provider_data.get("timeout", 30)))

            
            # Populate and select model
            self.populate_model_combobox(provider_type)
            model = self.provider_data.get("model", "")
            index = self.model_combobox.findText(model)
            if index >= 0:
                self.model_combobox.setCurrentIndex(index)
            else:
                self.model_combobox.setEditText(model)
    
    def provider_selected(self, index):
        provider_name = self.provider_combobox.itemText(index)

        self.populate_model_combobox(provider_name)
        
        # If custom, enable the name field unless in edit mode
        if provider_name == "Custom" and not self.is_edit_mode:
            self.name_input.setEnabled(True)
        elif not self.is_edit_mode:
            self.name_input.setText(provider_name)
            self.name_input.setEnabled(False)
    
    def refresh_models(self):
        provider_name = self.provider_combobox.currentText()
        self.populate_model_combobox(provider_name, True)

    def populate_model_combobox(self, provider_name, refresh = False):
        """Populate model dropdown based on provider type"""
        try:
            models = self.get_models_for_provider(provider_name, refresh)
        except Exception as e:
            error_message = urllib.parse.unquote(str(e))
            QMessageBox.warning(self, "Error", f"Error fetching models: {error_message}")
            models = ["Error"]
        self.model_combobox.clear()
        self.model_combobox.addItems(models)
    
    def get_models_for_provider(self, provider_name, refresh = False):
        provider = WWApiAggregator.aggregator.create_provider(provider_name, {
            "api_key": self.api_key_input.text(),
            "endpoint": self.endpoint_url_input.text()
        })
        if provider is None:
            return ["Provider not found"]
        if provider.model_requires_api_key and not self.api_key_input.text():
            return [self.labels["api_key_required"]]
        return provider.get_available_models(refresh)
    
    def toggle_reveal_api_key(self, checked):
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.reveal_button.setText(self.labels["hide"])
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.reveal_button.setText(self.labels["reveal"])
    
    def test_provider_connection(self):
        """Test the provider connection"""
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 30

        provider_name = self.provider_combobox.currentText()
        endpoint = self.endpoint_url_input.text()
        api_key = self.api_key_input.text()
        overrides = {
            "provider": provider_name,
        }
        if endpoint not in ("", "Default"):
            overrides["endpoint"] = endpoint
        if api_key != '':
            overrides["api_key"] = api_key
                
        try:
            provider = WWApiAggregator.aggregator.create_provider(provider_name)
            if provider.test_connection(overrides):
                QMessageBox.information(self, "Test Result", self.labels["test_successful"])
            else:
                QMessageBox.warning(self, "Test Result", "Connection failed.")
        except Exception as e:
            QMessageBox.warning(self, "Test Result", self.labels["test_failed"].format(e))
    
    def get_provider_data(self):
        """Return the provider data entered by the user"""
        if self.provider_combobox.currentText() == "Custom":
            provider_name = self.name_input.text().strip()
        else:
            provider_name = self.name_input.text().strip() or self.provider_combobox.currentText()
        
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 30
        
        return {
            "name": provider_name,
            "provider": self.provider_combobox.currentText(),
            "endpoint": self.endpoint_url_input.text(),
            "model": self.model_combobox.currentText(),
            "api_key": self.api_key_input.text(),
            "timeout": timeout,
            "is_default": self.default_checkbox.isChecked()
        }

    def update_labels(self, labels):
        """Update all UI labels based on the selected language."""
        self.labels = labels
        self.setWindowTitle(self.labels["edit_provider"] if self.is_edit_mode else self.labels["new_provider"])
        self.provider_label.setText(self.labels["provider"])
        self.name_label.setText(self.labels["name"])
        self.endpoint_url_label.setText(self.labels["endpoint_url"])
        self.model_label.setText(self.labels["model"])
        self.refresh_button.setToolTip(self.labels["refresh_models"])
        self.api_key_label.setText(self.labels["api_key"])
        self.reveal_button.setText(self.labels["reveal"] if self.api_key_input.echoMode() == QLineEdit.Password else self.labels["hide"])
        self.timeout_label.setText(self.labels["timeout"])
        self.default_checkbox.setText(self.labels["default_provider"])
        self.test_button.setText(self.labels["test"])
        self.button_box.clear()
        if self.is_edit_mode:
            self.button_box.addButton(self.labels["update"], QDialogButtonBox.AcceptRole)
        else:
            self.button_box.addButton(self.labels["add"], QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.labels["close"], QDialogButtonBox.RejectRole)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(500, 500)
        self.setWindowIcon(QIcon("icon.png"))  # Replace with your icon file

        self.general_settings = WWSettingsManager.get_general_settings()
        self.appearance_settings = WWSettingsManager.get_appearance_settings()
        self.llm_configs = WWSettingsManager.get_llm_configs()
        self.default_provider = WWSettingsManager.get_active_llm_name()

        self.ui_labels = UI_LABELS
        try:
            if os.path.exists("lang_settings.json"):
                with open("lang_settings.json", "r", encoding="utf-8") as f:
                    self.ui_labels = json.load(f)
        except UnicodeDecodeError as e:
            self.logger.error(f"Warn: Error reading unicode in language settings file: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Warn: Error parsing language settings file: {e}")
        except Exception as e:
            self.logger.error(f"Warn: Unexpected error: {e}")

        self.labels = self.ui_labels.get(self.general_settings["language"], self.ui_labels["en"])

        self.init_ui()
        self.load_values_from_settings()

        self.unsaved_changes = False  # Track unsaved changes

    def init_ui(self):
        self.tabs = QTabWidget()

        self.general_tab = QWidget()
        self.appearance_tab = QWidget()
        self.provider_tab = QWidget()

        self.tabs.addTab(self.general_tab, self.labels["general_tab"])
        self.tabs.addTab(self.appearance_tab, self.labels["appearance_tab"])
        self.tabs.addTab(self.provider_tab, self.labels["provider_tab"])

        self.init_general_tab()
        self.init_appearance_tab()
        self.init_provider_tab()

        self.button_box = QHBoxLayout()
        self.save_button = QPushButton(self.labels["save"])
        self.save_button.clicked.connect(self.save_settings_to_file)
        self.cancel_button = QPushButton(self.labels["close"])
        self.cancel_button.clicked.connect(self.check_unsaved_changes)
        self.button_box.addWidget(self.save_button)
        self.button_box.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(self.button_box)

        self.setLayout(main_layout)

    def init_general_tab(self):
        layout = QFormLayout()

        self.fast_tts_checkbox = QCheckBox(self.labels["fast_tts"])
        self.fast_tts_checkbox.stateChanged.connect(self.mark_unsaved_changes)
        layout.addRow(self.fast_tts_checkbox)

        self.enable_autosave_checkbox = QCheckBox(self.labels["enable_autosave"])
        self.enable_autosave_checkbox.stateChanged.connect(self.mark_unsaved_changes)
        layout.addRow(self.enable_autosave_checkbox)

        self.language_combobox = QComboBox()
        self.language_combobox.setMinimumWidth(80)
        self.language_combobox.addItems(LANGUAGES)
        self.language_combobox.currentIndexChanged.connect(self.language_changed)
        self.language_combobox.currentIndexChanged.connect(self.mark_unsaved_changes)
        self.language_label = QLabel(self.labels["language"])
        layout.addRow(self.language_label, self.language_combobox)

        self.general_tab.setLayout(layout)

    def init_appearance_tab(self):
        layout = QFormLayout()

        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(ThemeManager.list_themes())
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)
        self.theme_combobox.currentIndexChanged.connect(self.mark_unsaved_changes)
        self.theme_label = QLabel(self.labels["theme"])
        layout.addRow(self.theme_label, self.theme_combobox)

        self.background_color_button = QPushButton(self.labels["background_color"])
        self.background_color_button.clicked.connect(self.choose_background_color)
        self.background_color_label = QLabel()
        self.background_color_label.setAutoFillBackground(True)
        self.set_background_color_label(self.appearance_settings["background_color"])  # Initialize color label
        hbox = QHBoxLayout()
        hbox.addWidget(self.background_color_button)
        hbox.addWidget(self.background_color_label)
        layout.addRow(hbox)

        self.text_size_spinbox = QSpinBox()
        self.text_size_spinbox.setRange(8, 24)
        self.text_size_spinbox.valueChanged.connect(self.mark_unsaved_changes)
        self.text_size_label = QLabel(self.labels["text_size"])
        layout.addRow(self.text_size_label, self.text_size_spinbox)

        self.appearance_tab.setLayout(layout)

    def init_provider_tab(self):
        layout = QVBoxLayout()
        
        # Group box for provider list
        self.providers_group = QGroupBox(self.labels["providers_list"])
        providers_layout = QVBoxLayout()
        
        # List widget for providers
        self.providers_list = QListWidget()
        self.providers_list.setMinimumHeight(200)
        self.providers_list.itemClicked.connect(self.provider_item_clicked)
        providers_layout.addWidget(self.providers_list)
        
        # Buttons for provider management
        buttons_layout = QHBoxLayout()
        self.new_provider_button = QPushButton(self.labels["new_provider"])
        self.new_provider_button.clicked.connect(self.add_new_provider)
        self.edit_provider_button = QPushButton(self.labels["edit"])
        self.edit_provider_button.clicked.connect(self.edit_selected_provider)
        self.delete_provider_button = QPushButton(self.labels["delete"])
        self.delete_provider_button.clicked.connect(self.delete_provider)
        
        buttons_layout.addWidget(self.new_provider_button)
        buttons_layout.addWidget(self.edit_provider_button)
        buttons_layout.addWidget(self.delete_provider_button)
        providers_layout.addLayout(buttons_layout)
        
        self.providers_group.setLayout(providers_layout)
        layout.addWidget(self.providers_group)
        
        self.provider_tab.setLayout(layout)
        
        # Initially disable buttons that require selection
        self.edit_provider_button.setEnabled(False)
        self.delete_provider_button.setEnabled(False)

    def populate_providers_list(self):
        """Populate the providers list with configured providers"""
        self.providers_list.clear()
        
        for provider_name, provider_data in self.llm_configs.items():
            item = QListWidgetItem(provider_name)
            if provider_name == self.default_provider:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setData(Qt.UserRole, {"name": provider_name, "is_default": True})
                item.setText(f"{provider_name} ({self.labels['default_provider']})")
            else:
                item.setData(Qt.UserRole, {"name": provider_name, "is_default": False})
            
            self.providers_list.addItem(item)

    def provider_item_clicked(self, item):
        """Handle provider item selection"""
        self.edit_provider_button.setEnabled(True)
        
        # Only allow deletion of custom providers
        provider_data = item.data(Qt.UserRole)
        provider_name = provider_data["name"]
        is_default_provider = provider_data["is_default"]
        
        self.delete_provider_button.setEnabled(not is_default_provider)

    def add_new_provider(self):
        """Open dialog to add a new provider"""
        default_providers = WWApiAggregator.get_llm_providers()
        dialog = ProviderDialog(
            parent=self,
            providers=default_providers,
            labels=self.labels
        )
        
        if dialog.exec_():
            provider_data = dialog.get_provider_data()
            provider_name = provider_data["name"]
            
            if not provider_name:
                QMessageBox.warning(self, "Warning", "Provider name cannot be empty.")
                return
                
            if provider_name in self.llm_configs:
                QMessageBox.warning(self, "Warning", f"Provider '{provider_name}' already exists.")
                return
                
            # Add the new provider
            self.llm_configs[provider_name] = {
                "provider": provider_data["provider"],
                "endpoint": provider_data["endpoint"] == "Default" and provider_data["endpoint"] or "",
                "model": provider_data["model"],
                "api_key": provider_data["api_key"],
                "timeout": provider_data["timeout"]
            }
            
            # Set as default if specified
            if provider_data["is_default"]:
                self.default_provider = provider_name
                
            # Refresh the list
            self.populate_providers_list()
            self.mark_unsaved_changes()

    def edit_selected_provider(self):
        """Open dialog to edit the selected provider"""
        if not self.providers_list.currentItem():
            return
            
        provider_data = self.providers_list.currentItem().data(Qt.UserRole)
        provider_name = provider_data["name"]
        
        if provider_name not in self.llm_configs:
            return
            
        default_providers = WWApiAggregator.get_llm_providers()
        is_default = provider_name == self.default_provider
        
        dialog = ProviderDialog(
            parent=self,
            provider_name=provider_name,
            provider_data=self.llm_configs[provider_name],
            providers=default_providers,
            labels=self.labels,
            is_default=is_default
        )
        
        if dialog.exec_():
            updated_data = dialog.get_provider_data()
            
            # Update provider data
            self.llm_configs[provider_name] = {
                "provider": updated_data["provider"],
                "endpoint": updated_data["endpoint"],
                "model": updated_data["model"],
                "api_key": updated_data["api_key"],
                "timeout": updated_data["timeout"]
            }
            
            # Update default provider if needed
            if updated_data["is_default"]:
                self.default_provider = provider_name
            elif self.default_provider == provider_name and not updated_data["is_default"]:
                self.default_provider = ""
                
            # Refresh the list
            self.populate_providers_list()
            self.mark_unsaved_changes()

    def set_background_color_label(self, color_code):
        """Sets the background color label's color."""
        palette = self.background_color_label.palette()
        palette.setColor(QPalette.Window, QColor(color_code))
        self.background_color_label.setPalette(palette)
        self.background_color_label.setText(color_code)  # Display the color code.
        self.background_color_label.update()

    def delete_provider(self):
        """Deletes the currently selected provider."""
        if not self.providers_list.currentItem():
            return
            
        provider_data = self.providers_list.currentItem().data(Qt.UserRole)
        provider_name = provider_data["name"]
        
        # Check if provider is a default one
        if provider_data["is_default"]:
            QMessageBox.warning(self, "Warning", f"{provider_name} cannot be deleted as it is the default provider.")
            return
            
        reply = QMessageBox.question(
            self, 
            self.labels["delete_title"],
            self.labels["delete_confirmation"],
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from config
            if provider_name in self.llm_configs:
                del self.llm_configs[provider_name]
                
            # Remove as default if it was default
            if self.default_provider == provider_name:
                self.default_provider = ""
                
            # Update UI
            self.populate_providers_list()
            self.edit_provider_button.setEnabled(False)
            self.delete_provider_button.setEnabled(False)
            self.mark_unsaved_changes()

    def choose_background_color(self):
        color = QColorDialog.getColor(QColor(self.appearance_settings["background_color"]), self)
        if color.isValid():
            color_code = color.name()
            self.appearance_settings["background_color"] = color_code
            self.set_background_color_label(color_code)
            self.mark_unsaved_changes()

    def language_changed(self, index):
        language = LANGUAGES[index]
        self.general_settings["language"] = language
        self.labels = self.ui_labels.get(language, self.ui_labels[language])
        self.update_ui_labels()
        self.mark_unsaved_changes()

    def update_ui_labels(self):
        """Updates all UI labels based on the selected language."""
        self.tabs.setTabText(0, self.labels["general_tab"])
        self.tabs.setTabText(1, self.labels["appearance_tab"])
        self.tabs.setTabText(2, self.labels["provider_tab"])
        self.fast_tts_checkbox.setText(self.labels["fast_tts"])
        self.enable_autosave_checkbox.setText(self.labels["enable_autosave"])
        self.language_label.setText(self.labels["language"])
        self.theme_label.setText(self.labels["theme"])
        self.background_color_button.setText(self.labels["background_color"])
        self.text_size_label.setText(self.labels["text_size"])
        self.providers_group.setTitle(self.labels["providers_list"])
        
        self.save_button.setText(self.labels["save"])
        self.cancel_button.setText(self.labels["close"])
        self.new_provider_button.setText(self.labels["new_provider"])
        self.edit_provider_button.setText(self.labels["edit"])
        self.delete_provider_button.setText(self.labels["delete"])
        
        # Update provider dialog labels if it is open
        if hasattr(self, 'provider_dialog') and self.provider_dialog.isVisible():
            self.provider_dialog.update_labels(self.labels)
        
        # Re-populate provider list to update default provider label
        self.populate_providers_list()

    def load_values_from_settings(self):
        """Loads the settings values into the UI elements."""
        self.fast_tts_checkbox.setChecked(self.general_settings["fast_tts"])
        self.enable_autosave_checkbox.setChecked(self.general_settings["enable_autosave"])
        index = self.language_combobox.findText(self.general_settings["language"])
        if index >= 0:
            self.language_combobox.setCurrentIndex(index)

        index = self.theme_combobox.findText(self.appearance_settings["theme"])
        if index >= 0:
            self.theme_combobox.setCurrentIndex(index)
        self.text_size_spinbox.setValue(self.appearance_settings["text_size"])
        self.set_background_color_label(self.appearance_settings["background_color"])

        # Populate provider list
        self.populate_providers_list()

    def save_settings_to_file(self):
        """Saves the current UI settings to the JSON file."""
        self.general_settings["fast_tts"] = self.fast_tts_checkbox.isChecked()
        self.general_settings["enable_autosave"] = self.enable_autosave_checkbox.isChecked()
        self.general_settings["language"] = self.language_combobox.currentText()
        self.appearance_settings["theme"] = self.theme_combobox.currentText()
        self.appearance_settings["text_size"] = self.text_size_spinbox.value()

        WWSettingsManager.update_general_settings(self.general_settings)
        WWSettingsManager.update_appearance_settings(self.appearance_settings)
        WWSettingsManager.update_llm_configs(self.llm_configs, self.default_provider)
        QMessageBox.information(self, "Save Result", self.labels["save_successful"])
        self.unsaved_changes = False  # Reset unsaved changes flag

    def mark_unsaved_changes(self):
        """Mark that there are unsaved changes."""
        self.unsaved_changes = True

    def check_unsaved_changes(self):
        """Check for unsaved changes and show a warning dialog if there are any."""
        if self.unsaved_changes:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle(self.labels["unsaved_warning"])
            msg_box.setText(self.labels["unsaved_warning"])
            save_button = msg_box.addButton(self.labels["save"], QMessageBox.AcceptRole)
            discard_button = msg_box.addButton(self.labels["discard"], QMessageBox.DestructiveRole)
            cancel_button = msg_box.addButton(self.labels["cancel"], QMessageBox.RejectRole)
            msg_box.setDefaultButton(cancel_button)
            msg_box.exec_()

            if msg_box.clickedButton() == save_button:
                self.save_settings_to_file()
                self.close()
            elif msg_box.clickedButton() == discard_button:
                self.close()
            else:
                # Cancel, do nothing
                return
        else:
            self.close()

    def change_theme(self, index):
        """Change the theme based on the selected theme in the combobox."""
        theme_name = self.theme_combobox.itemText(index)
        ThemeManager.apply_to_app(theme_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings_dialog = SettingsDialog()
    settings_dialog.show()
    sys.exit(app.exec_())
