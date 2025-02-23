# theme_manager.py

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
            /* General widget styling */
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            /* Input fields */
            QLineEdit, QTextEdit {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #555;
            }
            /* Buttons */
            QPushButton {
                background-color: #444;
                color: #fff;
                border: 1px solid #666;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            /* Tree Views and Widgets */
            QTreeView, QTreeWidget {
                background-color: #3c3f41;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                color: #ffffff;
                padding: 4px;
            }
            /* Tab Widget and Tab Bar */
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

        "Matrix": """
            /* Matrix-themed styling */
            QWidget {
                background-color: black;
                color: #00ff00;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QLineEdit, QTextEdit {
                background-color: black;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QPushButton {
                background-color: black;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QPushButton:hover {
                background-color: #003300;
            }
            QTreeView, QTreeWidget {
                background-color: black;
                color: #00ff00;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QHeaderView::section {
                background-color: black;
                color: #00ff00;
                padding: 4px;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: black;
                color: #00ff00;
                padding: 5px;
                font-family: "OCR A Extended", "Courier New", monospace;
            }
            QTabBar::tab:selected {
                background: #003300;
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
                color: #eee8d5;
                border: 1px solid #93a1a1;
                padding: 5px;
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

        "Cyberpunk Neon": """
            QWidget {
                background-color: #0f0f0f;
                color: #ff007f;
                font-family: "Consolas", "Monospace";
            }
            QLineEdit, QTextEdit {
                background-color: #1a1a1a;
                color: #00ffff;
                border: 1px solid #ff007f;
            }
            QPushButton {
                background-color: #222;
                color: #ff007f;
                border: 1px solid #00ffff;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QTreeView, QTreeWidget {
                background-color: #0f0f0f;
                color: #ff007f;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #00ffff;
                padding: 4px;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #ff007f;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #00ffff;
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
                border: 1px solid #aaa;
                padding: 5px;
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
                border: 1px solid #0288d1;
                padding: 5px;
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
                border: 1px solid #a67c52;
                padding: 5px;
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

        This assumes that a QApplication instance has already been created.
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
