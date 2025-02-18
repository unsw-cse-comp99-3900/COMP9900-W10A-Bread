import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout,
    QToolButton, QPushButton, QLabel, QMessageBox, QMenu, QFileDialog, QInputDialog
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from project_window_core import ProjectWindow
from options import OptionsWindow  # Import the global options window

# Define the file used for storing project data.
PROJECTS_FILE = "projects.json"

def load_projects():
    """Load project data from a JSON file. If the file does not exist, return default projects."""
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.warning(None, "Load Projects", f"Error loading projects: {e}")
    # Default dummy project data.
    return [
        {"name": "My First Project", "cover": None},
        {"name": "Sci-Fi Epic", "cover": None},
        {"name": "Mystery Novel", "cover": None},
    ]

def save_projects(projects):
    """Save the project data to a JSON file."""
    try:
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=4)
    except Exception as e:
        QMessageBox.warning(None, "Save Projects", f"Error saving projects: {e}")

# Load projects at module level.
PROJECTS = load_projects()

class ProjectPostIt(QToolButton):
    """
    A custom QToolButton that displays the project cover.
    Left-click opens the project.
    Right-click shows a context menu with options.
    (This widget now displays only the cover image.)
    """
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setup_ui()
        # Set a tooltip with instructions.
        self.setToolTip("Left-click: Open project\nRight-click: Options (Delete, Export, Stats, Edit Cover)")

    def setup_ui(self):
        default_size = QSize(300, 450)
        if self.project["cover"]:
            pixmap = QPixmap(self.project["cover"])
            # Scale to default size while keeping aspect ratio.
            pixmap = pixmap.scaled(default_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Create a placeholder image of default size.
            pixmap = QPixmap(default_size)
            pixmap.fill(Qt.lightGray)
        icon = QIcon(pixmap)
        self.setIcon(icon)
        # Force a consistent icon size.
        self.setIconSize(default_size)
        self.setFixedSize(default_size)
        # Remove any text from the button so only the image shows.
        self.setText("")
        # Optional styling.
        self.setStyleSheet("QToolButton { border: 2px solid #ccc; border-radius: 5px; }")

    def contextMenuEvent(self, event):
        """Show a context menu when the user right-clicks."""
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Project")
        export_action = menu.addAction("Export Project")
        stats_action = menu.addAction("Project Statistics")
        cover_action = menu.addAction("Add Book Cover")
        action = menu.exec_(event.globalPos())
        if action == delete_action:
            confirm = QMessageBox.question(
                self, "Delete Project",
                f"Are you sure you want to delete '{self.project['name']}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    PROJECTS.remove(self.project)
                    save_projects(PROJECTS)
                    QMessageBox.information(self, "Delete Project", f"Project '{self.project['name']}' deleted.")
                    # Refresh the workbench UI by calling load_covers() on the main window.
                    workbench = self.window()
                    if hasattr(workbench, "load_covers"):
                        workbench.load_covers()
                except Exception as e:
                    QMessageBox.warning(self, "Delete Project", f"Error deleting project: {e}")
        elif action == export_action:
            QMessageBox.information(
                self, "Export Project",
                f"Export '{self.project['name']}' functionality will be implemented later."
            )
        elif action == stats_action:
            QMessageBox.information(
                self, "Project Statistics",
                f"Statistics for '{self.project['name']}' will be available in a future release."
            )
        elif action == cover_action:
            self.add_book_cover()

    def add_book_cover(self):
        """
        Open a file selection dialog to choose a new cover image.
        Updates the project cover and refreshes the icon, then saves the change persistently.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Book Cover", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.project["cover"] = file_path
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(
                    self, "Invalid Image",
                    "The selected file is not a valid image."
                )
                return
            default_size = QSize(300, 450)
            pixmap = pixmap.scaled(default_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
            self.setIcon(icon)
            self.setIconSize(default_size)
            # Persist the updated project data.
            save_projects(PROJECTS)

class ProjectCoverWidget(QWidget):
    """
    A composite widget that displays the project title above the cover.
    Uses a custom signal to notify when the cover is clicked.
    """
    # Define a custom signal that emits the project name.
    openProject = pyqtSignal(str)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        # Title label (centered)
        self.titleLabel = QLabel(self.project["name"])
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.titleLabel)
        # The cover image button
        self.coverButton = ProjectPostIt(self.project)
        # Connect the cover button's click signal to emit the custom signal.
        self.coverButton.clicked.connect(lambda: self.openProject.emit(self.project["name"]))
        layout.addWidget(self.coverButton)
        self.setLayout(layout)
        # Ensure the widget has a fixed size matching the cover (plus room for the title).
        self.setFixedSize(300, 480)  # 450 for cover, ~30 for title.

class WorkbenchWindow(QMainWindow):
    """
    The main workbench window that shows your project covers in a carousel-like view.
    Only one book cover (styled as a realistic book) is shown at a time with left/right arrow buttons.
    The cover area is fixed at 300x450 for the cover, with an extra label for the title.
    A "Settings" button opens program-wide options.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Writingway - Workbench")
        self.resize(600, 800)  # Increased height for vertical space.
        self.init_ui()

    def init_ui(self):
        # Create a central widget with a vertical layout.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header container: Title label and Settings button.
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_label = QLabel("My Projects")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Settings button with cog icon, label, and tooltip.
        settings_button = QPushButton("Settings")
        settings_button.setIcon(QIcon.fromTheme("preferences-system"))
        settings_button.setToolTip("Click here to configure global options (paths, fonts, themes, etc.)")
        settings_button.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_button)
        
        layout.addWidget(header_container)
        
        # Create a horizontal container for the carousel.
        carousel_container = QWidget()
        carousel_layout = QHBoxLayout(carousel_container)
        carousel_layout.setContentsMargins(0, 0, 0, 0)
        carousel_layout.setSpacing(10)
        
        # Left arrow button.
        self.left_button = QPushButton("<")
        self.left_button.setFixedSize(120, 120)
        self.left_button.clicked.connect(self.show_previous)
        carousel_layout.addWidget(self.left_button)
        
        # QStackedWidget for the project cover widgets.
        self.coverStack = QStackedWidget()
        # Set a fixed size for the cover widget (cover size + title label).
        self.coverStack.setFixedSize(300, 480)  # 450 for cover, ~30 for title.
        carousel_layout.addWidget(self.coverStack, stretch=1)
        
        # Right arrow button.
        self.right_button = QPushButton(">")
        self.right_button.setFixedSize(120, 120)
        self.right_button.clicked.connect(self.show_next)
        carousel_layout.addWidget(self.right_button)
        
        layout.addWidget(carousel_container)
        
        # NEW: Add a "New Project" button below the carousel.
        new_project_button = QPushButton("＋ New Project")
        new_project_button.setFixedSize(200, 50)  # Adjust size as needed.
        new_project_button.clicked.connect(self.new_project)
        layout.addWidget(new_project_button, alignment=Qt.AlignCenter)
        
        # Connect the currentChanged signal to update the cover size.
        self.coverStack.currentChanged.connect(self.updateCoverStackSize)
        
        # Load the project covers into the carousel.
        self.load_covers()

    def open_settings(self):
        """Opens the global Options window."""
        options = OptionsWindow(self)
        options.exec_()

    def updateCoverStackSize(self, index):
        """
        Force the coverStack to remain at a fixed size.
        """
        fixed_width = 300
        fixed_height = 480  # 450 for cover + 30 for title.
        self.coverStack.setFixedSize(fixed_width, fixed_height)

    def load_covers(self):
        """Load project covers (or a 'New Project' cover if none exist) into the carousel."""
        # Clear existing items.
        while self.coverStack.count():
            widget = self.coverStack.widget(0)
            self.coverStack.removeWidget(widget)
            widget.deleteLater()
        
        if PROJECTS:
            for project in PROJECTS:
                cover_widget = ProjectCoverWidget(project)
                # Connect the custom openProject signal to the open_project method.
                cover_widget.openProject.connect(self.open_project)
                self.coverStack.addWidget(cover_widget)
        else:
            # If no projects exist, show a "New Project" cover.
            new_project_btn = QToolButton()
            new_project_btn.setText("＋ New Project")
            new_project_btn.setFixedSize(300, 480)
            new_project_btn.clicked.connect(self.new_project)
            self.coverStack.addWidget(new_project_btn)
        
        # Update the stacked widget's size for the current cover.
        self.updateCoverStackSize(self.coverStack.currentIndex())

    def show_previous(self):
        """Show the previous project cover in the carousel."""
        count = self.coverStack.count()
        if count == 0:
            return
        index = self.coverStack.currentIndex()
        new_index = (index - 1) % count
        self.coverStack.setCurrentIndex(new_index)

    def show_next(self):
        """Show the next project cover in the carousel."""
        count = self.coverStack.count()
        if count == 0:
            return
        index = self.coverStack.currentIndex()
        new_index = (index + 1) % count
        self.coverStack.setCurrentIndex(new_index)

    def open_project(self, project_name):
        """Open the project view window for the given project."""
        self.project_window = ProjectWindow(project_name)
        self.project_window.show()

    def new_project(self):
        """Create a new project by prompting for its name."""
        name, ok = QInputDialog.getText(self, "New Project", "Enter new project name:")
        if ok and name.strip():
            new_project = {"name": name.strip(), "cover": None}
            PROJECTS.append(new_project)
            save_projects(PROJECTS)
            self.load_covers()
            # Automatically select the newly created project.
            self.coverStack.setCurrentIndex(len(PROJECTS) - 1)
            QMessageBox.information(self, "New Project", f"Project '{name}' created.")
        else:
            QMessageBox.information(self, "New Project", "Project creation cancelled.")

# For testing standalone.
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = WorkbenchWindow()
    window.show()
    sys.exit(app.exec_())
