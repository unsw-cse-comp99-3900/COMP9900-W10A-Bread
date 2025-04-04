from PyQt5.QtWidgets import QWidget, QSplitter, QTreeWidget, QTextEdit, QVBoxLayout, QMenu, QTreeWidgetItem, QMessageBox, QDialog
from PyQt5.QtCore import Qt, QPoint
import json, os, re
from langchain.prompts import PromptTemplate

from .enhanced_compendium import EnhancedCompendiumWindow
from .ai_compendium_dialog import AICompendiumDialog
from settings.llm_api_aggregator import WWApiAggregator
from settings.settings_manager import WWSettingsManager
from settings.llm_settings_dialog import LLMSettingsDialog

DEBUG = False  # Set to True to enable debug prints

def sanitize(text):
    return re.sub(r'\W+', '', text)

class CompendiumPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.project_window = parent

        # Determine the project name from the parent window and set the compendium file path.
        self.project_name = getattr(self.parent().model, "project_name", "default")
        self.new_compendium_file = os.path.join(os.getcwd(), "Projects", sanitize(self.project_name), "compendium.json")
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
        action_analyze = menu.addAction("Analyze Scene with AI")
        action = menu.exec_(self.tree.viewport().mapToGlobal(pos))

        if action == action_open:
            self.open_in_enhanced_compendium()
        elif action == action_analyze:
            self.analyze_scene_with_ai()

    def open_in_enhanced_compendium(self):
        """Launch the enhanced compendium window.
        If an entry is selected, the enhanced window will jump to that entry."""
        self.enhanced_window = EnhancedCompendiumWindow(self.project_name, self.parent())
        self.enhanced_window.show()
        # If an entry is selected, try to select it in the enhanced window.
        current_item = self.tree.currentItem()
        if current_item and current_item.data(0, Qt.UserRole) == "entry":
            entry_name = current_item.text(0)
            if entry_name.startswith("* "):
                entry_name = entry_name[2:]
            self.enhanced_window.find_and_select_entry(entry_name)

    def analyze_scene_with_ai(self):
        """Analyze current scene content and compendium using AI and show results."""
        # Get the scene editor content from the parent window
        scene_editor = self.project_window.scene_editor.editor
        if not scene_editor or not scene_editor.toPlainText():
            QMessageBox.warning(self, "Warning", "No scene content available to analyze.")
            return

        scene_content = scene_editor.toPlainText()
        
        # Get existing compendium data
        current_compendium = {}
        if os.path.exists(self.compendium_file):
            try:
                with open(self.compendium_file, "r", encoding="utf-8") as f:
                    current_compendium = json.load(f)
            except Exception as e:
                print(f"Error loading compendium: {e}")

        overrides = LLMSettingsDialog.show_dialog(
            self,
            default_provider=WWSettingsManager.get_active_llm_name(),
            default_model=None,  # Could fetch from settings if desired
            default_timeout=60
        )
        if not overrides:
            return  # User canceled

        # Define the PromptTemplate
        analysis_template = PromptTemplate(
            input_variables=["scene_content", "existing_compendium"],
            template="""Analyze the following scene content and existing compendium data. 
Generate or update compendium entries in JSON format for:
1. Major and minor characters (name, personality, description, relationships)
2. Locations (name, description)
3. Key objects (name, description)
4. Significant plot items (name, description)

Compendium entries apply to the entire story, so do not update existing entries for current status.

Scene Content:
{scene_content}

Existing Compendium:
{existing_compendium}

Return only the JSON result without additional commentary. The JSON should maintain the structure:
{{
  "categories": [
    {{
      "name": "category_name",
      "entries": [
        {{
          "name": "entry_name",
          "content": "description and details",
          "relationships": [{{"name": "related_entry", "type": "relationship_type"}}] (optional)
        }}
      ]
    }}
  ]
}}
"""
        )

        # Format the prompt using the template
        prompt = analysis_template.format(
            scene_content=scene_content,
            existing_compendium=json.dumps(current_compendium, indent=2)
        )

        try:
            # Use WWApiAggregator to get AI response
            response = WWApiAggregator.send_prompt_to_llm(prompt, overrides=overrides)
            
            # Preprocess to remove Markdown markers
            cleaned_response = self.preprocess_json_string(response)

            # Attempt to repair incomplete JSON
            repaired_response = self.repair_incomplete_json(cleaned_response)
            if repaired_response is None:
                QMessageBox.warning(self, "Error", "AI returned invalid JSON that could not be repaired.")
                return
            
            # Validate JSON response
            try:
                ai_compendium = json.loads(repaired_response)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "AI returned invalid JSON format.")
                return

            # Show the dialog with AI results
            dialog = AICompendiumDialog(ai_compendium, self.compendium_file, self)
            if dialog.exec_() == QDialog.Accepted:
                self.save_ai_analysis(dialog.get_compendium_data())

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to analyze scene: {str(e)}")

    def preprocess_json_string(self, raw_string):
        """Remove Markdown code block markers and extraneous whitespace from the string."""
        # Remove ```json (with optional language specifier) and ``` markers
        cleaned = re.sub(r'^```(?:json)?\s*\n', '', raw_string, flags=re.MULTILINE)
        cleaned = re.sub(r'\n```$', '', cleaned, flags=re.MULTILINE)
        # Remove leading/trailing whitespace
        return cleaned.strip()
    
    def repair_incomplete_json(self, json_str):
        """Attempt to repair incomplete JSON by adding missing closing brackets."""
        try:
            json.loads(json_str)  # If it parses, no repair needed
            return json_str
        except json.JSONDecodeError:
            # Add missing closing characters step-by-step
            repaired = json_str.strip()
            if repaired.endswith('"'):  # Ends with an open string
                repaired += '"'
            # Count and balance brackets
            open_braces = repaired.count('{') - repaired.count('}')
            open_brackets = repaired.count('[') - repaired.count(']')
            
            # Add missing closing braces and brackets
            for _ in range(open_braces):
                repaired += '}'
            for _ in range(open_brackets):
                repaired += ']'
            
            try:
                json.loads(repaired)
                return repaired
            except json.JSONDecodeError:
                return None  # If still invalid, return None

    def save_ai_analysis(self, ai_compendium):
        """Save the AI-generated compendium analysis to the file."""
        try:
            # Merge with existing compendium if it exists
            if os.path.exists(self.compendium_file):
                with open(self.compendium_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                
                # Simple merge strategy: append new categories
                existing_categories = {cat["name"]: cat for cat in existing.get("categories", [])}
                for new_cat in ai_compendium.get("categories", []):
                    if new_cat["name"] in existing_categories:
                        # For existing categories, merge entries
                        existing_entries = {entry["name"]: entry for entry in existing_categories[new_cat["name"]]["entries"]}
                        for new_entry in new_cat["entries"]:
                            existing_entries[new_entry["name"]] = new_entry
                        existing_categories[new_cat["name"]]["entries"] = list(existing_entries.values())
                    else:
                        # Add new category
                        existing["categories"].append(new_cat)
            else:
                existing = ai_compendium

            # Save the merged compendium
            with open(self.compendium_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            
            # Refresh the tree view
            self.populate_compendium()
            
            QMessageBox.information(self, "Success", "Compendium updated successfully.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save compendium: {str(e)}")