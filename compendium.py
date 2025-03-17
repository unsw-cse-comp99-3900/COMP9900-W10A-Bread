# compendium.py
from PyQt5.QtWidgets import QMainWindow
from compendium_panel import CompendiumPanel

class CompendiumWindow(QMainWindow):
    def __init__(self, project_name, parent=None):
        super().__init__(parent)
        self.project_name = project_name
        self.setWindowTitle(f"Compendium - {project_name}")
        self.resize(500, 600)
        # Pass self as parent so that CompendiumPanel can access project_name
        self.compendium_panel = CompendiumPanel(self)
        self.setCentralWidget(self.compendium_panel)
