from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QVBoxLayout
from PyQt5.QtGui import QColor
from settings.theme_manager import ThemeManager

class GlobalToolbar(QWidget):
    """Global actions toolbar at the top of the window."""
    def __init__(self, controller, tint_color=QColor("black")):
        super().__init__()
        self.controller = controller  # Reference to ProjectWindow for callbacks
        self.tint_color = tint_color
        self.toolbar = QToolBar(_("Global Actions"))
        self.toolbar.setObjectName("GlobalActionsToolBar")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setStyleSheet("")  # Reset any custom styles to use theme

        for icon, tip, func in [
            ("assets/icons/message-square.svg", _("Workshop Chat"), self.controller.open_workshop),
            ("assets/icons/mic.svg",_("Open Whisper"),self.controller.open_whisper_app),
            ("assets/icons/wikidata.svg",_("Open Web with LLM"),self.controller.open_web_llm),
            ("assets/icons/arch.svg",_("Open Internet Archive"),self.controller.open_ia_window),
            ("assets/icons/maximize-2.svg", _("Focus Mode"), self.controller.open_focus_mode),
        ]:
            self.add_action(icon, tip, func)

    def add_action(self, icon_path, tooltip, callback):
        action = QAction(ThemeManager.get_tinted_icon(icon_path, self.tint_color), "", self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)
        return action

    def update_tint(self, tint_color):
        """Update icon tints when theme changes."""
        self.tint_color = tint_color
        self.workshop_action.setIcon(ThemeManager.get_tinted_icon("assets/icons/message-square.svg", tint_color))
        self.focus_mode_action.setIcon(ThemeManager.get_tinted_icon("assets/icons/maximize-2.svg", tint_color))