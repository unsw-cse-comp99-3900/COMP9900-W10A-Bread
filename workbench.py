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
            QMessageBox.warning(None, "Load Projects",
                                f"Error loading projects: {e}")
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
        QMessageBox.warning(None, "Save Projects",
                            f"Error saving projects: {e}")


# Load projects at module level.
PROJECTS = load_projects()


class ProjectPostIt(QToolButton):
    """
    A custom QToolButton that displays the project cover.
    Left-click opens the project.
    Right-click shows a context menu with options.
    """

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setup_ui()
        self.setToolTip(
            "Left-click: Open project\nRight-click: Options (Delete, Export, Stats, Edit Cover)")

    def setup_ui(self):
        default_size = QSize(300, 450)
        if self.project["cover"]:
            pixmap = QPixmap(self.project["cover"])
            pixmap = pixmap.scaled(
                default_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap(default_size)
            pixmap.fill(Qt.lightGray)
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(default_size)
        self.setFixedSize(default_size)
        self.setText("")
        self.setStyleSheet("QToolButton { margin: 0px; padding: 0px; }")

    def contextMenuEvent(self, event):
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
                    QMessageBox.information(
                        self, "Delete Project", f"Project '{self.project['name']}' deleted.")
                    workbench = self.window()
                    if hasattr(workbench, "load_covers"):
                        workbench.load_covers()
                except Exception as e:
                    QMessageBox.warning(
                        self, "Delete Project", f"Error deleting project: {e}")
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Book Cover", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.project["cover"] = file_path
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Invalid Image",
                                    "The selected file is not a valid image.")
                return
            default_size = QSize(300, 450)
            pixmap = pixmap.scaled(
                default_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
            self.setIcon(icon)
            self.setIconSize(default_size)
            save_projects(PROJECTS)


class ProjectCoverWidget(QWidget):
    """
    A composite widget that displays the project title above the cover.
    """
    openProject = pyqtSignal(str)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.titleLabel = QLabel(self.project["name"])
        self.titleLabel.setObjectName("projectTitleLabel")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titleLabel)
        self.coverButton = ProjectPostIt(self.project)
        self.coverButton.clicked.connect(
            lambda: self.openProject.emit(self.project["name"]))
        layout.addWidget(self.coverButton)
        self.setLayout(layout)
        self.setFixedSize(300, 480)


class WorkbenchWindow(QMainWindow):
    """
    The main workbench window that shows your project covers in a carousel-like view.
    """

    def __init__(self):
        super().__init__()
        # Removed global stylesheet propagation prevention.
        self.setWindowTitle("Writingway - Workbench")
        self.resize(640, 720)
        self.init_ui()
        self.apply_fixed_stylesheet()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_label = QLabel("My Projects")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        settings_button = QPushButton("")
        cog_icon_path = os.path.join("assets", "icons", "settings.svg")
        settings_button.setIcon(QIcon(cog_icon_path))
        settings_button.setToolTip(
            "Click here to configure global options (paths, fonts, themes, etc.)")
        settings_button.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_button)
        layout.addWidget(header_container)

        carousel_container = QWidget()
        carousel_layout = QHBoxLayout(carousel_container)
        carousel_layout.setContentsMargins(0, 0, 0, 0)
        carousel_layout.setSpacing(10)

        self.left_button = QPushButton("")
        left_arrow_icon = QIcon(os.path.join(
            "assets", "icons", "chevron-left.svg"))
        self.left_button.setIcon(left_arrow_icon)
        self.left_button.setIconSize(QSize(32, 32))
        self.left_button.setFixedSize(60, 60)
        self.left_button.setToolTip("Previous Project")
        self.left_button.clicked.connect(self.show_previous)
        carousel_layout.addWidget(self.left_button)

        self.coverStack = QStackedWidget()
        self.coverStack.setFixedSize(300, 480)
        carousel_layout.addWidget(self.coverStack, stretch=1)

        self.right_button = QPushButton("")
        right_arrow_icon = QIcon(os.path.join(
            "assets", "icons", "chevron-right.svg"))
        self.right_button.setIcon(right_arrow_icon)
        self.right_button.setIconSize(QSize(32, 32))
        self.right_button.setFixedSize(60, 60)
        self.right_button.setToolTip("Next Project")
        self.right_button.clicked.connect(self.show_next)
        carousel_layout.addWidget(self.right_button)
        layout.addWidget(carousel_container)

        new_project_button = QPushButton("＋ New Project")
        new_project_button.setObjectName("newProjectButton")
        new_project_button.setFixedSize(200, 50)
        new_project_button.setToolTip("Create a brand-new project")
        new_project_button.clicked.connect(self.new_project)
        layout.addWidget(new_project_button, alignment=Qt.AlignCenter)

        self.coverStack.currentChanged.connect(self.updateCoverStackSize)
        self.load_covers()

    def apply_fixed_stylesheet(self):
        fixed_styles = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel#headerLabel {
                font-size: 22px;
                font-weight: 600;
                color: #333;
            }
            QLabel#projectTitleLabel {
                font-size: 14px;
                font-weight: 500;
                color: #333;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
            }
            QPushButton#newProjectButton {
                font-size: 16px;
                font-weight: bold;
            }
            QToolButton {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            QToolButton:hover {
                background-color: #f0f0f0;
            }
        """
        self.setStyleSheet(fixed_styles)

    def open_settings(self):
        options = OptionsWindow(self)
        options.exec_()

    def updateCoverStackSize(self, index):
        fixed_width = 300
        fixed_height = 480
        self.coverStack.setFixedSize(fixed_width, fixed_height)

    def load_covers(self):
        while self.coverStack.count():
            widget = self.coverStack.widget(0)
            self.coverStack.removeWidget(widget)
            widget.deleteLater()
        if PROJECTS:
            for project in PROJECTS:
                cover_widget = ProjectCoverWidget(project)
                cover_widget.openProject.connect(self.open_project)
                self.coverStack.addWidget(cover_widget)
        else:
            new_project_btn = QToolButton()
            new_project_btn.setText("＋ New Project")
            new_project_btn.setFixedSize(300, 480)
            new_project_btn.clicked.connect(self.new_project)
            self.coverStack.addWidget(new_project_btn)
        self.updateCoverStackSize(self.coverStack.currentIndex())

    def show_previous(self):
        count = self.coverStack.count()
        if count == 0:
            return
        index = self.coverStack.currentIndex()
        new_index = (index - 1) % count
        self.coverStack.setCurrentIndex(new_index)

    def show_next(self):
        count = self.coverStack.count()
        if count == 0:
            return
        index = self.coverStack.currentIndex()
        new_index = (index + 1) % count
        self.coverStack.setCurrentIndex(new_index)

    def open_project(self, project_name):
        self.project_window = ProjectWindow(project_name)
        self.project_window.show()

    def new_project(self):
        name, ok = QInputDialog.getText(
            self, "New Project", "Enter new project name:")
        if ok and name.strip():
            new_project = {"name": name.strip(), "cover": None}
            PROJECTS.append(new_project)
            save_projects(PROJECTS)
            self.load_covers()
            self.coverStack.setCurrentIndex(len(PROJECTS) - 1)
            QMessageBox.information(
                self, "New Project", f"Project '{name}' created.")
        else:
            QMessageBox.information(
                self, "New Project", "Project creation cancelled.")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = WorkbenchWindow()
    window.show()
    sys.exit(app.exec_())
