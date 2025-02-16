import sys
import json
import os
from PyQt5.QtWidgets import QApplication
from workbench import WorkbenchWindow
from theme_manager import ThemeManager

SETTINGS_FILE = "settings.json"

def load_theme():
    """Load the saved theme from settings.json, defaulting to 'Standard'."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            return settings.get("theme", "Standard")
        except Exception as e:
            print("Error loading theme from settings:", e)
    return "Standard"

def main():
    app = QApplication(sys.argv)
    
    # Load and apply the saved theme to the application
    theme = load_theme()
    try:
        ThemeManager.apply_to_app(theme)
    except Exception as e:
        print("Error applying theme:", e)
    
    window = WorkbenchWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
