#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication


class ThemeManager:
    """
    A simple manager for predefined themes.

    Provides methods to:
      - List available themes.
      - Retrieve a stylesheet for a given theme.
      - Apply a theme to a specific widget or the entire application.
    """

    THEMES = {
        "Standard": "",  # Default styling; no custom stylesheet.
        "Night Mode": """
            /* Night Mode styling */
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #333;
                color: #ffffff;
                border: 2px solid #ffffff;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QTreeView, QTreeWidget {
                background-color: #3c3f41;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                color: #ffffff;
                padding: 4px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #3c3f41;
                color: #ffffff;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #555;
            }
        """,
        "Solarized Dark": """
            QWidget {
                background-color: #002b36;
                color: #839496;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #073642;
                color: #93a1a1;
                border: 1px solid #586e75;
            }
            QPushButton {
                background-color: #586e75;
                color: #fdf6e3;
                border: 2px solid #fdf6e3;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #657b83;
            }
            QTreeView, QTreeWidget {
                background-color: #073642;
                color: #839496;
            }
            QHeaderView::section {
                background-color: #073642;
                color: #93a1a1;
                padding: 4px;
            }
            QTabBar::tab {
                background: #073642;
                color: #839496;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #586e75;
            }
        """,
        "Paper White": """
            QWidget {
                background-color: #f9f9f9;
                color: #333;
                font-family: "Georgia", serif;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                color: #000;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #f1f1f1;
                color: #333;
                border: 2px solid #333;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e1e1e1;
            }
            QTreeView, QTreeWidget {
                background-color: #f9f9f9;
                color: #333;
            }
            QHeaderView::section {
                background-color: #e1e1e1;
                color: #333;
                padding: 4px;
            }
            QTabBar::tab {
                background: #f1f1f1;
                color: #333;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #ddd;
            }
        """,
        "Ocean Breeze": """
            QWidget {
                background-color: #e0f7fa;
                color: #0277bd;
                font-family: "Verdana", sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #b2ebf2;
                color: #004d40;
                border: 1px solid #0288d1;
            }
            QPushButton {
                background-color: #4dd0e1;
                color: #004d40;
                border: 2px solid #004d40;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #26c6da;
            }
            QTreeView, QTreeWidget {
                background-color: #b2ebf2;
                color: #004d40;
            }
            QHeaderView::section {
                background-color: #4dd0e1;
                color: #004d40;
                padding: 4px;
            }
            QTabBar::tab {
                background: #b2ebf2;
                color: #0277bd;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #4dd0e1;
            }
        """,
        "Sepia": """
            QWidget {
                background-color: #f4ecd8;
                color: #5a4630;
                font-family: "Times New Roman", serif;
            }
            QLineEdit, QTextEdit {
                background-color: #f8f1e4;
                color: #3a2c1f;
                border: 1px solid #a67c52;
            }
            QPushButton {
                background-color: #d8c3a5;
                color: #3a2c1f;
                border: 2px solid #3a2c1f;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c4a484;
            }
            QTreeView, QTreeWidget {
                background-color: #f4ecd8;
                color: #5a4630;
            }
            QHeaderView::section {
                background-color: #d8c3a5;
                color: #5a4630;
                padding: 4px;
            }
            QTabBar::tab {
                background: #d8c3a5;
                color: #5a4630;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #c4a484;
            }
        """
    }

    ICON_TINTS = {
        "Standard": "black",
        "Paper White": "black",
        "Ocean Breeze": "black",
        "Sepia": "black",
        "Night Mode": "white",
        "Solarized Dark": "#fdf6e3",
    }

    @classmethod
    def list_themes(cls):
        """
        Return a list of available theme names.
        """
        return list(cls.THEMES.keys())

    @classmethod
    def get_stylesheet(cls, theme_name):
        """
        Retrieve the stylesheet string for a given theme name.
        """
        return cls.THEMES.get(theme_name, "")

    @classmethod
    def apply_theme(cls, widget, theme_name):
        """
        Apply the stylesheet of the specified theme to the given widget.
        """
        stylesheet = cls.get_stylesheet(theme_name)
        widget.setStyleSheet(stylesheet)

    @classmethod
    def apply_to_app(cls, theme_name):
        """
        Apply the theme to the entire application.
        """
        stylesheet = cls.get_stylesheet(theme_name)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
        else:
            raise RuntimeError(
                "No QApplication instance found. Create one before applying a theme.")


if __name__ == '__main__':
    print("Available themes:")
    for theme in ThemeManager.list_themes():
        print(f" - {theme}")
