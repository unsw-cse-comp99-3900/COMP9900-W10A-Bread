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
            raise RuntimeError("No QApplication instance found. Create one before applying a theme.")

if __name__ == '__main__':
    print("Available themes:")
    for theme in ThemeManager.list_themes():
        print(f" - {theme}")
