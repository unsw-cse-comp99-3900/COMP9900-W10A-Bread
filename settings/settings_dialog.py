import sys
import json
import copy
import os
from PyQt5.QtWidgets import (QApplication, QDialog, QTabWidget, QVBoxLayout,
                             QCheckBox, QComboBox, QLabel, QPushButton,
                             QFormLayout, QColorDialog, QHBoxLayout, QSpinBox,
                             QMessageBox, QListWidget, QListWidgetItem,
                             QGroupBox, QWidget)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QSettings

from .ui_constants import UI_LABELS, LANGUAGES
from .theme_manager import ThemeManager
from .llm_api_aggregator import WWApiAggregator
from .settings_manager import WWSettingsManager
from .provider_dialog import ProviderDialog

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(500, 500)
        self.setWindowIcon(QIcon("icon.png"))

        self.general_settings = WWSettingsManager.get_general_settings()
        self.appearance_settings = WWSettingsManager.get_appearance_settings()
        self.llm_configs = WWSettingsManager.get_llm_configs()
        self.default_provider = WWSettingsManager.get_active_llm_name()
        
        self.original_llm_configs = copy.deepcopy(self.llm_configs)

        self.ui_labels = UI_LABELS
        try:
            filepath = os.path.join(os.getcwd(), "assets", "lang_settings.json")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
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
        self.read_settings()

        self.unsaved_changes = False

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
        
        self.show_quote_checkbox = QCheckBox(self.labels["show_random_quote"])
        self.show_quote_checkbox.stateChanged.connect(self.mark_unsaved_changes)
        layout.addRow(self.show_quote_checkbox)

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
        self.set_background_color_label(self.appearance_settings["background_color"])
        hbox = QHBoxLayout()
        hbox.addWidget(self.background_color_button)
        hbox.addWidget(self.background_color_label)
        layout.addRow(hbox)

        self.text_size_spinbox = QSpinBox()
        self.text_size_spinbox.setRange(8, 24)
        self.text_size_spinbox.valueChanged.connect(self.update_font_size)
        self.text_size_spinbox.valueChanged.connect(self.mark_unsaved_changes)
        self.text_size_label = QLabel(self.labels["text_size"])
        layout.addRow(self.text_size_label, self.text_size_spinbox)

        self.sample_group_box = QGroupBox()
        sample_layout = QHBoxLayout()
        sample_layout.setAlignment(Qt.AlignCenter)
        self.sample_text_label = QLabel(self.labels["sample"])
        sample_layout.addWidget(self.sample_text_label)
        self.sample_group_box.setLayout(sample_layout)
        layout.addRow(self.sample_group_box)

        self.appearance_tab.setLayout(layout)

    def init_provider_tab(self):
        layout = QVBoxLayout()
        
        self.providers_group = QGroupBox(self.labels["providers_list"])
        providers_layout = QVBoxLayout()
        
        self.providers_list = QListWidget()
        self.providers_list.setMinimumHeight(200)
        self.providers_list.itemClicked.connect(self.provider_item_clicked)
        providers_layout.addWidget(self.providers_list)
        
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
        
        provider_data = item.data(Qt.UserRole)
        provider_name = provider_data["name"]
        is_default_provider = provider_data["is_default"]
        
        self.delete_provider_button.setEnabled(not is_default_provider)

    def add_new_provider(self):
        """Open dialog to add a new provider"""
        default_providers = WWApiAggregator.get_llm_providers()
        self.provider_dialog = ProviderDialog(
            parent=self,
            providers=default_providers,
            labels=self.labels
        )
        
        if self.provider_dialog.exec_():
            provider_data = self.provider_dialog.get_provider_data()
            provider_name = provider_data["name"]
            
            if not provider_name:
                QMessageBox.warning(self, "Warning", "Provider name cannot be empty.")
                return
                
            if provider_name in self.llm_configs:
                QMessageBox.warning(self, "Warning", f"Provider '{provider_name}' already exists.")
                return
                
            self.llm_configs[provider_name] = {
                "provider": provider_data["provider"],
                "endpoint": provider_data["endpoint"] == "Default" and provider_data["endpoint"] or "",
                "model": provider_data["model"],
                "api_key": provider_data["api_key"],
                "timeout": provider_data["timeout"]
            }
            
            if provider_data["is_default"]:
                self.default_provider = provider_name
                
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
        
        self.provider_dialog = ProviderDialog(
            parent=self,
            provider_name=provider_name,
            provider_data=self.llm_configs[provider_name],
            providers=default_providers,
            labels=self.labels,
            is_default=is_default
        )
        
        if self.provider_dialog.exec_():
            updated_data = self.provider_dialog.get_provider_data()
            
            self.llm_configs[provider_name] = {
                "provider": updated_data["provider"],
                "endpoint": updated_data["endpoint"],
                "model": updated_data["model"],
                "api_key": updated_data["api_key"],
                "timeout": updated_data["timeout"]
            }
            
            if updated_data["is_default"]:
                self.default_provider = provider_name
            elif self.default_provider == provider_name and not updated_data["is_default"]:
                self.default_provider = ""
                
            self.populate_providers_list()
            self.mark_unsaved_changes()

    def set_background_color_label(self, color_code):
        """Sets the background color label's color."""
        palette = self.background_color_label.palette()
        palette.setColor(QPalette.Window, QColor(color_code))
        self.background_color_label.setPalette(palette)
        self.background_color_label.setText(color_code)
        self.background_color_label.update()

    def delete_provider(self):
        """Deletes the currently selected provider."""
        if not self.providers_list.currentItem():
            return
            
        provider_data = self.providers_list.currentItem().data(Qt.UserRole)
        provider_name = provider_data["name"]
        
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
            if provider_name in self.llm_configs:
                del self.llm_configs[provider_name]
                
            if self.default_provider == provider_name:
                self.default_provider = ""
                
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
        self.labels = self.ui_labels.get(language, self.ui_labels["en"])
        self.update_ui_labels()
        self.mark_unsaved_changes()

    def update_ui_labels(self):
        """Updates all UI labels based on the selected language."""
        self.tabs.setTabText(0, self.labels["general_tab"])
        self.tabs.setTabText(1, self.labels["appearance_tab"])
        self.tabs.setTabText(2, self.labels["provider_tab"])
        self.fast_tts_checkbox.setText(self.labels["fast_tts"])
        self.enable_autosave_checkbox.setText(self.labels["enable_autosave"])
        self.show_quote_checkbox.setText(self.labels["show_random_quote"])
        self.language_label.setText(self.labels["language"])
        self.theme_label.setText(self.labels["theme"])
        self.background_color_button.setText(self.labels["background_color"])
        self.text_size_label.setText(self.labels["text_size"])
        self.providers_group.setTitle(self.labels["providers_list"])
        self.sample_text_label.setText(self.labels["sample"])
        
        self.save_button.setText(self.labels["save"])
        self.cancel_button.setText(self.labels["close"])
        self.new_provider_button.setText(self.labels["new_provider"])
        self.edit_provider_button.setText(self.labels["edit"])
        self.delete_provider_button.setText(self.labels["delete"])
        
        if hasattr(self, 'provider_dialog') and self.provider_dialog.isVisible():
            self.provider_dialog.update_labels(self.labels)
        
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

        self.populate_providers_list()
        
        self.show_quote_checkbox.setChecked(self.general_settings.get("show_random_quote", False))

    def save_settings_to_file(self):
        """Saves the current UI settings to the JSON file."""
        self.general_settings["fast_tts"] = self.fast_tts_checkbox.isChecked()
        self.general_settings["enable_autosave"] = self.enable_autosave_checkbox.isChecked()
        self.general_settings["show_random_quote"] = self.show_quote_checkbox.isChecked()
        self.general_settings["language"] = self.language_combobox.currentText()
        self.appearance_settings["theme"] = self.theme_combobox.currentText()
        self.appearance_settings["text_size"] = self.text_size_spinbox.value()

        deleted_configs = set(self.original_llm_configs.keys()) - set(self.llm_configs.keys())
        for provider_name in deleted_configs:
            success = WWSettingsManager.delete_llm_config(provider_name)
            if not success:
                QMessageBox.warning(self, "Warning", f"Failed to delete config {provider_name} from settings.json.")

        success = (
            WWSettingsManager.update_general_settings(self.general_settings) and
            WWSettingsManager.update_appearance_settings(self.appearance_settings) and
            WWSettingsManager.update_llm_configs(self.llm_configs, self.default_provider)
        )

        if success:
            self.original_llm_configs = copy.deepcopy(self.llm_configs)
            QMessageBox.information(self, "Save Result", self.labels["save_successful"])
            self.unsaved_changes = False
            self.settings_saved.emit()
        else:
            QMessageBox.warning(self, "Warning", "Failed to save settings.")

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
                return
        else:
            self.close()

    def change_theme(self, index):
        """Change the theme based on the selected theme in the combobox."""
        theme_name = self.theme_combobox.itemText(index)
        ThemeManager.apply_to_app(theme_name)

    def update_font_size(self, value):
        """Update the font size for all text UI objects except the TextEdit contents."""
        font = self.font()
        font.setPointSize(value)
        QApplication.instance().setFont(font)
        self.sample_text_label.setFont(font)

    def read_settings(self):
        """Restore window geometry and tab state."""
        settings = QSettings("MyCompany", "WritingwayProject")
        self.restoreGeometry(settings.value("SettingsDialog/geometry", self.saveGeometry()))
        self.tabs.setCurrentIndex(int(settings.value("SettingsDialog/tab_index", 0)))

    def write_settings(self):
        """Save window geometry and tab state."""
        settings = QSettings("MyCompany", "WritingwayProject")
        settings.setValue("SettingsDialog/geometry", self.saveGeometry())
        settings.setValue("SettingsDialog/tab_index", self.tabs.currentIndex())

    def closeEvent(self, event):
        """Save settings when closing the dialog."""
        self.write_settings()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings_dialog = SettingsDialog()
    settings_dialog.show()
    sys.exit(app.exec_())