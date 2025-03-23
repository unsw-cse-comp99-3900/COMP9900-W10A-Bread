#!/usr/bin/env python3
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import Qt
from . import tree_manager

def add_act(window):
    text, ok = QInputDialog.getText(window, "Add Act", "Enter act name:")
    if ok and text.strip():
        new_act = {
            "name": text.strip(),
            "summary": f"This is the summary for {text.strip()}.",
            "chapters": []
        }
        window.model.structure.setdefault("acts", []).append(new_act)
        tree_manager.populate_tree(window.project_tree.tree, window.model.structure)
        tree_manager.save_structure(window.model.project_name, window.model.structure)


def add_chapter(window, act_item):
    text, ok = QInputDialog.getText(
        window, "Add Chapter", "Enter chapter name:")
    if ok and text.strip():
        new_chapter = {
            "name": text.strip(),
            "summary": f"This is the summary for {text.strip()}.",
            "scenes": []
        }

        # Get the act name from the act_item
        act_name = act_item.text(0)

        # Find the corresponding act in the in-memory structure and append the new chapter.
        for act in window.model.structure.get("acts", []):
            if act.get("name") == act_name:
                act.setdefault("chapters", []).append(new_chapter)
                break

        # Refresh the tree using the updated structure.
        tree_manager.populate_tree(window.project_tree.tree, window.model.structure)
        tree_manager.save_structure(window.model.project_name, window.model.structure)
        window.model.unsaved_changes = False # Reset unsaved changes flag after adding a chapter


def add_scene(window, chapter_item):
    text, ok = QInputDialog.getText(window, "Add Scene", "Enter scene name:")
    if ok and text.strip():
        new_scene = {
            "name": text.strip(),
            "content": f"This is the scene content for {text.strip()}."
        }

        # Get the chapter name and its parent act's name.
        chapter_name = chapter_item.text(0)
        act_item = chapter_item.parent()
        act_name = act_item.text(0)

        # Find the corresponding act and chapter in the in-memory structure.
        for act in window.model.structure.get("acts", []):
            if act.get("name") == act_name:
                for chapter in act.get("chapters", []):
                    if chapter.get("name") == chapter_name:
                        chapter.setdefault("scenes", []).append(new_scene)
                        break
                break

        # Refresh the tree using the updated structure.
        tree_manager.populate_tree(window.project_tree.tree, window.model.structure)
        tree_manager.save_structure(window.model.project_name, window.model.structure)
        window.model.unsaved_changes = False # Reset unsaved changes flag after adding a scene


def rename_item(window, item):
    current_name = item.text(0)
    new_name, ok = QInputDialog.getText(
        window, "Rename", "Enter new name:", text=current_name)
    if ok and new_name.strip():
        new_name = new_name.strip()
        item.setText(0, new_name)
        data = item.data(0, Qt.UserRole)
        if isinstance(data, dict):
            data["name"] = new_name
        else:
            data = {"name": new_name}
        item.setData(0, Qt.UserRole, data)
        # Update the structure from the tree to sync changes
        tree_manager.update_structure_from_tree(window.project_tree.tree, window.model.project_name)


def move_item_up(window, item):
    parent = item.parent() or window.project_tree.tree.invisibleRootItem()
    index = parent.indexOfChild(item)
    if index > 0:
        parent.takeChild(index)
        parent.insertChild(index - 1, item)
        window.project_tree.tree.setCurrentItem(item)
        tree_manager.update_structure_from_tree(window.project_tree.tree, window.model.project_name)


def move_item_down(window, item):
    parent = item.parent() or window.project_tree.tree.invisibleRootItem()
    index = parent.indexOfChild(item)
    if index < parent.childCount() - 1:
        parent.takeChild(index)
        parent.insertChild(index + 1, item)
        window.project_tree.tree.setCurrentItem(item)
        tree_manager.update_structure_from_tree(window.project_tree.tree, window.model.project_name)
