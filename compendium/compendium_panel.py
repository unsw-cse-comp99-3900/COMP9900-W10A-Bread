from PyQt5.QtWidgets import QWidget, QSplitter, QTreeWidget, QTextEdit, QVBoxLayout, QMenu, QTreeWidgetItem, QInputDialog
from PyQt5.QtCore import Qt, QPoint
import json, os, re
from .enhanced_compendium import EnhancedCompendiumWindow

DEBUG = False  # Set to True to enable debug prints

def sanitize(text):
    return re.sub(r'\W+', '', text)

class CompendiumPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        
        # Determine the project name from the parent window and set the compendium file path.
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
        # The editor is now set to read-only so that this panel serves only as a reference.
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a compendium entry to view.")
        self.editor.setReadOnly(True)
        
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
        """Load compendium data from the file and populate the tree view."""
        self.tree.clear()
        if os.path.exists(self.compendium_file):
            try:
                with open(self.compendium_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if DEBUG:
                    print("Compendium data loaded:", data)
                
                # Convert from old format if necessary.
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
                    with open(self.compendium_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    if DEBUG:
                        print("Conversion complete. Data saved in new format.")
                
                # Populate the tree.
                for cat in data.get("categories", []):
                    cat_item = QTreeWidgetItem(self.tree, [cat.get("name", "Unnamed Category")])
                    cat_item.setData(0, Qt.UserRole, "category")
                    for entry in cat.get("entries", []):
                        entry_item = QTreeWidgetItem(cat_item, [entry.get("name", "Unnamed Entry")])
                        entry_item.setData(0, Qt.UserRole, "entry")
                        entry_item.setData(1, Qt.UserRole, entry.get("content", ""))
                    cat_item.setExpanded(True)
            except Exception as e:
                if DEBUG:
                    print("Error loading compendium data:", e)
        else:
            if DEBUG:
                print("Compendium file not found at", self.compendium_file)
            # Create default structure.
            default_data = {"categories": [{"name": "Characters", "entries": [{"name": "Readme", "content": "This is a dummy entry. You can view it for reference."}]}]}
            try:
                with open(self.compendium_file, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
                if DEBUG:
                    print("Created default compendium data at", self.compendium_file)
            except Exception as e:
                if DEBUG:
                    print("Error creating default compendium file:", e)
            self.populate_compendium()

    def on_item_changed(self, current, previous):
        """Display entry content in the read-only editor when a tree item is selected."""
        if current is None:
            self.editor.clear()
            return
        if current.data(0, Qt.UserRole) == "entry":
            content = current.data(1, Qt.UserRole)
            self.editor.setPlainText(content)
        else:
            self.editor.clear()

    def show_tree_context_menu(self, pos: QPoint):
        """Display a simplified context menu with only the option to open the enhanced compendium."""
        menu = QMenu(self)
        action_open = menu.addAction("Open Enhanced Compendium")
        action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
        if action == action_open:
            self.open_in_enhanced_compendium()

    def open_in_enhanced_compendium(self):
        """Launch the enhanced compendium window.
        If an entry is selected, the enhanced window will jump to that entry."""
        project_name = getattr(self.parent(), "project_name", "default")
        self.enhanced_window = EnhancedCompendiumWindow(project_name, self.parent())
        self.enhanced_window.show()
        # If an entry is selected, try to select it in the enhanced window.
        current_item = self.tree.currentItem()
        if current_item and current_item.data(0, Qt.UserRole) == "entry":
            entry_name = current_item.text(0)
            if entry_name.startswith("* "):
                entry_name = entry_name[2:]
            self.enhanced_window.find_and_select_entry(entry_name)
