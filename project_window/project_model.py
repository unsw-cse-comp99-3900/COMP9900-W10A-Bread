#!/usr/bin/env python3
import os
from PyQt5.QtCore import pyqtSignal, QObject
from . import project_settings_manager as psm
from settings.settings_manager import WWSettingsManager
from settings.autosave_manager import load_latest_autosave, save_scene, get_latest_autosave_path
from .tree_manager import load_structure, save_structure, update_structure_from_tree, get_structure_file_path

class ProjectModel(QObject):
    """Manages project data and persistence."""
    structureChanged = pyqtSignal(list)

    def __init__(self, project_name):
        super().__init__()
        self.project_name = project_name
        self.structure = load_structure(project_name)
        self.migrate_legacy_content()
        self.settings = self.load_settings()
        self.autosave_enabled = WWSettingsManager.get_setting("general", "enable_autosave", False)
        self.unsaved_changes = False
        self.last_saved_hierarchy = None

    def load_settings(self):
        """Load project settings with defaults."""
        settings = psm.load_project_settings(self.project_name)
        return {
            "global_pov": settings.get("global_pov", "Third Person Limited"),
            "global_pov_character": settings.get("global_pov_character", "Character"),
            "global_tense": settings.get("global_tense", "Present Tense")
        }

    def save_settings(self):
        """Save current settings to file."""
        psm.save_project_settings(self.project_name, self.settings)

    def update_structure(self, tree):
        """Update project structure from the tree widget."""
        self.structure = update_structure_from_tree(tree, self.project_name)
        self.save_structure()

    def save_structure(self):
        """Persist the project structure."""
        save_structure(self.project_name, self.structure)

    def load_autosave(self, hierarchy):
        """Load the latest autosave for a given hierarchy."""
        return load_latest_autosave(self.project_name, hierarchy)

    def migrate_legacy_content(self):
        """Migrate 'content' from structure.json to HTML files on startup."""
        def traverse_and_migrate(node, hierarchy):
            if "content" in node:
                latest_autosave_path = get_latest_autosave_path(self.project_name, hierarchy)

                if not latest_autosave_path:
                    # Migrate content to HTML
                    filepath = save_scene(self.project_name, hierarchy, node["content"])
                    if filepath:
                        del node["content"]
                else:
                    # HTML is newer; just remove content from structure
                    del node["content"]
            if "chapters" in node:
                for i, chapter in enumerate(node["chapters"]):
                    traverse_and_migrate(chapter, hierarchy + [chapter["name"]])
            if "scenes" in node:
                for i, scene in enumerate(node["scenes"]):
                    traverse_and_migrate(scene, hierarchy + [scene["name"]])

        # Backup original structure.json
        file_path = get_structure_file_path(self.project_name)
        backup_path = file_path + ".backup"
        if os.path.exists(file_path) and not os.path.exists(backup_path):
            os.rename(file_path, backup_path)

        # Perform migration
        for act in self.structure.get("acts", []):
            traverse_and_migrate(act, [act["name"]])

        # Save updated structure
        if os.path.exists(backup_path):
            self.save_structure()
            os.remove(backup_path)  # Remove backup if successful

    def load_scene_content(self, hierarchy):
        """Load content, prioritizing HTML, falling back to structure (for legacy)."""
        content = load_latest_autosave(self.project_name, hierarchy)
        if content is None:
            node = self._get_node_by_hierarchy(hierarchy)
            content = node.get("content") if node else None
            if content:  # Legacy content found, migrate it
                filepath = save_scene(self.project_name, hierarchy, content)
                if filepath and "content" in node:
                    del node["content"]
                    self.save_structure()
                    self.structureChanged.emit(hierarchy)
        return content

    def save_scene(self, hierarchy, content):
        """Save scene to HTML and remove content from structure."""
        filepath = save_scene(self.project_name, hierarchy, content)
        if filepath:
            node = self._get_node_by_hierarchy(hierarchy)
            if node and "content" in node:
                del node["content"]
            self.save_structure()
            self.structureChanged.emit(hierarchy)
        return filepath
    
    def save_summary(self, hierarchy, summary_text):
        """
        Save the summary to a file and update the structure with the filepath.
        
        Args:
            hierarchy (list): The hierarchy path to the act or chapter (e.g., ["Act 1", "Chapter 1"]).
            summary_text (str): The summary content to save.
        
        Returns:
            str: The filepath where the summary was saved, or None if failed.
        """
        
        node = self._get_node_by_hierarchy(hierarchy)
        if not node:
            return None

        # Generate a unique filename for the summary
        sanitized_project_name = WWSettingsManager.sanitize(self.project_name)
        sanitized_hierarchy = "-".join(WWSettingsManager.sanitize(h) for h in hierarchy)
        filename = f"{sanitized_project_name}-Summary-{sanitized_hierarchy}.html"
        filepath = WWSettingsManager.get_project_relpath(self.project_name, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(summary_text)
            # Update the structure to reference the file instead of storing the text
            if "summary" in node and not isinstance(node["summary"], str):  # Clean up old file if exists
                try:
                    os.remove(node["summary"])
                except OSError:
                    pass
            node["summary"] = filepath  # Store the filepath
            self.save_structure()
            self.last_saved_hierarchy = hierarchy
            self.structureChanged.emit(hierarchy)
            return filepath
        except Exception as e:
            print(f"Error saving summary to {filepath}: {e}")
            return None

    def load_summary(self, hierarchy):
        """
        Load the summary content from its file, if it exists.
        
        Args:
            hierarchy (list): The hierarchy path to the act or chapter.
        
        Returns:
            str: The summary content, or None if not found or failed to load.
        """
        node = self._get_node_by_hierarchy(hierarchy)
        if node and "summary" in node:
            summary_ref = node["summary"]
            if isinstance(summary_ref, str) and os.path.exists(summary_ref):  # It’s a filepath
                try:
                    with open(summary_ref, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error loading summary from {summary_ref}: {e}")
                    return None
            return summary_ref  # Legacy case: return text if not a filepath
        return None
    
    def add_act(self, act_name):
        new_act = {"name": act_name, "summary": f"This is the summary for {act_name}.", "chapters": []}
        self.structure.setdefault("acts", []).append(new_act)
        self.save_structure()
        self.structureChanged.emit([act_name])

    def add_chapter(self, act_name, chapter_name):
        new_chapter = {"name": chapter_name, "summary": f"This is the summary for {chapter_name}.", "scenes": []}
        for act in self.structure.get("acts", []):
            if act.get("name") == act_name:
                act.setdefault("chapters", []).append(new_chapter)
                self.save_structure()
                self.structureChanged.emit([act_name, chapter_name])
                break

    def add_scene(self, act_name, chapter_name, scene_name):
        new_scene = {"name": scene_name}
        for act in self.structure.get("acts", []):
            if act.get("name") == act_name:
                for chapter in act.get("chapters", []):
                    if chapter.get("name") == chapter_name:
                        chapter.setdefault("scenes", []).append(new_scene)
                        self.save_structure()
                        self.structureChanged.emit([act_name, chapter_name, scene_name])
                        break
                break

    def rename_node(self, hierarchy, new_name):
        node = self._get_node_by_hierarchy(hierarchy)
        if node:
            node["name"] = new_name
            self.save_structure()
            self.structureChanged.emit(hierarchy)

    def delete_node(self, hierarchy):
        parent, index = self._get_parent_and_index(hierarchy)
        if parent and index is not None:
            parent.pop(index)
            self.save_structure()
            self.structureChanged.emit(hierarchy)

    def save_scene(self, hierarchy, content):
        filepath = save_scene(self.project_name, hierarchy, content)
        if filepath:
            node = self._get_node_by_hierarchy(hierarchy)
            if node and "content" in node:
                del node["content"]  # Remove content from structure
            self.save_structure()
            self.structureChanged.emit(hierarchy)
        return filepath

    def _get_node_by_hierarchy(self, hierarchy):
        current = self.structure.get("acts", [])
        for level, name in enumerate(hierarchy):
            for item in current:
                if item.get("name") == name:
                    if level == len(hierarchy) - 1:
                        return item
                    current = item.get("chapters" if level == 0 else "scenes", [])
                    break
        return None

    def _get_parent_and_index(self, hierarchy):
        current = self.structure.get("acts", [])
        parent = None
        for level, name in enumerate(hierarchy[:-1]):
            for item in current:
                if item.get("name") == name:
                    parent = current
                    current = item.get("chapters" if level == 0 else "scenes", [])
                    break
        for i, item in enumerate(current):
            if item.get("name") == hierarchy[-1]:
                return current, i
        return None, None