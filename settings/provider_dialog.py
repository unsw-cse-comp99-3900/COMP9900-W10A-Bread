import urllib
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout,
                             QComboBox, QLabel, QLineEdit, QPushButton,
                             QHBoxLayout, QCheckBox, QDialogButtonBox,
                             QMessageBox, QInputDialog, QSizePolicy)
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import Qt

from .ui_constants import UI_LABELS, LANGUAGES
from .llm_api_aggregator import WWApiAggregator
from .provider_info_dialog import ProviderInfoDialog
from .settings_manager import WWSettingsManager

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
        
        group_box = QGroupBox(self.labels["provider_details"])
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.provider_label = QLabel(self.labels["provider"])
        self.provider_combobox = QComboBox()
        self.provider_combobox.addItems(self.providers)
        self.provider_combobox.currentIndexChanged.connect(self.provider_selected)
        self.provider_info_button = QPushButton()
        self.provider_info_button.setIcon(QIcon("assets/icons/info.svg"))
        self.provider_info_button.setToolTip(self.labels["provider_info"])
        self.provider_info_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.provider_info_button.clicked.connect(self.show_provider_info)
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(self.provider_combobox)
        provider_layout.addWidget(self.provider_info_button)
        form_layout.addRow(self.provider_label, provider_layout)

        self.name_label = QLabel(self.labels["name"])
        self.name_input = QLineEdit()
        self.name_input.setMinimumWidth(230)
        form_layout.addRow(self.name_label, self.name_input)
                
        self.endpoint_url_label = QLabel(self.labels["endpoint_url"])
        self.endpoint_url_input = QLineEdit()
        self.endpoint_url_input.setToolTip(self.labels["leave_empty"])
        self.endpoint_url_input.setMinimumWidth(300)
        self.endpoint_help_button = QPushButton()
        self.endpoint_help_button.setIcon(QIcon("assets/icons/help-circle.svg"))
        self.endpoint_help_button.setToolTip(self.labels["endpoint_help_tooltip"])
        self.endpoint_help_button.clicked.connect(lambda: QMessageBox.information(self, self.labels["endpoint_help_title"], self.labels["endpoint_help_message"]))
        endpoint_layout = QHBoxLayout()
        endpoint_layout.addWidget(self.endpoint_url_input)
        endpoint_layout.addWidget(self.endpoint_help_button)
        form_layout.addRow(self.endpoint_url_label, endpoint_layout)
        
        self.model_label = QLabel(self.labels["model"])
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("assets/icons/rotate-cw.svg"))
        self.refresh_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.refresh_button.setToolTip(self.labels["refresh_models"])
        self.refresh_button.clicked.connect(self.refresh_models)
        self.model_combobox = QComboBox()
        self.model_combobox.setMinimumWidth(250)
        self.model_combobox.setEditable(True)

        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_combobox)
        model_layout.addWidget(self.refresh_button)
        form_layout.addRow(self.model_label, model_layout)
        
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
        
        self.timeout_label = QLabel(self.labels["timeout"])
        self.timeout_input = QLineEdit()
        self.timeout_input.setValidator(QIntValidator(30, 600))
        self.timeout_input.setMaximumWidth(40)
        form_layout.addRow(self.timeout_label, self.timeout_input)
        
        self.default_checkbox = QCheckBox(self.labels["default_provider"])
        self.default_checkbox.setChecked(self.is_default)
        form_layout.addRow("", self.default_checkbox)
        
        self.test_button = QPushButton(self.labels["test"])
        self.test_button.clicked.connect(self.test_provider_connection)
        form_layout.addRow("", self.test_button)
        
        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        
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

        self.timeout_input.setText(str(30))

        if self.is_edit_mode and self.provider_data:
            self.name_input.setText(self.provider_name)
            self.name_input.setEnabled(False)
            
            provider_type = self.provider_data.get("provider", "")
            index = self.provider_combobox.findText(provider_type)
            if index >= 0:
                self.provider_combobox.setCurrentIndex(index)
            
            self.endpoint_url_input.setText(self.provider_data.get("endpoint", "Default"))
            self.api_key_input.setText(self.provider_data.get("api_key", ""))
            self.timeout_input.setText(str(self.provider_data.get("timeout", 30)))

            self.populate_model_combobox(provider_type)
            model = self.provider_data.get("model", "")
            index = self.model_combobox.findText(model)
            if index >= 0:
                self.model_combobox.setCurrentIndex(index)
            else:
                self.model_combobox.setEditText(model)
    
    def show_provider_info(self):
        dialog = ProviderInfoDialog(self, self.labels, self.parent().llm_configs)
        dialog.exec_()

    def provider_selected(self, index):
        provider_name = self.provider_combobox.itemText(index)
        self.populate_model_combobox(provider_name)
        
        if provider_name == "Custom" and not self.is_edit_mode:
            self.name_input.setEnabled(True)
        elif not self.is_edit_mode:
            self.name_input.setText(provider_name)
            self.name_input.setEnabled(False)
    
    def refresh_models(self):
        provider_name = self.provider_combobox.currentText()
        self.populate_model_combobox(provider_name, True)

    def populate_model_combobox(self, provider_name, refresh=False):
        try:
            models = self.get_models_for_provider(provider_name, refresh)
        except Exception as e:
            if refresh:
                error_message = urllib.parse.unquote(str(e))
                QMessageBox.warning(self, "Error", f"Error fetching models: {error_message}\nEnsure API key and endpoint are correct.")
            models = ["Error"]
        self.model_combobox.clear()
        self.model_combobox.addItems(models)
    
    def get_models_for_provider(self, provider_name, refresh=False):
        config = {
            "api_key": self.api_key_input.text(),
            "endpoint": self.endpoint_url_input.text()
        }
        # Check settings for an existing API key
        llm_configs = WWSettingsManager.get_llm_configs()
        for name, cfg in llm_configs.items():
            if cfg.get("provider") == provider_name:
                config["api_key"] = cfg.get("api_key", config["api_key"])
                break

        provider = WWApiAggregator.aggregator.create_provider(provider_name, config)
        if provider is None:
            QMessageBox.warning(self, "Error", f"Provider {provider_name} not found.")
            return ["Provider not found"]
        
        if provider.model_requires_api_key and not config["api_key"]:
            api_key, ok = QInputDialog.getText(
                self,
                "API Key Required",
                f"An API key is required for {provider_name}. Please enter it:",
                echo=QLineEdit.Password
            )
            if ok and api_key:
                config["api_key"] = api_key
                # Save to settings
                provider_config = {
                    "provider": provider_name,
                    "endpoint": config.get("endpoint", provider.get_default_endpoint()),
                    "model": "",
                    "api_key": api_key,
                    "timeout": config.get("timeout", 30)
                }
                WWSettingsManager.update_llm_config(f"{provider_name}_auto", provider_config)
                provider = WWApiAggregator.aggregator.create_provider(provider_name, config)
            else:
                return [self.labels["api_key_required"]]
        
        try:
            return provider.get_available_models(refresh)
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")

    def toggle_reveal_api_key(self, checked):
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.reveal_button.setText(self.labels["hide"])
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.reveal_button.setText(self.labels["reveal"])
    
    def test_provider_connection(self):
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 30

        provider_name = self.provider_combobox.currentText()
        endpoint = self.endpoint_url_input.text()
        model = self.model_combobox.currentText()
        api_key = self.api_key_input.text()
        config = {
            "provider": provider_name,
            "model": model,
            "timeout": timeout,
            "api_key": api_key
        }
        if endpoint not in ("", "Default"):
            config["endpoint"] = endpoint
        
        # Check settings for an existing API key
        llm_configs = WWSettingsManager.get_llm_configs()
        for name, cfg in llm_configs.items():
            if cfg.get("provider") == provider_name:
                config["api_key"] = cfg.get("api_key", config["api_key"])
                break

        provider = WWApiAggregator.aggregator.create_provider(provider_name, config)
        if provider is None:
            QMessageBox.warning(self, "Error", f"Provider {provider_name} not found.")
            return

        if provider.model_requires_api_key and not config["api_key"]:
            api_key, ok = QInputDialog.getText(
                self,
                "API Key Required",
                f"An API key is required for {provider_name}. Please enter it:",
                echo=QLineEdit.Password
            )
            if ok and api_key:
                config["api_key"] = api_key
                # Save to settings
                provider_config = {
                    "provider": provider_name,
                    "endpoint": config.get("endpoint", provider.get_default_endpoint()),
                    "model": model,
                    "api_key": api_key,
                    "timeout": timeout
                }
                WWSettingsManager.update_llm_config(f"{provider_name}_auto", provider_config)
                provider = WWApiAggregator.aggregator.create_provider(provider_name, config)
            else:
                QMessageBox.warning(self, "Error", f"API key is required for {provider_name}.")
                return
                
        try:
            if provider.test_connection(config):
                QMessageBox.information(self, "Test Result", self.labels["test_successful"])
            else:
                QMessageBox.warning(self, "Test Result", "Connection failed. Check provider settings.")
        except Exception as e:
            QMessageBox.warning(self, "Test Result", self.labels["test_failed"].format(str(e)))

    def get_provider_data(self):
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
        self.labels = labels
        self.setWindowTitle(self.labels["edit_provider"] if self.is_edit_mode else self.labels["new_provider"])
        self.provider_label.setText(self.labels["provider"])
        self.provider_info_button.setToolTip(self.labels["provider_info"])
        self.name_label.setText(self.labels["name"])
        self.endpoint_url_label.setText(self.labels["endpoint_url"])
        self.endpoint_help_button.setToolTip(self.labels["endpoint_help_tooltip"])
        self.endpoint_help_button.clicked.disconnect()
        self.endpoint_help_button.clicked.connect(lambda: QMessageBox.information(self, self.labels["endpoint_help_title"], self.labels["endpoint_help_message"]))
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