# compendium_panel.py
from PyQt5.QtWidgets import QWidget, QSplitter, QTreeWidget, QTextEdit, QVBoxLayout, QMenu, QTreeWidgetItem, QInputDialog
from PyQt5.QtCore import Qt, QPoint
import json, os, re

DEBUG = False  # Set to True to enable debug prints

def sanitize(text):
    return re.sub(r'\W+', '', text)

class CompendiumPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        
        # Determine the project name from the parent window and set the new compendium file path.
        project_name = getattr(self.parent(), "project_name", "default")
        self.new_compendium_file = os.path.join(os.getcwd(), "Projects", sanitize(project_name), "compendium.json")
        if DEBUG:
            print("New compendium file path:", self.new_compendium_file)
        
        # Ensure the project directory exists.
        project_dir = os.path.dirname(self.new_compendium_file)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        # Check for an old compendium file in the main directory.
        self.old_compendium_file = os.path.join(os.getcwd(), "compendium.json")
        if os.path.exists(self.old_compendium_file):
            if DEBUG:
                print("Old compendium file found at", self.old_compendium_file)
            try:
                with open(self.old_compendium_file, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                # Save data to the new compendium file.
                with open(self.new_compendium_file, "w", encoding="utf-8") as f:
                    json.dump(old_data, f, indent=2)
                # Delete the old compendium file.
                os.remove(self.old_compendium_file)
                if DEBUG:
                    print("Migrated compendium data to", self.new_compendium_file)
            except Exception as e:
                if DEBUG:
                    print("Error migrating old compendium file:", e)
        
        # Set self.compendium_file to the new location.
        self.compendium_file = self.new_compendium_file
        
        # Create a horizontal splitter dividing the panel into a tree and an editor.
        self.splitter = QSplitter(Qt.Horizontal, self)
        
        # Left side: Tree for categories and entries.
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Compendium")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.tree.currentItemChanged.connect(self.on_item_changed)
        
        # Right side: Editor for the selected entry.
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a compendium entry to view/edit.")
        
        # Set up the layout.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.editor)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        
        # Load the compendium data.
        self.populate_compendium()

    def populate_compendium(self):
        """Load compendium data from the compendium file, convert it if necessary, and populate the tree."""
        self.tree.clear()
        if os.path.exists(self.compendium_file):
            try:
                with open(self.compendium_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if DEBUG:
                    print("Compendium data loaded:", data)
                
                # Detect if data is in the old format (categories as dict) and convert if needed.
                if isinstance(data.get("categories"), dict):
                    if DEBUG:
                        print("Old format detected. Converting data...")
                    old_categories = data["categories"]
                    category_order = data.get("category_order", list(old_categories.keys()))
                    new_categories = []
                    for cat_name in category_order:
                        entries_dict = old_categories.get(cat_name, {})
                        entries_list = []
                        for entry_name, entry_content in entries_dict.items():
                            entries_list.append({
                                "name": entry_name,
                                "content": entry_content
                            })
                        new_categories.append({
                            "name": cat_name,
                            "entries": entries_list
                        })
                    data["categories"] = new_categories
                    # Save the converted data back to file.
                    with open(self.compendium_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    if DEBUG:
                        print("Conversion complete. Data saved in new format.")
                
                # Now data["categories"] should be a list.
                for cat in data.get("categories", []):
                    cat_item = QTreeWidgetItem(self.tree, [cat.get("name", "Unnamed Category")])
                    cat_item.setData(0, Qt.UserRole, "category")
                    for entry in cat.get("entries", []):
                        entry_item = QTreeWidgetItem(cat_item, [entry.get("name", "Unnamed Entry")])
                        entry_item.setData(0, Qt.UserRole, "entry")
                        # Store the entry content using a custom role.
                        entry_item.setData(1, Qt.UserRole, entry.get("content", ""))
                    cat_item.setExpanded(True)
            except Exception as e:
                if DEBUG:
                    print("Error loading compendium data:", e)
        else:
            if DEBUG:
                print("Compendium file not found at", self.compendium_file)
            # Create default structure if file does not exist.
            default_data = {"categories": [{"name": "Default Category", "entries": [{"name": "Default Entry", "content": "This is the default entry content."}]}]}
            try:
                with open(self.compendium_file, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
                if DEBUG:
                    print("Created default compendium data at", self.compendium_file)
            except Exception as e:
                if DEBUG:
                    print("Error creating default compendium file:", e)
            self.populate_compendium()  # Reload now that the file exists.

    def on_item_changed(self, current, previous):
        """When a tree item is selected, update the editor with its content if it's an entry."""
        if current is None:
            self.editor.clear()
            return
        if current.data(0, Qt.UserRole) == "entry":
            content = current.data(1, Qt.UserRole)
            self.editor.setPlainText(content)
        else:
            self.editor.clear()

    def show_tree_context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        item_type = item.data(0, Qt.UserRole)
        if item_type == "category":
            # Right-click menu for categories.
            action_new = menu.addAction("New Entry")
            action_delete = menu.addAction("Delete Category")
            action_rename = menu.addAction("Rename Category")
            action_move_up = menu.addAction("Move Up")
            action_move_down = menu.addAction("Move Down")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == action_new:
                self.new_entry(item)
            elif action == action_delete:
                self.delete_category(item)
            elif action == action_rename:
                self.rename_item(item, "category")
            elif action == action_move_up:
                self.move_item(item, direction="up")
            elif action == action_move_down:
                self.move_item(item, direction="down")
        elif item_type == "entry":
            # Right-click menu for entries.
            action_save = menu.addAction("Save Entry")
            action_delete = menu.addAction("Delete Entry")
            action_rename = menu.addAction("Rename Entry")
            action_move_to = menu.addAction("Move To...")
            action_move_up = menu.addAction("Move Up")
            action_move_down = menu.addAction("Move Down")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == action_save:
                self.save_entry(item)
            elif action == action_delete:
                self.delete_entry(item)
            elif action == action_rename:
                self.rename_item(item, "entry")
            elif action == action_move_to:
                self.move_entry(item)
            elif action == action_move_up:
                self.move_item(item, direction="up")
            elif action == action_move_down:
                self.move_item(item, direction="down")

    # --- Category Actions ---
    def new_entry(self, category_item):
        new_item = QTreeWidgetItem(category_item, ["New Entry"])
        new_item.setData(0, Qt.UserRole, "entry")
        new_item.setData(1, Qt.UserRole, "")
        category_item.setExpanded(True)
        self.save_compendium_to_file()

    def delete_category(self, category_item):
        root = self.tree.invisibleRootItem()
        root.removeChild(category_item)
        self.save_compendium_to_file()

    # --- Common Rename ---
    def rename_item(self, item, item_type):
        current_text = item.text(0)
        new_text, ok = QInputDialog.getText(self, f"Rename {item_type.capitalize()}", "New name:", text=current_text)
        if ok and new_text:
            item.setText(0, new_text)
            self.save_compendium_to_file()

    def move_item(self, item, direction="up"):
        parent = item.parent() or self.tree.invisibleRootItem()
        index = parent.indexOfChild(item)
        if direction == "up" and index > 0:
            parent.takeChild(index)
            parent.insertChild(index - 1, item)
        elif direction == "down" and index < parent.childCount() - 1:
            parent.takeChild(index)
            parent.insertChild(index + 1, item)
        self.save_compendium_to_file()

    # --- Entry Actions ---
    def save_entry(self, entry_item):
        content = self.editor.toPlainText()
        entry_item.setData(1, Qt.UserRole, content)
        if DEBUG:
            print("Saved entry:", entry_item.text(0))
        self.save_compendium_to_file()

    def delete_entry(self, entry_item):
        parent = entry_item.parent()
        if parent:
            parent.removeChild(entry_item)
            self.save_compendium_to_file()

    from PyQt5.QtGui import QCursor

    def move_entry(self, entry_item):
        from PyQt5.QtGui import QCursor  # Import here if not imported globally
        # Create a menu listing all categories.
        menu = QMenu(self)
        root = self.tree.invisibleRootItem()
        categories = []
        for i in range(root.childCount()):
            cat_item = root.child(i)
            if cat_item.data(0, Qt.UserRole) == "category":
                categories.append(cat_item)
        if not categories:
            return
        # Add each category as an action.
        for cat in categories:
            action = menu.addAction(cat.text(0))
            action.setData(cat)  # store the category item in the action.
        # Execute the menu at the current mouse position.
        selected_action = menu.exec_(QCursor.pos())
        if selected_action is not None:
            target_category = selected_action.data()
            if target_category is not None:
                # Remove the entry from its current category.
                current_parent = entry_item.parent()
                if current_parent is not None:
                    current_parent.removeChild(entry_item)
                # Add the entry to the selected category.
                target_category.addChild(entry_item)
                target_category.setExpanded(True)
                self.save_compendium_to_file()

    def get_compendium_data(self):
        """Traverse the tree to reconstruct the compendium data."""
        data = {"categories": []}
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            if cat_item.data(0, Qt.UserRole) == "category":
                cat_data = {"name": cat_item.text(0), "entries": []}
                for j in range(cat_item.childCount()):
                    entry_item = cat_item.child(j)
                    if entry_item.data(0, Qt.UserRole) == "entry":
                        cat_data["entries"].append({
                            "name": entry_item.text(0),
                            "content": entry_item.data(1, Qt.UserRole)
                        })
                data["categories"].append(cat_data)
        return data

    def save_compendium_to_file(self):
        """Save the current compendium data back to the compendium file."""
        data = self.get_compendium_data()
        try:
            with open(self.compendium_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if DEBUG:
                print("Compendium data saved to", self.compendium_file)
        except Exception as e:
            if DEBUG:
                print("Error saving compendium data:", e)
