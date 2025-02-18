#!/usr/bin/env python3
import sys, os, json
from PyQt5.QtWidgets import (
    QDialog, QSplitter, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QToolBar, QAction, QMessageBox,
    QInputDialog, QWidget, QLineEdit, QLabel, QPushButton, QComboBox,
    QFormLayout, QMenu
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

JSON_FILE = "compendium.json"


class NewEntryDialog(QDialog):
    """
    A dialog for creating a new compendium entry.
    It includes an entry for the name and an editable combo box for the category.
    """
    def __init__(self, existing_categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Entry")
        self.entry_name = ""
        self.category = ""
        self.init_ui(existing_categories)

    def init_ui(self, existing_categories):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Entry Name:", self.name_edit)
        
        # Editable combo box: the user can choose an existing category or type a new one.
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(sorted(existing_categories))
        form.addRow("Category:", self.category_combo)
        
        layout.addLayout(form)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def accept(self):
        self.entry_name = self.name_edit.text().strip()
        self.category = self.category_combo.currentText().strip()
        if not self.entry_name or not self.category:
            QMessageBox.warning(self, "Input Error", "Both entry name and category are required.")
            return
        super().accept()


class ManageCategoryDialog(QDialog):
    """
    A dialog for changing an entry's category.
    It shows an editable combo box pre-populated with existing categories and the current category.
    """
    def __init__(self, current_category, existing_categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Category")
        self.new_category = current_category
        self.init_ui(current_category, existing_categories)

    def init_ui(self, current_category, existing_categories):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(sorted(existing_categories))
        self.category_combo.setCurrentText(current_category)
        form.addRow("Category:", self.category_combo)
        
        layout.addLayout(form)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def accept(self):
        self.new_category = self.category_combo.currentText().strip()
        if not self.new_category:
            QMessageBox.warning(self, "Input Error", "Category cannot be empty.")
            return
        super().accept()


class CompendiumWindow(QDialog):
    """
    The Compendium window for managing background entries.
    Data is stored in a JSON file.
    The left panel shows categories (as collapsible nodes) and their entries.
    The right panel provides an editor and toolbar.
    A search field at the top filters entries by name or content.
    Right-clicking an entry shows a context menu for delete, rename, or manage (change category).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compendium")
        self.resize(800, 500)
        # Data structure: { "categories": { category_name: { entry_name: content, ... }, ... }, "category_order": [category_name, ...] }
        self.data = {"categories": {}}
        self.load_from_file()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Search field at the top.
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search by entry name or content...")
        self.search_field.textChanged.connect(self.filter_entries)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_field)
        main_layout.addLayout(search_layout)
        
        # Main splitter divides the tree and the editor.
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: QTreeWidget for categories and entries.
        self.entry_tree = QTreeWidget()
        self.entry_tree.setHeaderHidden(True)
        self.entry_tree.itemClicked.connect(self.on_tree_item_clicked)
        # Enable custom context menu on the tree widget.
        self.entry_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entry_tree.customContextMenuRequested.connect(self.show_context_menu)
        main_splitter.addWidget(self.entry_tree)
        
        # Right Panel: Toolbar and Editor.
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.create_toolbar(right_layout)
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Edit entry content here...")
        right_layout.addWidget(self.editor)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(main_splitter)
        
        self.populate_tree()

    def create_toolbar(self, layout):
        self.toolbar = QToolBar()

        new_entry_action = QAction(QIcon.fromTheme("document-new"), "New Entry", self)
        new_entry_action.triggered.connect(self.new_entry)
        self.toolbar.addAction(new_entry_action)

        new_category_action = QAction(QIcon.fromTheme("folder-new"), "New Category", self)
        new_category_action.triggered.connect(self.new_category)
        self.toolbar.addAction(new_category_action)
        
        save_entry_action = QAction(QIcon.fromTheme("document-save"), "Save Entry", self)
        save_entry_action.triggered.connect(self.save_entry)
        self.toolbar.addAction(save_entry_action)
        
        delete_entry_action = QAction(QIcon.fromTheme("edit-delete"), "Delete Entry", self)
        delete_entry_action.triggered.connect(self.delete_entry)
        self.toolbar.addAction(delete_entry_action)
        
        rename_entry_action = QAction(QIcon.fromTheme("edit-rename"), "Rename Entry", self)
        rename_entry_action.triggered.connect(self.rename_entry)
        self.toolbar.addAction(rename_entry_action)
        
        manage_entry_action = QAction(QIcon.fromTheme("folder"), "Manage Category", self)
        manage_entry_action.triggered.connect(self.manage_entry)
        self.toolbar.addAction(manage_entry_action)
        
        layout.addWidget(self.toolbar)

    def populate_tree(self):
        """Populate the QTreeWidget from self.data using the category order."""
        self.entry_tree.clear()
        # Ensure category_order exists and is consistent
        category_order = self.data.get("category_order", list(self.data["categories"].keys()))
        # Add any new categories that might not be in the order list
        for cat in self.data["categories"]:
            if cat not in category_order:
                category_order.append(cat)
        # Remove any categories that no longer exist
        category_order = [cat for cat in category_order if cat in self.data["categories"]]
        self.data["category_order"] = category_order
        
        for category in category_order:
            entries = self.data["categories"][category]
            category_item = QTreeWidgetItem([category])
            category_item.setFlags(category_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for entry_name, content in entries.items():
                entry_item = QTreeWidgetItem([entry_name])
                category_item.addChild(entry_item)
            self.entry_tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
            
    def filter_entries(self, text):
        """
        Filter tree items by matching the search text against the entry name and content.
        Items that do not match are hidden.
        """
        text = text.lower()
        root = self.entry_tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            category_match = False
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                entry_name = entry_item.text(0).lower()
                # Look up the content in self.data.
                category = cat_item.text(0)
                entry_content = self.data["categories"].get(category, {}).get(entry_item.text(0), "").lower()
                # Determine if the entry should be visible.
                match = text in entry_name or text in entry_content
                entry_item.setHidden(not match)
                if match:
                    category_match = True
            cat_item.setHidden(not category_match)

    def on_tree_item_clicked(self, item, column):
        """
        When an entry is clicked, load its content into the editor.
        Only act if the clicked item is a child (an entry), not a category.
        """
        if item.parent() is None:
            return
        category = item.parent().text(0)
        entry_name = item.text(0)
        content = self.data["categories"].get(category, {}).get(entry_name, "")
        self.editor.setPlainText(content)

    def show_context_menu(self, pos):
        """
        Show a context menu when right-clicking.
        For a blank area, offer an option to add a new category.
        For a category, offer options to rename, delete, or move it up or down.
        For an entry, offer options for delete, rename, or manage category.
        """
        item = self.entry_tree.itemAt(pos)
        menu = QMenu()
        if item is None:
            add_category_action = menu.addAction("Add New Category")
            action = menu.exec_(self.entry_tree.viewport().mapToGlobal(pos))
            if action == add_category_action:
                self.new_category()
        elif item.parent() is None:
            # Category node context menu
            rename_action = menu.addAction("Rename Category")
            delete_action = menu.addAction("Delete Category")
            move_up_action = menu.addAction("Move Category Up")
            move_down_action = menu.addAction("Move Category Down")
            action = menu.exec_(self.entry_tree.viewport().mapToGlobal(pos))
            if action == rename_action:
                self.rename_category()
            elif action == delete_action:
                self.delete_category()
            elif action == move_up_action:
                self.move_category_up()
            elif action == move_down_action:
                self.move_category_down()
        else:
            # Entry node context menu
            delete_action = menu.addAction("Delete")
            rename_action = menu.addAction("Rename")
            manage_action = menu.addAction("Manage Category")
            action = menu.exec_(self.entry_tree.viewport().mapToGlobal(pos))
            if action == delete_action:
                self.entry_tree.setCurrentItem(item)
                self.delete_entry()
            elif action == rename_action:
                self.entry_tree.setCurrentItem(item)
                self.rename_entry()
            elif action == manage_action:
                self.entry_tree.setCurrentItem(item)
                self.manage_entry()

    def new_entry(self):
        """Show a dialog to create a new entry with name and category."""
        existing_categories = self.data["categories"].keys()
        dlg = NewEntryDialog(existing_categories, self)
        if dlg.exec_():
            entry_name = dlg.entry_name
            category = dlg.category
            if category not in self.data["categories"]:
                self.data["categories"][category] = {}
                # Ensure the new category is added to the order list
                if "category_order" not in self.data:
                    self.data["category_order"] = []
                self.data["category_order"].append(category)
            if entry_name in self.data["categories"][category]:
                QMessageBox.warning(self, "New Entry", "An entry with that name already exists in this category.")
                return
            self.data["categories"][category][entry_name] = ""
            self.populate_tree()
            self.save_to_file()

    def new_category(self):
        """Prompt the user to add a new category."""
        new_category, ok = QInputDialog.getText(self, "New Category", "Enter new category name:")
        new_category = new_category.strip()
        if ok:
            if not new_category:
                QMessageBox.warning(self, "New Category", "Category name cannot be empty.")
                return
            if new_category in self.data["categories"]:
                QMessageBox.warning(self, "New Category", "Category already exists.")
                return
            self.data["categories"][new_category] = {}
            if "category_order" not in self.data:
                self.data["category_order"] = []
            self.data["category_order"].append(new_category)
            self.populate_tree()
            self.save_to_file()

    def save_entry(self):
        """
        Save the content from the editor into the selected entry.
        Also writes the JSON file.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent():
            category = current_item.parent().text(0)
            entry_name = current_item.text(0)
            self.data["categories"][category][entry_name] = self.editor.toPlainText()
            QMessageBox.information(self, "Save Entry", f"Entry '{entry_name}' saved.")
            self.save_to_file()
        else:
            QMessageBox.warning(self, "Save Entry", "No entry selected to save.")

    def delete_entry(self):
        """
        Delete the selected entry.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent():
            category = current_item.parent().text(0)
            entry_name = current_item.text(0)
            reply = QMessageBox.question(self, "Delete Entry", f"Delete entry '{entry_name}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.data["categories"][category][entry_name]
                # If the category is now empty, remove it
                if not self.data["categories"][category]:
                    del self.data["categories"][category]
                    if "category_order" in self.data and category in self.data["category_order"]:
                        self.data["category_order"].remove(category)
                self.populate_tree()
                self.editor.clear()
                self.save_to_file()
        else:
            QMessageBox.warning(self, "Delete Entry", "No entry selected to delete.")

    def rename_entry(self):
        """
        Rename the selected entry.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent():
            category = current_item.parent().text(0)
            old_name = current_item.text(0)
            new_name, ok = QInputDialog.getText(self, "Rename Entry", "Enter new name:", text=old_name)
            new_name = new_name.strip()
            if ok and new_name and new_name != old_name:
                if new_name in self.data["categories"][category]:
                    QMessageBox.warning(self, "Rename Entry", "An entry with that name already exists in this category.")
                    return
                self.data["categories"][category][new_name] = self.data["categories"][category].pop(old_name)
                self.populate_tree()
                self.save_to_file()
        else:
            QMessageBox.warning(self, "Rename Entry", "No entry selected to rename.")

    def manage_entry(self):
        """
        Change the category of the selected entry.
        This now uses a pull-down (editable combo) dialog that shows existing categories.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent():
            old_category = current_item.parent().text(0)
            entry_name = current_item.text(0)
            existing_categories = self.data["categories"].keys()
            dlg = ManageCategoryDialog(old_category, existing_categories, self)
            if dlg.exec_():
                new_category = dlg.new_category
                if new_category and new_category != old_category:
                    content = self.data["categories"][old_category].pop(entry_name)
                    if new_category not in self.data["categories"]:
                        self.data["categories"][new_category] = {}
                        if "category_order" not in self.data:
                            self.data["category_order"] = []
                        self.data["category_order"].append(new_category)
                    if entry_name in self.data["categories"][new_category]:
                        QMessageBox.warning(self, "Manage Entry", "An entry with that name already exists in the new category.")
                        self.data["categories"][old_category][entry_name] = content
                    else:
                        self.data["categories"][new_category][entry_name] = content
                        if not self.data["categories"][old_category]:
                            del self.data["categories"][old_category]
                            if "category_order" in self.data and old_category in self.data["category_order"]:
                                self.data["category_order"].remove(old_category)
                    self.populate_tree()
                    self.save_to_file()
        else:
            QMessageBox.warning(self, "Manage Entry", "No entry selected to manage.")

    def rename_category(self):
        """
        Rename the selected category.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent() is None:
            old_category = current_item.text(0)
            new_category, ok = QInputDialog.getText(self, "Rename Category", "Enter new category name:", text=old_category)
            new_category = new_category.strip()
            if ok and new_category and new_category != old_category:
                if new_category in self.data["categories"]:
                    QMessageBox.warning(self, "Rename Category", "A category with that name already exists.")
                    return
                # Rename category in the data dictionary
                self.data["categories"][new_category] = self.data["categories"].pop(old_category)
                # Update category order list
                if "category_order" in self.data:
                    index = self.data["category_order"].index(old_category)
                    self.data["category_order"][index] = new_category
                self.populate_tree()
                self.save_to_file()
        else:
            QMessageBox.warning(self, "Rename Category", "No category selected.")

    def delete_category(self):
        """
        Delete the selected category and all its entries.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent() is None:
            category = current_item.text(0)
            reply = QMessageBox.question(self, "Delete Category", f"Delete category '{category}' and all its entries?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if category in self.data["categories"]:
                    del self.data["categories"][category]
                if "category_order" in self.data and category in self.data["category_order"]:
                    self.data["category_order"].remove(category)
                self.populate_tree()
                self.editor.clear()
                self.save_to_file()
        else:
            QMessageBox.warning(self, "Delete Category", "No category selected to delete.")

    def move_category_up(self):
        """
        Move the selected category up in the list.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent() is None:
            category = current_item.text(0)
            order = self.data.get("category_order", list(self.data["categories"].keys()))
            index = order.index(category)
            if index > 0:
                order[index], order[index-1] = order[index-1], order[index]
                self.data["category_order"] = order
                self.populate_tree()
                self.save_to_file()
            else:
                QMessageBox.information(self, "Move Category", "Category is already at the top.")
        else:
            QMessageBox.warning(self, "Move Category", "No category selected to move.")

    def move_category_down(self):
        """
        Move the selected category down in the list.
        """
        current_item = self.entry_tree.currentItem()
        if current_item and current_item.parent() is None:
            category = current_item.text(0)
            order = self.data.get("category_order", list(self.data["categories"].keys()))
            index = order.index(category)
            if index < len(order) - 1:
                order[index], order[index+1] = order[index+1], order[index]
                self.data["category_order"] = order
                self.populate_tree()
                self.save_to_file()
            else:
                QMessageBox.information(self, "Move Category", "Category is already at the bottom.")
        else:
            QMessageBox.warning(self, "Move Category", "No category selected to move.")

    def load_from_file(self):
        """Load compendium data from a JSON file."""
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                if "category_order" not in self.data:
                    self.data["category_order"] = list(self.data["categories"].keys())
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load JSON file: {e}")
                self.data = {"categories": {}}
        else:
            self.data = {
                "categories": {
                    "Characters": {
                        "Alice": "Details about Alice.",
                        "Bob": "Details about Bob."
                    },
                    "Locations": {
                        "New York": "Details about New York."
                    },
                    "Items": {
                        "Ancient Key": "Details about the Ancient Key."
                    }
                },
                "category_order": ["Characters", "Locations", "Items"]
            }
            self.save_to_file()

    def save_to_file(self):
        """Save compendium data to a JSON file."""
        try:
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save to JSON file: {e}")


# If you wish to run this file standalone for testing, uncomment below:
# if __name__ == "__main__":
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     window = CompendiumWindow()
#     window.show()
#     sys.exit(app.exec_())
