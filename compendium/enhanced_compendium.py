import os
import json
import re
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QSplitter, QTreeWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QListWidget, QTabWidget, QFileDialog, QMessageBox, QTreeWidgetItem,
                             QScrollArea, QFormLayout, QGroupBox, QInputDialog, QMenu, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

DEBUG = False

###########################
# CUSTOM TEMPLATE DIALOG  #
###########################
class CustomTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Template")
        self.resize(400, 200)
        self.layout = QVBoxLayout(self)
        
        # Template name input
        self.name_label = QLabel("Template Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        
        # Template fields input (comma-separated field names)
        self.fields_label = QLabel("Field Names (comma-separated):")
        self.fields_input = QLineEdit()
        self.layout.addWidget(self.fields_label)
        self.layout.addWidget(self.fields_input)
        
        # Dialog buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_template_data(self):
        """Return the template name and a dictionary of fields (default type 'text')."""
        name = self.name_input.text().strip()
        fields_text = self.fields_input.text().strip()
        if not name:
            return None, None
        fields = {}
        if fields_text:
            for field in fields_text.split(","):
                field_name = field.strip()
                if field_name:
                    fields[field_name] = {"type": "text", "label": field_name.capitalize()}
        return name, {"fields": fields}


#############################
# ENHANCED COMPENDIUM CLASS #
#############################
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QComboBox, QPushButton, QToolBar, QSizePolicy
)
from PyQt5.QtCore import Qt

class EnhancedCompendiumWindow(QMainWindow):
    def __init__(self, project_name="My First Project", parent=None):
        super().__init__(parent)

        self.project_name = project_name

        # 1) Create a QToolBar at the top instead of a big header panel
        self.toolbar = QToolBar("Project Toolbar")
        self.toolbar.setMovable(False)  # Keeps the toolbar fixed at the top
        self.addToolBar(self.toolbar)

        # 2) Add a label and combo box to the toolbar
        label = QLabel("<b>Project:</b>")
        self.toolbar.addWidget(label)

        self.project_combo = QComboBox()
        self.toolbar.addWidget(self.project_combo)

        # 3) Add a spacer so label + combo are left-aligned
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        # 4) Now set up the central widget (which holds the main layout and splitter)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 5) Create the main splitter for the rest of the UI
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)

        # 6) Create the left (tree), center (content/tabs), and right (tags/template) panels
        self.create_tree_view()
        self.create_center_panel()
        self.create_right_panel()

        # 7) Set splitter proportions
        self.main_splitter.setStretchFactor(0, 1)  # Tree view
        self.main_splitter.setStretchFactor(1, 2)  # Content panel
        self.main_splitter.setStretchFactor(2, 1)  # Right panel

        # 8) Set up the rest of your logic
        self.setup_compendium_file()
        self.define_templates()
        self.populate_compendium()
        self.connect_signals()

        # 9) Window title and size
        self.setWindowTitle(f"Enhanced Compendium - {self.project_name}")
        self.resize(900, 700)

        # 10) Finally, populate the project combo and connect its signal
        self.populate_project_combo()
        self.project_combo.currentTextChanged.connect(self.on_project_combo_changed)
    
    def populate_project_combo(self):
        """Populate the project pulldown with subdirectories in .\Projects."""
        projects_path = os.path.join(os.getcwd(), "Projects")
        if not os.path.exists(projects_path):
            os.makedirs(projects_path)
        projects = [d for d in os.listdir(projects_path) if os.path.isdir(os.path.join(projects_path, d))]
        self.project_combo.clear()
        if projects:
            self.project_combo.addItems(projects)
        else:
            self.project_combo.addItem("My First Project")
        index = self.project_combo.findText(self.project_name)
        if index >= 0:
            self.project_combo.setCurrentIndex(index)
        else:
            self.project_combo.setCurrentIndex(0)
            self.project_name = self.project_combo.currentText()
    
    def on_project_combo_changed(self, new_project):
        """Update the project and reload the compendium when a different project is selected."""
        self.project_name = new_project
        self.setWindowTitle(f"Enhanced Compendium - {self.project_name}")
        self.setup_compendium_file()
        self.populate_compendium()
    
    def setup_compendium_file(self):
        """Set up the compendium file path for the selected project."""
        project_dir = os.path.join(os.getcwd(), "Projects", self.sanitize(self.project_name))
        self.compendium_file = os.path.join(project_dir, "compendium.json")
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        if DEBUG:
            print("Loading compendium from:", self.compendium_file)
    
    def create_tree_view(self):
        """Create the left panel: a tree view (with a search bar) for categories and entries."""
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search entries...")
        tree_layout.addWidget(self.search_bar)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Compendium")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree_layout.addWidget(self.tree)
        self.main_splitter.addWidget(self.tree_widget)
    
    def create_center_panel(self):
        """Create the center panel with a header and a tabbed view for content, details, relationships, and images."""
        self.center_widget = QWidget()
        center_layout = QVBoxLayout(self.center_widget)
        
        # Header
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        self.entry_name_label = QLabel("No entry selected")
        self.entry_name_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(self.entry_name_label)
        self.entry_template_label = QLabel("")
        header_layout.addWidget(self.entry_template_label)
        header_layout.addStretch()
        self.save_button = QPushButton("Save Changes")
        self.save_button.setEnabled(False)
        header_layout.addWidget(self.save_button)
        center_layout.addWidget(self.header_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Overview Tab
        self.overview_tab = QWidget()
        overview_layout = QVBoxLayout(self.overview_tab)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a compendium entry to view/edit.")
        overview_layout.addWidget(self.editor)
        self.tabs.addTab(self.overview_tab, "Overview")
        
        # Details Tab
        self.details_tab = QScrollArea()
        self.details_tab.setWidgetResizable(True)
        self.details_content = QWidget()
        self.details_layout = QVBoxLayout(self.details_content)
        self.details_tab.setWidget(self.details_content)
        self.tabs.addTab(self.details_tab, "Details")
        
        # Relationships Tab
        self.relationships_tab = QWidget()
        relationships_layout = QVBoxLayout(self.relationships_tab)
        add_rel_group = QGroupBox("Add Relationship")
        add_rel_layout = QFormLayout(add_rel_group)
        self.rel_entry_combo = QComboBox()
        self.rel_type_combo = QComboBox()
        self.rel_type_combo.addItems(["Friend", "Family", "Ally", "Enemy", "Acquaintance", "Other"])
        self.rel_type_combo.setEditable(True)
        self.add_rel_button = QPushButton("Add")
        add_rel_layout.addRow("Related Entry:", self.rel_entry_combo)
        add_rel_layout.addRow("Relationship Type:", self.rel_type_combo)
        add_rel_layout.addRow("", self.add_rel_button)
        relationships_layout.addWidget(add_rel_group)
        self.relationships_list = QTreeWidget()
        self.relationships_list.setHeaderLabels(["Entry", "Relationship Type"])
        self.relationships_list.setContextMenuPolicy(Qt.CustomContextMenu)
        relationships_layout.addWidget(self.relationships_list)
        self.tabs.addTab(self.relationships_tab, "Relationships")
        
        # Images Tab
        self.images_tab = QWidget()
        images_layout = QVBoxLayout(self.images_tab)
        image_controls = QWidget()
        image_controls_layout = QHBoxLayout(image_controls)
        self.add_image_button = QPushButton("Add Image")
        self.remove_image_button = QPushButton("Remove Selected")
        self.remove_image_button.setEnabled(False)
        image_controls_layout.addWidget(self.add_image_button)
        image_controls_layout.addWidget(self.remove_image_button)
        image_controls_layout.addStretch()
        images_layout.addWidget(image_controls)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_scroll.setWidget(self.image_container)
        images_layout.addWidget(self.image_scroll)
        self.tabs.addTab(self.images_tab, "Images")
        
        center_layout.addWidget(self.tabs)
        self.main_splitter.addWidget(self.center_widget)
    
    def create_right_panel(self):
        """Create the right panel with template selection and tag management."""
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        template_group = QGroupBox("Template")
        template_layout = QVBoxLayout(template_group)
        self.template_combo = QComboBox()
        self.template_combo.addItem("None")
        self.add_template_button = QPushButton("Add Template")
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(self.add_template_button)
        right_layout.addWidget(template_group)
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        tag_input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add new tag...")
        self.add_tag_button = QPushButton("+")
        self.add_tag_button.setFixedWidth(30)
        tag_input_layout.addWidget(self.tag_input)
        tag_input_layout.addWidget(self.add_tag_button)
        tags_layout.addLayout(tag_input_layout)
        self.tags_list = QListWidget()
        self.tags_list.setContextMenuPolicy(Qt.CustomContextMenu)
        tags_layout.addWidget(self.tags_list)
        right_layout.addWidget(tags_group)
        self.main_splitter.addWidget(self.right_widget)
    
    def define_templates(self):
        """Define the default templates."""
        self.templates = {
            "Character": {
                "fields": {
                    "appearance": {"type": "text", "label": "Appearance"},
                    "personality": {"type": "text", "label": "Personality"},
                    "background": {"type": "text", "label": "Background"},
                    "goals": {"type": "text", "label": "Goals"},
                    "strengths": {"type": "text", "label": "Strengths"},
                    "weaknesses": {"type": "text", "label": "Weaknesses"}
                }
            },
            "Location": {
                "fields": {
                    "description": {"type": "text", "label": "Description"},
                    "history": {"type": "text", "label": "History"},
                    "significance": {"type": "text", "label": "Significance"},
                    "inhabitants": {"type": "text", "label": "Inhabitants"},
                    "points_of_interest": {"type": "text", "label": "Points of Interest"}
                }
            },
            "Item": {
                "fields": {
                    "description": {"type": "text", "label": "Description"},
                    "properties": {"type": "text", "label": "Properties"},
                    "history": {"type": "text", "label": "History"},
                    "significance": {"type": "text", "label": "Significance"}
                }
            },
            "Concept": {
                "fields": {
                    "definition": {"type": "text", "label": "Definition"},
                    "explanation": {"type": "text", "label": "Explanation"},
                    "examples": {"type": "text", "label": "Examples"},
                    "implications": {"type": "text", "label": "Implications"}
                }
            }
        }
    
    def populate_compendium(self):
        """Load compendium data from the file and populate the UI."""
        self.tree.clear()
        if not os.path.exists(self.compendium_file):
            if DEBUG:
                print("Compendium file not found, creating default structure")
            default_data = {
                "categories": [
                    {
                        "name": "Characters", 
                        "entries": [
                            {
                                "name": "Readme", 
                                "content": "This is a dummy entry. You can view and edit extended data in this window."
                            }
                        ]
                    }
                ],
                "extensions": {
                    "entries": {}
                }
            }
            try:
                with open(self.compendium_file, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
                if DEBUG:
                    print("Created default compendium data at", self.compendium_file)
            except Exception as e:
                if DEBUG:
                    print("Error creating default compendium file:", e)
                QMessageBox.warning(self, "Error", f"Failed to create default compendium file: {str(e)}")
                return
        
        try:
            with open(self.compendium_file, "r", encoding="utf-8") as f:
                self.compendium_data = json.load(f)
            if DEBUG:
                print("Loaded compendium data")
            
            if "extensions" not in self.compendium_data:
                self.compendium_data["extensions"] = {"entries": {}}
            elif "entries" not in self.compendium_data["extensions"]:
                self.compendium_data["extensions"]["entries"] = {}
            
            if "templates" in self.compendium_data["extensions"]:
                for tmpl_name, tmpl_def in self.compendium_data["extensions"]["templates"].items():
                    if tmpl_name not in self.templates:
                        self.templates[tmpl_name] = tmpl_def
                        self.template_combo.addItem(tmpl_name)
            
            for cat in self.compendium_data.get("categories", []):
                cat_item = QTreeWidgetItem(self.tree, [cat.get("name", "Unnamed Category")])
                cat_item.setData(0, Qt.UserRole, "category")
                for entry in cat.get("entries", []):
                    entry_name = entry.get("name", "Unnamed Entry")
                    entry_item = QTreeWidgetItem(cat_item, [entry_name])
                    entry_item.setData(0, Qt.UserRole, "entry")
                    entry_item.setData(1, Qt.UserRole, entry.get("content", ""))
                    if entry_name in self.compendium_data["extensions"]["entries"]:
                        entry_item.setText(0, f"* {entry_name}")
                cat_item.setExpanded(True)
            self.update_relation_combo()
            
        except Exception as e:
            if DEBUG:
                print("Error loading compendium data:", e)
            QMessageBox.warning(self, "Error", f"Failed to load compendium data: {str(e)}")
    
    def update_relation_combo(self):
        """Populate the relationship combo box with available entries."""
        self.rel_entry_combo.clear()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                entry_name = entry_item.text(0)
                if entry_name.startswith("* "):
                    entry_name = entry_name[2:]
                self.rel_entry_combo.addItem(entry_name)
    
    def connect_signals(self):
        """Connect UI signals to their respective handlers."""
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.tree.currentItemChanged.connect(self.on_item_changed)
        self.search_bar.textChanged.connect(self.filter_tree)
        self.save_button.clicked.connect(self.save_current_entry)
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        self.add_template_button.clicked.connect(self.add_custom_template)
        self.add_tag_button.clicked.connect(self.add_tag)
        self.tag_input.returnPressed.connect(self.add_tag)
        self.tags_list.customContextMenuRequested.connect(self.show_tags_context_menu)
        self.add_rel_button.clicked.connect(self.add_relationship)
        self.relationships_list.customContextMenuRequested.connect(self.show_relationships_context_menu)
        self.relationships_list.itemDoubleClicked.connect(self.open_related_entry)
        self.add_image_button.clicked.connect(self.add_image)
        self.remove_image_button.clicked.connect(self.remove_selected_image)
    
    def show_tree_context_menu(self, pos):
        """Display context menu for the tree view."""
        item = self.tree.itemAt(pos)
        menu = QMenu(self)
        if item is None:
            action_new_category = menu.addAction("New Category")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == action_new_category:
                self.new_category()
            return
        item_type = item.data(0, Qt.UserRole)
        if item_type == "category":
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
                self.move_item(item, "up")
            elif action == action_move_down:
                self.move_item(item, "down")
        elif item_type == "entry":
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
                self.move_item(item, "up")
            elif action == action_move_down:
                self.move_item(item, "down")
    
    def show_tags_context_menu(self, pos):
        """Show context menu for tag removal."""
        item = self.tags_list.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            action_remove = menu.addAction("Remove Tag")
            action = menu.exec_(self.tags_list.viewport().mapToGlobal(pos))
            if action == action_remove:
                self.tags_list.takeItem(self.tags_list.row(item))
                self.save_button.setEnabled(True)
    
    def show_relationships_context_menu(self, pos):
        """Show context menu for relationship removal."""
        item = self.relationships_list.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            action_remove = menu.addAction("Remove Relationship")
            action = menu.exec_(self.relationships_list.viewport().mapToGlobal(pos))
            if action == action_remove:
                self.relationships_list.takeTopLevelItem(self.relationships_list.indexOfTopLevelItem(item))
                self.save_button.setEnabled(True)
    
    def add_custom_template(self):
        """Open the custom template dialog to add a new template."""
        dialog = CustomTemplateDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            template_name, template_def = dialog.get_template_data()
            if template_name and template_def:
                if template_name not in self.templates:
                    self.templates[template_name] = template_def
                    self.template_combo.addItem(template_name)
                    if "templates" not in self.compendium_data["extensions"]:
                        self.compendium_data["extensions"]["templates"] = {}
                    self.compendium_data["extensions"]["templates"][template_name] = template_def
                    self.save_button.setEnabled(True)
    
    def add_tag(self):
        """Add a new tag to the current entry."""
        if not hasattr(self, 'current_entry'):
            return
        tag = self.tag_input.text().strip()
        if not tag:
            return
        for i in range(self.tags_list.count()):
            if self.tags_list.item(i).text() == tag:
                return
        self.tags_list.addItem(tag)
        self.tag_input.clear()
        self.save_button.setEnabled(True)
        self.update_entry_indicator()
    
    def add_relationship(self):
        """Add a new relationship to the current entry."""
        if not hasattr(self, 'current_entry'):
            return
        related_entry = self.rel_entry_combo.currentText()
        rel_type = self.rel_type_combo.currentText()
        if not related_entry or not rel_type:
            return
        rel_item = QTreeWidgetItem([related_entry, rel_type])
        self.relationships_list.addTopLevelItem(rel_item)
        self.save_button.setEnabled(True)
        self.update_entry_indicator()
    
    def open_related_entry(self, item, column):
        """Double-click a relationship to open the corresponding entry."""
        entry_name = item.text(0)
        self.find_and_select_entry(entry_name)

    def sanitize(self, text):
        return re.sub(r'\W+', '', text)    

    def add_image(self):
        """Add an image to the current entry."""
        if not hasattr(self, 'current_entry'):
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)")
        if not file_path:
            return
        project_dir = os.path.dirname(self.compendium_file)
        images_dir = os.path.join(project_dir, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        _, ext = os.path.splitext(file_path)
        sanitized_entry_name = self.sanitize(self.current_entry)
        new_filename = f"{sanitized_entry_name}_{timestamp}{ext}"
        new_path = os.path.join(images_dir, new_filename)
        try:
            shutil.copy2(file_path, new_path)
            if self.current_entry not in self.compendium_data["extensions"]["entries"]:
                self.compendium_data["extensions"]["entries"][self.current_entry] = {}
            if "images" not in self.compendium_data["extensions"]["entries"][self.current_entry]:
                self.compendium_data["extensions"]["entries"][self.current_entry]["images"] = []
            self.compendium_data["extensions"]["entries"][self.current_entry]["images"].append(new_filename)
            self.add_image_to_ui(new_path, new_filename)
            self.save_button.setEnabled(True)
            self.update_entry_indicator()
        except Exception as e:
            if DEBUG:
                print("Error copying image:", e)
            QMessageBox.warning(self, "Error", f"Failed to copy image: {str(e)}")
    
    def load_images(self, image_filenames):
        """Load images for the current entry."""
        self.clear_images()
        if not image_filenames:
            return
        project_dir = os.path.dirname(self.compendium_file)
        images_dir = os.path.join(project_dir, "images")
        for filename in image_filenames:
            image_path = os.path.join(images_dir, filename)
            if os.path.exists(image_path):
                self.add_image_to_ui(image_path, filename)
    
    def add_image_to_ui(self, image_path, filename):
        """Display an image in the UI."""
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            max_width = 400
            if pixmap.width() > max_width:
                pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setProperty("filename", filename)
            image_label.setFrameShape(QLabel.Box)
            image_label.setObjectName("image")
            image_label.mousePressEvent = lambda event, label=image_label: self.select_image(label)
            image_layout.addWidget(image_label)
            name_label = QLabel(filename)
            name_label.setAlignment(Qt.AlignCenter)
            image_layout.addWidget(name_label)
            self.image_layout.addWidget(image_container)
        else:
            if DEBUG:
                print(f"Failed to load image: {image_path}")
    
    def select_image(self, label):
        """Select an image (for removal)."""
        for i in range(self.image_layout.count()):
            container = self.image_layout.itemAt(i).widget()
            for j in range(container.layout().count()):
                widget = container.layout().itemAt(j).widget()
                if isinstance(widget, QLabel) and widget.objectName() == "image":
                    widget.setStyleSheet("")
        label.setStyleSheet("border: 2px solid blue;")
        self.remove_image_button.setEnabled(True)
        self.selected_image = label
    
    def remove_selected_image(self):
        """Remove the selected image."""
        if not hasattr(self, 'selected_image'):
            return
        filename = self.selected_image.property("filename")
        if (hasattr(self, 'current_entry') and 
            self.current_entry in self.compendium_data["extensions"]["entries"] and
            "images" in self.compendium_data["extensions"]["entries"][self.current_entry]):
            if filename in self.compendium_data["extensions"]["entries"][self.current_entry]["images"]:
                self.compendium_data["extensions"]["entries"][self.current_entry]["images"].remove(filename)
            container = self.selected_image.parent()
            if container:
                container.deleteLater()
            self.remove_image_button.setEnabled(False)
            del self.selected_image
            self.save_button.setEnabled(True)
            self.update_entry_indicator()
    
    def filter_tree(self, text):
        """Filter the tree view based on the search text."""
        if not text:
            for i in range(self.tree.topLevelItemCount()):
                cat_item = self.tree.topLevelItem(i)
                cat_item.setHidden(False)
                for j in range(cat_item.childCount()):
                    cat_item.child(j).setHidden(False)
            return
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            cat_visible = False
            if text in cat_item.text(0).lower():
                cat_visible = True
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                entry_name = entry_item.text(0)
                if entry_name.startswith("* "):
                    entry_name = entry_name[2:]
                if text in entry_name.lower():
                    entry_item.setHidden(False)
                    cat_visible = True
                    continue
                if entry_name in self.compendium_data["extensions"]["entries"]:
                    extended_data = self.compendium_data["extensions"]["entries"][entry_name]
                    if any(text in tag.lower() for tag in extended_data.get("tags", [])):
                        entry_item.setHidden(False)
                        cat_visible = True
                        continue
                    if "template" in extended_data and "fields" in extended_data:
                        fields = extended_data["fields"]
                        if any(text in str(value).lower() for value in fields.values()):
                            entry_item.setHidden(False)
                            cat_visible = True
                            continue
                entry_item.setHidden(True)
            cat_item.setHidden(not cat_visible)
    
    def update_entry_indicator(self):
        """Update the '*' indicator on an entry based on extended data presence."""
        if not hasattr(self, 'current_entry') or not hasattr(self, 'current_entry_item'):
            return
        has_extended = (
            self.current_entry in self.compendium_data["extensions"]["entries"] and
            bool(self.compendium_data["extensions"]["entries"][self.current_entry])
        )
        current_text = self.current_entry_item.text(0)
        if has_extended and not current_text.startswith("* "):
            self.current_entry_item.setText(0, f"* {self.current_entry}")
        elif not has_extended and current_text.startswith("* "):
            self.current_entry_item.setText(0, self.current_entry)
    
    def save_entry(self, entry_item):
        """Save changes to a specific entry."""
        entry_name = entry_item.text(0)
        if entry_name.startswith("* "):
            entry_name = entry_name[2:]
        entry_item.setData(1, Qt.UserRole, self.editor.toPlainText())
        self.save_compendium_to_file()
        self.save_button.setEnabled(False)
    
    def save_current_entry(self):
        """Save the currently displayed entry (both basic and extended data)."""
        if not hasattr(self, 'current_entry') or not hasattr(self, 'current_entry_item'):
            return
        self.current_entry_item.setData(1, Qt.UserRole, self.editor.toPlainText())
        self.save_extended_data()
        self.save_compendium_to_file()
        self.save_button.setEnabled(False)
    
    def save_extended_data(self):
        """Extract and save extended data for the current entry."""
        if not hasattr(self, 'current_entry'):
            return
        if self.current_entry not in self.compendium_data["extensions"]["entries"]:
            self.compendium_data["extensions"]["entries"][self.current_entry] = {}
        template_name = self.template_combo.currentText()
        if template_name != "None":
            self.compendium_data["extensions"]["entries"][self.current_entry]["template"] = template_name
            fields_data = {}
            for i in range(self.details_layout.count()):
                item = self.details_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QGroupBox):
                    group_box = item.widget()
                    for j in range(group_box.layout().count()):
                        child = group_box.layout().itemAt(j)
                        if child.widget() and isinstance(child.widget(), QTextEdit):
                            field_widget = child.widget()
                            field_name = field_widget.property("field_name")
                            if field_name:
                                fields_data[field_name] = field_widget.toPlainText()
            self.compendium_data["extensions"]["entries"][self.current_entry]["fields"] = fields_data
        else:
            if "template" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["template"]
            if "fields" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["fields"]
        tags = []
        for i in range(self.tags_list.count()):
            tags.append(self.tags_list.item(i).text())
        if tags:
            self.compendium_data["extensions"]["entries"][self.current_entry]["tags"] = tags
        else:
            if "tags" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["tags"]
        relationships = []
        for i in range(self.relationships_list.topLevelItemCount()):
            item = self.relationships_list.topLevelItem(i)
            relationships.append({"name": item.text(0), "type": item.text(1)})
        if relationships:
            self.compendium_data["extensions"]["entries"][self.current_entry]["relationships"] = relationships
        else:
            if "relationships" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["relationships"]
        if not self.compendium_data["extensions"]["entries"][self.current_entry]:
            del self.compendium_data["extensions"]["entries"][self.current_entry]
        self.update_entry_indicator()
    
    def get_compendium_data(self):
        """Reconstruct the full compendium data."""
        data = {"categories": []}
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            cat_data = {"name": cat_item.text(0), "entries": []}
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                entry_name = entry_item.text(0)
                if entry_name.startswith("* "):
                    entry_name = entry_name[2:]
                cat_data["entries"].append({"name": entry_name, "content": entry_item.data(1, Qt.UserRole)})
            data["categories"].append(cat_data)
        data["extensions"] = self.compendium_data.get("extensions", {"entries": {}})
        return data
    
    def save_compendium_to_file(self):
        """Save the compendium data back to the file."""
        try:
            data = self.get_compendium_data()
            with open(self.compendium_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if DEBUG:
                print("Saved compendium data to", self.compendium_file)
        except Exception as e:
            if DEBUG:
                print("Error saving compendium data:", e)
            QMessageBox.warning(self, "Error", f"Failed to save compendium data: {str(e)}")
    
    def new_category(self):
        name, ok = QInputDialog.getText(self, "New Category", "Category name:")
        if ok and name:
            cat_item = QTreeWidgetItem(self.tree, [name])
            cat_item.setData(0, Qt.UserRole, "category")
            self.save_compendium_to_file()
    
    def new_entry(self, category_item):
        name, ok = QInputDialog.getText(self, "New Entry", "Entry name:")
        if ok and name:
            entry_item = QTreeWidgetItem(category_item, [name])
            entry_item.setData(0, Qt.UserRole, "entry")
            entry_item.setData(1, Qt.UserRole, "")
            category_item.setExpanded(True)
            self.save_compendium_to_file()
    
    def delete_category(self, category_item):
        confirm = QMessageBox.question(self, "Confirm Deletion",
            f"Are you sure you want to delete the category '{category_item.text(0)}' and all its entries?",
            QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for i in range(category_item.childCount()):
                entry_item = category_item.child(i)
                entry_name = entry_item.text(0)
                if entry_name.startswith("* "):
                    entry_name = entry_name[2:]
                if entry_name in self.compendium_data["extensions"]["entries"]:
                    del self.compendium_data["extensions"]["entries"][entry_name]
            root = self.tree.invisibleRootItem()
            root.removeChild(category_item)
            self.save_compendium_to_file()
    
    def delete_entry(self, entry_item):
        entry_name = entry_item.text(0)
        if entry_name.startswith("* "):
            entry_name = entry_name[2:]
        confirm = QMessageBox.question(self, "Confirm Deletion",
            f"Are you sure you want to delete the entry '{entry_name}'?",
            QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            if entry_name in self.compendium_data["extensions"]["entries"]:
                del self.compendium_data["extensions"]["entries"][entry_name]
            parent = entry_item.parent()
            if parent:
                parent.removeChild(entry_item)
            self.save_compendium_to_file()
            if hasattr(self, 'current_entry') and self.current_entry == entry_name:
                self.clear_entry_ui()
    
    def rename_item(self, item, item_type):
        current_text = item.text(0)
        if current_text.startswith("* ") and item_type == "entry":
            current_text = current_text[2:]
        new_text, ok = QInputDialog.getText(self, f"Rename {item_type.capitalize()}", "New name:", text=current_text)
        if ok and new_text:
            if item_type == "entry":
                old_name = current_text
                if old_name in self.compendium_data["extensions"]["entries"]:
                    self.compendium_data["extensions"]["entries"][new_text] = self.compendium_data["extensions"]["entries"][old_name]
                    del self.compendium_data["extensions"]["entries"][old_name]
                if new_text in self.compendium_data["extensions"]["entries"]:
                    item.setText(0, f"* {new_text}")
                else:
                    item.setText(0, new_text)
                if hasattr(self, 'current_entry') and self.current_entry == old_name:
                    self.current_entry = new_text
                    self.entry_name_label.setText(new_text)
            else:
                item.setText(0, new_text)
            self.save_compendium_to_file()
            if item_type == "entry":
                self.update_relation_combo()
    
    def move_item(self, item, direction):
        parent = item.parent() or self.tree.invisibleRootItem()
        index = parent.indexOfChild(item)
        if direction == "up" and index > 0:
            parent.takeChild(index)
            parent.insertChild(index - 1, item)
            self.tree.setCurrentItem(item)
        elif direction == "down" and index < parent.childCount() - 1:
            parent.takeChild(index)
            parent.insertChild(index + 1, item)
            self.tree.setCurrentItem(item)
        self.save_compendium_to_file()
    
    def move_entry(self, entry_item):
        from PyQt5.QtGui import QCursor
        menu = QMenu(self)
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            if cat_item.data(0, Qt.UserRole) == "category":
                action = menu.addAction(cat_item.text(0))
                action.setData(cat_item)
        selected_action = menu.exec_(QCursor.pos())
        if selected_action is not None:
            target_category = selected_action.data()
            if target_category is not None:
                current_parent = entry_item.parent()
                if current_parent is not None:
                    current_parent.removeChild(entry_item)
                target_category.addChild(entry_item)
                target_category.setExpanded(True)
                self.tree.setCurrentItem(entry_item)
                self.save_compendium_to_file()
    
    def on_item_changed(self, current, previous):
        if current is None:
            self.clear_entry_ui()
            return
        item_type = current.data(0, Qt.UserRole)
        if item_type == "entry":
            if previous is not None and previous.data(0, Qt.UserRole) == "entry" and self.save_button.isEnabled():
                save = QMessageBox.question(self, "Save Changes",
                    "Do you want to save changes to the current entry?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if save == QMessageBox.Yes:
                    self.save_entry(previous)
                elif save == QMessageBox.Cancel:
                    self.tree.setCurrentItem(previous)
                    return
            entry_name = current.text(0)
            if entry_name.startswith("* "):
                entry_name = entry_name[2:]
            self.load_entry(entry_name, current)
        else:
            self.clear_entry_ui()
    
    def load_entry(self, entry_name, entry_item):
        self.current_entry = entry_name
        self.current_entry_item = entry_item
        self.entry_name_label.setText(entry_name)
        self.save_button.setEnabled(False)
        content = entry_item.data(1, Qt.UserRole)
        self.editor.setPlainText(content)
        has_extended = entry_name in self.compendium_data["extensions"]["entries"]
        if has_extended:
            extended_data = self.compendium_data["extensions"]["entries"][entry_name]
            template = extended_data.get("template", "None")
            index = self.template_combo.findText(template)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)
            else:
                self.template_combo.setCurrentIndex(0)
            self.tags_list.clear()
            for tag in extended_data.get("tags", []):
                self.tags_list.addItem(tag)
            if template in self.templates:
                self.load_template_fields(template, extended_data.get("fields", {}))
            self.relationships_list.clear()
            for rel in extended_data.get("relationships", []):
                rel_item = QTreeWidgetItem(self.relationships_list, [rel.get("name", ""), rel.get("type", "")])
                self.relationships_list.addTopLevelItem(rel_item)
            self.load_images(extended_data.get("images", []))
        else:
            self.template_combo.setCurrentIndex(0)
            self.tags_list.clear()
            self.clear_template_fields()
            self.relationships_list.clear()
            self.clear_images()
    
    def clear_entry_ui(self):
        self.entry_name_label.setText("No entry selected")
        self.entry_template_label.setText("")
        self.editor.clear()
        self.template_combo.setCurrentIndex(0)
        self.tags_list.clear()
        self.clear_template_fields()
        self.relationships_list.clear()
        self.clear_images()
        self.save_button.setEnabled(False)
        if hasattr(self, 'current_entry'):
            del self.current_entry
        if hasattr(self, 'current_entry_item'):
            del self.current_entry_item
    
    def clear_template_fields(self):
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def clear_images(self):
        while self.image_layout.count():
            child = self.image_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def load_template_fields(self, template_name, field_values):
        self.clear_template_fields()
        if template_name not in self.templates:
            return
        template = self.templates[template_name]
        for field_name, field_def in template["fields"].items():
            field_group = QGroupBox(field_def["label"])
            field_layout = QVBoxLayout(field_group)
            if field_def["type"] == "text":
                field_widget = QTextEdit()
                field_widget.setPlainText(field_values.get(field_name, ""))
                field_widget.textChanged.connect(lambda: self.save_button.setEnabled(True))
            else:
                field_widget = QTextEdit()
                field_widget.setPlainText(field_values.get(field_name, ""))
                field_widget.textChanged.connect(lambda: self.save_button.setEnabled(True))
            field_widget.setProperty("field_name", field_name)
            field_layout.addWidget(field_widget)
            self.details_layout.addWidget(field_group)
        self.details_layout.addStretch()
    
    def on_template_changed(self, index):
        if not hasattr(self, 'current_entry'):
            return
        template_name = self.template_combo.currentText()
        if template_name != "None":
            self.entry_template_label.setText(f"[{template_name}]")
        else:
            self.entry_template_label.setText("")
        if self.current_entry not in self.compendium_data["extensions"]["entries"]:
            self.compendium_data["extensions"]["entries"][self.current_entry] = {}
        if template_name != "None":
            self.compendium_data["extensions"]["entries"][self.current_entry]["template"] = template_name
            if "fields" not in self.compendium_data["extensions"]["entries"][self.current_entry]:
                self.compendium_data["extensions"]["entries"][self.current_entry]["fields"] = {}
            self.load_template_fields(template_name, self.compendium_data["extensions"]["entries"][self.current_entry].get("fields", {}))
        else:
            if "template" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["template"]
            if "fields" in self.compendium_data["extensions"]["entries"][self.current_entry]:
                del self.compendium_data["extensions"]["entries"][self.current_entry]["fields"]
            self.clear_template_fields()
        self.save_button.setEnabled(True)
        self.update_entry_indicator()
    
    def find_and_select_entry(self, entry_name):
        """Search the tree and select an entry by name (ignoring the '*' prefix)."""
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                item_text = entry_item.text(0)
                if item_text.startswith("* "):
                    item_text = item_text[2:]
                if item_text == entry_name:
                    self.tree.setCurrentItem(entry_item)
                    return
