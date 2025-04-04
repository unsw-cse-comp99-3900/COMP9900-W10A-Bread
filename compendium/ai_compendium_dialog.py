from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QTreeWidget, QTreeWidgetItem, 
                             QSplitter, QMenu, QWidget, QInputDialog, QSizePolicy, QShortcut)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QCursor, QKeySequence
import json
import os

class AICompendiumDialog(QDialog):
    def __init__(self, ai_compendium_data, compendium_file, parent=None):
        super().__init__(parent)
        self.ai_compendium_data = ai_compendium_data
        self.compendium_file = compendium_file  # Path to existing compendium file
        self.existing_compendium = self.load_existing_compendium()
        self.font_size = 12  # Default font size in points
        self.init_ui()
        self.read_settings()  # Load previous settings if available

    def load_existing_compendium(self):
        """Load the existing compendium data for comparison."""
        if os.path.exists(self.compendium_file):
            try:
                with open(self.compendium_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading existing compendium: {e}")
                return {"categories": []}
        return {"categories": []}

    def init_ui(self):
        self.setWindowTitle("AI Compendium Analysis")
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Create a splitter similar to CompendiumPanel
        self.splitter = QSplitter(Qt.Horizontal)

        # Left side: Tree for categories and entries
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("AI-Generated Compendium")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.tree.currentItemChanged.connect(self.on_item_changed)
        self.splitter.addWidget(self.tree)

        # Right side: Editor for the selected entry
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select an entry to view or edit its content.")
        self.splitter.addWidget(self.editor)

        # Set splitter proportions
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        layout.addWidget(self.splitter)

        # Buttons
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        self.save_button = QPushButton("Save to Compendium")
        self.save_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(self.save_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        button_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(button_widget)
        self.setLayout(layout)

        # Populate the tree with AI-generated data and compare with existing
        self.populate_tree()

        # Shortcuts for zoom
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)


    def populate_tree(self):
        """Populate the tree with AI-generated data, comparing it to existing entries."""
        self.tree.clear()
        existing_entries = {}
        for cat in self.existing_compendium.get("categories", []):
            for entry in cat.get("entries", []):
                existing_entries[f"{cat['name']}/{entry['name']}"] = entry.get("content", "")

        for cat in self.ai_compendium_data.get("categories", []):
            cat_item = QTreeWidgetItem(self.tree, [cat.get("name", "Unnamed Category")])
            cat_item.setData(0, Qt.UserRole, "category")
            for entry in cat.get("entries", []):
                entry_name = entry.get("name", "Unnamed Entry")
                entry_content = entry.get("content", "")
                key = f"{cat['name']}/{entry_name}"
                entry_item = QTreeWidgetItem(cat_item, [entry_name])
                entry_item.setData(0, Qt.UserRole, "entry")
                entry_item.setData(1, Qt.UserRole, entry_content)

                # Compare with existing compendium
                if key in existing_entries and existing_entries[key] == entry_content:
                    entry_item.setData(2, Qt.UserRole, "Unchanged")
                    entry_item.setFlags(entry_item.flags() & ~Qt.ItemIsEditable)
                else:
                    # New or modified entry: highlight in bold
                    font = QFont()
                    font.setBold(True)
                    entry_item.setFont(0, font)
                    entry_item.setData(2, Qt.UserRole, "Modified")

            cat_item.setExpanded(True)

    def on_item_changed(self, current, previous):
        """Update the editor when a tree item is selected."""
        if current is None:
            self.editor.clear()
            self.editor.setReadOnly(True)
            return
        if current.data(0, Qt.UserRole) == "entry":
            content = current.data(1, Qt.UserRole)
            status = current.data(2, Qt.UserRole)
            self.editor.setPlainText(content)
            self.editor.setReadOnly(status == "Unchanged")
        else:
            self.editor.clear()
            self.editor.setReadOnly(True)

    def show_tree_context_menu(self, pos):
        """Display a context menu for tree items."""
        restore_action = None
        item = self.tree.itemAt(pos)
        if item and item.data(0, Qt.UserRole) == "entry":
            menu = QMenu(self)
            is_deleted = item.data(2, Qt.UserRole) == "Deleted"
            if is_deleted:
                restore_action = menu.addAction("Restore")
            else:
                delete_action = menu.addAction("Ignore Update")  # For deleted entries, we use "Ignore Update"
                rename_action = menu.addAction("Rename Entry")
                move_to_action = menu.addAction("Move To...")
                move_up_action = menu.addAction("Move Up")
                move_down_action = menu.addAction("Move Down")

            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))

            if action:
                # Restore must come first
                if action == restore_action:
                    self.restore_entry(item)
                elif action == delete_action:
                    self.delete_entry(item)
                elif action == rename_action:
                    self.rename_entry(item)
                elif action == move_to_action:
                    self.move_entry(item)
                elif action == move_up_action:
                    self.move_item(item, "up")
                elif action == move_down_action:
                    self.move_item(item, "down")

    def delete_entry(self, item):
        """Mark an entry as deleted with strike-through font."""
        font = item.font(0)
        font.setStrikeOut(True)
        item.setFont(0, font)
        item.setData(2, Qt.UserRole, "Deleted")
        self.editor.clear()
        self.editor.setReadOnly(True)

    def restore_entry(self, item):
        """Restore a deleted entry."""
        font = item.font(0)
        font.setStrikeOut(False)
        if item.data(2, Qt.UserRole) != "Unchanged":
            font.setBold(True)
        item.setFont(0, font)
        item.setFlags(item.flags() | Qt.ItemIsSelectable)
        item.setData(2, Qt.UserRole, "Modified" if item.data(2, Qt.UserRole) != "Unchanged" else "Unchanged")
        self.tree.setCurrentItem(item)

    def rename_entry(self, item):
        """Rename an entry."""
        old_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "Rename Entry", "New name:", text=old_name)
        if ok and new_name:
            item.setText(0, new_name)
            # Update the content if it's currently selected
            if self.tree.currentItem() == item:
                self.editor.setPlainText(item.data(1, Qt.UserRole))

    def move_item(self, item, direction):
        """Move an item up or down within its category."""
        parent = item.parent()
        index = parent.indexOfChild(item)
        if direction == "up" and index > 0:
            parent.takeChild(index)
            parent.insertChild(index - 1, item)
            self.tree.setCurrentItem(item)
        elif direction == "down" and index < parent.childCount() - 1:
            parent.takeChild(index)
            parent.insertChild(index + 1, item)
            self.tree.setCurrentItem(item)

    def move_entry(self, item):
        """Move an entry to another category."""
        menu = QMenu(self)
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            if cat_item.data(0, Qt.UserRole) == "category":
                action = menu.addAction(cat_item.text(0))
                action.setData(cat_item)
        selected_action = menu.exec_(QCursor.pos())
        if selected_action:
            target_category = selected_action.data()
            current_parent = item.parent()
            current_parent.removeChild(item)
            target_category.addChild(item)
            target_category.setExpanded(True)
            self.tree.setCurrentItem(item)

    def save_and_close(self):
        """Save the modified compendium data and close the dialog."""
        try:
            # Reconstruct the compendium data excluding deleted entries
            new_data = {"categories": []}
            root = self.tree.invisibleRootItem()
            for i in range(root.childCount()):
                cat_item = root.child(i)
                cat_data = {"name": cat_item.text(0), "entries": []}
                for j in range(cat_item.childCount()):
                    entry_item = cat_item.child(j)
                    if entry_item.data(2, Qt.UserRole) != "Deleted":
                        entry_content = (self.editor.toPlainText() if self.tree.currentItem() == entry_item 
                                         and entry_item.data(2, Qt.UserRole) != "Unchanged"
                                         else entry_item.data(1, Qt.UserRole))
                        cat_data["entries"].append({
                            "name": entry_item.text(0),
                            "content": entry_content
                        })
                if cat_data["entries"]:  # Only add categories with entries
                    new_data["categories"].append(cat_data)

            # Validate JSON
            json.dumps(new_data)
            self.ai_compendium_data = new_data
            self.write_settings()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
            return

    def reject(self):
        """Override reject to ensure settings are saved before closing."""
        self.write_settings()
        super().reject()

    def closeEvent(self, event):
        self.write_settings()
        event.accept()


    def get_compendium_data(self):
        """Return the current compendium data from the dialog."""
        return self.ai_compendium_data

    def zoom_in(self):
        """Increase font size."""
        if self.font_size < 24:  # Arbitrary max size
            self.font_size += 2
            self.update_font_size()

    def zoom_out(self):
        """Decrease font size."""
        if self.font_size > 8:  # Arbitrary min size
            self.font_size -= 2
            self.update_font_size()
            
    def update_font_size(self):
        """Apply the current font size to all tree items and widgets."""

        font = self.tree.header().font()
        font.setPointSize(self.font_size)
        self.tree.header().setFont(font)
        for i in range(self.tree.topLevelItemCount()):
            header_item = self.tree.topLevelItem(i)
            font = header_item.font(0)
            font.setPointSize(self.font_size)
            header_item.setFont(0, font)
            for j in range(header_item.childCount()):
                child_item = header_item.child(j)
                font = child_item.font(0)
                font.setPointSize(self.font_size)
                child_item.setFont(0, font)
        
        font = self.editor.font()
        font.setPointSize(self.font_size)
        self.editor.setFont(font)

    def read_settings(self):
        settings = QSettings("MyCompany", "WritingwayProject")
        geometry = settings.value("prompt_preview/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        # Load font size, default to 12 if not set
        self.font_size = settings.value("ai_compendium_dialog/fontSize", 12, type=int)
        self.update_font_size()  # Apply the loaded font size

    def write_settings(self):
        settings = QSettings("MyCompany", "WritingwayProject")
        settings.setValue("ai_compendium_dialog/geometry", self.saveGeometry())
        settings.setValue("ai_compendium_dialog/fontSize", self.font_size)  # Save font size

