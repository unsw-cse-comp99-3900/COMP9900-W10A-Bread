#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from . import tree_manager
from . import project_structure_manager as psm

class ProjectTreeWidget(QWidget):
    """Left panel with the project structure tree."""
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.tree = QTreeWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree.setHeaderLabels(["Name", "Status"])
        self.tree.setColumnCount(2)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.currentItemChanged.connect(self.controller.tree_item_changed)
        self.tree.itemSelectionChanged.connect(self.controller.tree_item_selection_changed)
        self.populate()

    def populate(self):
        """Populate the tree with the project structure."""
        tree_manager.populate_tree(self.tree, self.model.structure)
        self.assign_tree_icons()

    def assign_tree_icons(self):
        """Assign icons to tree items based on level and status."""
        def set_icon_recursively(item):
            level = self.get_item_level(item)
            tint = self.controller.icon_tint
            if level < 2:
                item.setIcon(0, self.controller.get_tinted_icon("assets/icons/book.svg", tint))
                item.setText(1, "")
            else:
                scene_data = item.data(0, Qt.UserRole) or {"name": item.text(0), "status": "To Do"}
                item.setData(0, Qt.UserRole, scene_data)
                item.setIcon(0, self.controller.get_tinted_icon("assets/icons/edit.svg", tint))
                self.update_scene_status_icon(item)
            for i in range(item.childCount()):
                set_icon_recursively(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            set_icon_recursively(self.tree.topLevelItem(i))

    def update_scene_status_icon(self, item):
        """Update the status icon for a scene item."""
        tint = self.controller.icon_tint
        status = item.data(0, Qt.UserRole).get("status", "To Do")
        icons = {
            "To Do": "assets/icons/circle.svg",
            "In Progress": "assets/icons/loader.svg",
            "Final Draft": "assets/icons/check-circle.svg"
        }
        item.setIcon(1, self.controller.get_tinted_icon(icons.get(status, ""), tint) if status in icons else QIcon())
        item.setText(1, "")

    def get_item_level(self, item):
        """Calculate the level of an item in the tree."""
        level = 0
        temp = item
        while temp.parent():
            level += 1
            temp = temp.parent()
        return level

    def show_context_menu(self, pos):
        """Display context menu for tree items."""
        item = self.tree.itemAt(pos)
        menu = QMenu()
        if not item:
            menu.addAction("Add Act", lambda: psm.add_act(self.controller))
        else:
            menu.addAction("Rename", lambda: psm.rename_item(self.controller, item))
            menu.addAction("Delete", lambda: tree_manager.delete_node(self.tree, item, self.model.project_name))
            menu.addAction("Move Up", lambda: psm.move_item_up(self.controller, item))
            menu.addAction("Move Down", lambda: psm.move_item_down(self.controller, item))
            level = self.get_item_level(item)
            if level == 0:
                menu.addAction("Add Chapter", lambda: psm.add_chapter(self.controller, item))
            elif level == 1:
                menu.addAction("Add Scene", lambda: psm.add_scene(self.controller, item))
            if level >= 2:
                status_menu = menu.addMenu("Set Scene Status")
                for status in ["To Do", "In Progress", "Final Draft"]:
                    status_menu.addAction(status, lambda s=status: self.controller.set_scene_status(item, s))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))
