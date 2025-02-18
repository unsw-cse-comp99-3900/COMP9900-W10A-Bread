#!/usr/bin/env python3
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import Qt
from tree_manager import save_structure, populate_tree, update_structure_from_tree

def add_act(window):
    text, ok = QInputDialog.getText(window, "Add Act", "Enter act name:")
    if ok and text.strip():
        new_act = {
            "name": text.strip(),
            "summary": f"This is the summary for {text.strip()}.",
            "chapters": []
        }
        window.structure.setdefault("acts", []).append(new_act)
        populate_tree(window.tree, window.structure)
        save_structure(window.project_name, window.structure)

def add_chapter(window, act_item):
    text, ok = QInputDialog.getText(window, "Add Chapter", "Enter chapter name:")
    if ok and text.strip():
        act_data = act_item.data(0, Qt.UserRole)
        if not isinstance(act_data, dict):
            act_data = {"name": act_item.text(0)}
        new_chapter = {
            "name": text.strip(),
            "summary": f"This is the summary for {text.strip()}.",
            "scenes": []
        }
        act_data.setdefault("chapters", []).append(new_chapter)
        act_item.setData(0, Qt.UserRole, act_data)
        populate_tree(window.tree, window.structure)
        save_structure(window.project_name, window.structure)

def add_scene(window, chapter_item):
    text, ok = QInputDialog.getText(window, "Add Scene", "Enter scene name:")
    if ok and text.strip():
        chapter_data = chapter_item.data(0, Qt.UserRole)
        if not isinstance(chapter_data, dict):
            chapter_data = {"name": chapter_item.text(0)}
        new_scene = {
            "name": text.strip(),
            "content": f"This is the scene content for {text.strip()}."
        }
        chapter_data.setdefault("scenes", []).append(new_scene)
        chapter_item.setData(0, Qt.UserRole, chapter_data)
        populate_tree(window.tree, window.structure)
        save_structure(window.project_name, window.structure)

def rename_item(window, item):
    current_name = item.text(0)
    new_name, ok = QInputDialog.getText(window, "Rename", "Enter new name:", text=current_name)
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
        update_structure_from_tree(window.tree, window.project_name)

def move_item_up(window, item):
    parent = item.parent() or window.tree.invisibleRootItem()
    index = parent.indexOfChild(item)
    if index > 0:
        parent.takeChild(index)
        parent.insertChild(index - 1, item)
        window.tree.setCurrentItem(item)
        update_structure_from_tree(window.tree, window.project_name)

def move_item_down(window, item):
    parent = item.parent() or window.tree.invisibleRootItem()
    index = parent.indexOfChild(item)
    if index < parent.childCount() - 1:
        parent.takeChild(index)
        parent.insertChild(index + 1, item)
        window.tree.setCurrentItem(item)
        update_structure_from_tree(window.tree, window.project_name)
