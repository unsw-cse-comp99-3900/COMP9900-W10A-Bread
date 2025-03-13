import os
import re
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
from PyQt5.QtCore import Qt

def sanitize(text):
    """Remove non-alphanumeric characters from text."""
    return re.sub(r'\W+', '', text)

def show_backup_dialog(parent, project_name, scene_identifier):
    """
    Opens a dialog that lists backup files from the project's backup directory.
    Supports both legacy .txt files and new HTML files.
    Returns the full path of the selected backup file, or None if canceled.
    """
    base_dir = os.getcwd()
    sanitized_project = sanitize(project_name)
    backup_dir = os.path.join(base_dir, "Projects", sanitized_project)
    
    sanitized_scene = sanitize(scene_identifier)
    
    backup_files = []
    if os.path.exists(backup_dir):
        # List only .txt and .html files that contain the sanitized scene identifier in the filename.
        for filename in os.listdir(backup_dir):
            if (filename.endswith(".txt") or filename.endswith(".html")) and sanitized_scene in filename:
                backup_files.append(filename)
    else:
        backup_files = []
    
    # Create the dialog.
    dialog = QDialog(parent)
    dialog.setWindowTitle("Backup Versions")
    dialog.setModal(True)
    dialog.resize(400, 300)
    
    dialog_layout = QVBoxLayout(dialog)
    list_widget = QListWidget(dialog)
    
    # Populate the list with backup files and format their timestamps.
    for f in sorted(backup_files):
        parts = f.rsplit("_", 1)
        if len(parts) == 2:
            timestamp_str = parts[1].split('.')[0]  # Remove file extension
            try:
                dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_timestamp = timestamp_str
            display_text = f"{f}   (Timestamp: {formatted_timestamp})"
        else:
            display_text = f
        list_widget.addItem(display_text)
        # Store the raw filename in the item's UserRole.
        list_item = list_widget.item(list_widget.count() - 1)
        list_item.setData(Qt.UserRole, f)
    
    dialog_layout.addWidget(list_widget)
    
    # Add OK and Cancel buttons.
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    dialog_layout.addWidget(button_box)
    
    # Function to handle OK: if an item is selected, store its filename.
    def on_accept():
        if list_widget.currentItem() is not None:
            dialog.selected_file = list_widget.currentItem().data(Qt.UserRole)
            dialog.accept()
        else:
            dialog.reject()
    
    button_box.accepted.connect(on_accept)
    button_box.rejected.connect(dialog.reject)
    
    result = dialog.exec_()
    if result == QDialog.Accepted and hasattr(dialog, "selected_file"):
        return os.path.join(backup_dir, dialog.selected_file)
    else:
        return None
