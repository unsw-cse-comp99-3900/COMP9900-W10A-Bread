#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QAction, QFontComboBox, QComboBox, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor, QColor
from .focus_mode import PlainTextEdit

class SceneEditor(QWidget):
    """Scene editor with toolbar and text area."""
    def __init__(self, controller, tint_color=QColor("black")):
        super().__init__()
        self.controller = controller
        self.tint_color = tint_color
        self.suppress_updates = False # Stop recursive updates to toolbar values
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.toolbar = QToolBar("Editor Toolbar")
        self.toolbar.setObjectName("SceneEditorToolBar")
        self.editor = PlainTextEdit()
        self.setup_toolbar()
        self.setup_editor()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.editor)
        layout.setContentsMargins(0, 0, 0, 0)

    def setup_toolbar(self):
        # Formatting Actions
        self.bold_action = self.add_action("bold", "assets/icons/bold.svg", "Bold", self.controller.toggle_bold, checkable=True)
        self.italic_action = self.add_action("italic", "assets/icons/italic.svg", "Italic", self.controller.toggle_italic, checkable=True)
        self.underline_action = self.add_action("underline", "assets/icons/underline.svg", "Underline", self.controller.toggle_underline, checkable=True)
        self.toolbar.addSeparator()
        self.tts_action = self.add_action("tts", "assets/icons/play-circle.svg", "Play TTS (or Stop if playing)", self.controller.toggle_tts)
        self.toolbar.addSeparator()
        self.align_left_action = self.add_action("align_left", "assets/icons/align-left.svg", "Align Left", self.controller.align_left)
        self.align_center_action = self.add_action("align_center", "assets/icons/align-center.svg", "Center Align", self.controller.align_center)
        self.align_right_action = self.add_action("align_right", "assets/icons/align-right.svg", "Align Right", self.controller.align_right)

        # Font Selection
        self.font_combo = QFontComboBox()
        self.font_combo.setToolTip("Select a font")
        self.font_combo.currentFontChanged.connect(self.controller.update_font_family)
        self.toolbar.addWidget(self.font_combo)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(size) for size in [10, 12, 14, 16, 18, 20, 24, 28, 32]])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.setToolTip("Select font size")
        self.font_size_combo.currentIndexChanged.connect(lambda: self.controller.set_font_size(int(self.font_size_combo.currentText())))
        self.toolbar.addWidget(self.font_size_combo)

        # Scene-Specific Actions
        self.toolbar.addSeparator()
        self.manual_save_action = self.add_action("manual_save", "assets/icons/save.svg", "Manual Save", self.controller.manual_save_scene)
        self.oh_shit_action = self.add_action("oh_shit", "assets/icons/share.svg", "Show Backups", self.controller.on_oh_shit)
        self.analysis_editor_action = self.add_action("analysis_editor", "assets/icons/feather.svg", "Open Analysis Editor", self.controller.open_analysis_editor)
        self.whisper_app_action = self.add_action("whisper_app", "assets/icons/mic.svg", "Open Whisper App", self.controller.open_whisper_app)
        self.wikidata_dialog_action = self.add_action("wikidata_dialog", "assets/icons/wikidata.svg", "Open Wikipedia", self.controller.open_wikidata_search)
        self.toolbar.addSeparator()

    def add_action(self, name, icon_path, tooltip, callback, checkable=False):
        action = QAction(self.controller.get_tinted_icon(icon_path, self.tint_color), "", self)
        action.setToolTip(tooltip)
        action.setCheckable(checkable)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)
        setattr(self, f"{name}_action", action)
        return action

    def setup_editor(self):
        self.editor.setPlaceholderText("Select a node to edit its content...")
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.controller.show_editor_context_menu)
        self.editor.setStyleSheet("border: 1px solid #ccc; padding: 2px;")
        self.editor.textChanged.connect(self.controller.on_editor_text_changed)
        # Connect cursor and selection signals
        self.editor.cursorPositionChanged.connect(self.update_toolbar_state)
        self.editor.selectionChanged.connect(self.update_toolbar_state)
        # Initialize toolbar state
        self.update_toolbar_state()

    def on_font_size_changed(self):
        if self.suppress_updates:
            return
        size_text = self.font_size_combo.currentText()
        if size_text:
            self.controller.set_font_size(int(size_text))

    def update_toolbar_state(self):
        if self.suppress_updates:
            return
        self.suppress_updates = True  # Prevent recursive updates

        cursor = self.editor.textCursor()
        has_selection = cursor.hasSelection()

        if has_selection:
            # Analyze the entire selection
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            formats = self.get_selection_formats(start, end)
            self.update_toggles_for_selection(formats)
            self.update_font_combo_for_selection(formats)
            self.update_font_size_combo_for_selection(formats)
        else:
            # Use the format at the cursor position
            char_format = self.editor.currentCharFormat()
            self.update_toggles(char_format)
            self.update_font_combo(char_format)
            self.update_font_size_combo(char_format)

        # Update alignment actions (simplified, as alignment applies to blocks)
        block_format = cursor.blockFormat()
        alignment = block_format.alignment()
        self.align_left_action.setChecked(alignment == Qt.AlignLeft)
        self.align_center_action.setChecked(alignment == Qt.AlignCenter)
        self.align_right_action.setChecked(alignment == Qt.AlignRight)

        self.suppress_updates = False

    def get_selection_formats(self, start, end):
        """Collect unique format attributes in the selection."""
        formats = {
            "bold": set(),
            "italic": set(),
            "underline": set(),
            "font_families": set(),
            "font_sizes": set()
        }
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        while cursor.position() < end:
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)
            if cursor.position() <= end:
                char_format = cursor.charFormat()
                formats["bold"].add(char_format.fontWeight() >= QFont.Bold)
                formats["italic"].add(char_format.fontItalic())
                formats["underline"].add(char_format.fontUnderline())
                formats["font_families"].add(char_format.font().family() if char_format.font().family() else "")
                formats["font_sizes"].add(char_format.fontPointSize() if char_format.fontPointSize() > 0 else 0)
            cursor.setPosition(cursor.position(), QTextCursor.MoveAnchor)
        return formats

    def update_toggles(self, char_format):
        """Update bold, italic, underline toggles based on char format."""
        self.bold_action.setChecked(char_format.fontWeight() >= QFont.Bold)
        self.italic_action.setChecked(char_format.fontItalic())
        self.underline_action.setChecked(char_format.fontUnderline())

    def update_toggles_for_selection(self, formats):
        """Update toggles for a selection, indeterminate if mixed."""
        self.bold_action.setChecked(len(formats["bold"]) == 1 and True in formats["bold"])
        self.italic_action.setChecked(len(formats["italic"]) == 1 and True in formats["italic"])
        self.underline_action.setChecked(len(formats["underline"]) == 1 and True in formats["underline"])

    def update_font_combo(self, char_format):
        """Update font combo based on char format."""
        font_family = char_format.font().family()
        if font_family:
            self.font_combo.blockSignals(True)
            self.font_combo.setCurrentFont(char_format.font())
            self.font_combo.blockSignals(False)

    def update_font_combo_for_selection(self, formats):
        """Update font combo for selection, blank if mixed."""
        self.font_combo.blockSignals(True)
        if len(formats["font_families"]) == 1:
            font_family = next(iter(formats["font_families"]))
            if font_family:
                from PyQt5.QtGui import QFont
                self.font_combo.setCurrentFont(QFont(font_family))
            else:
                self.font_combo.setCurrentText("")
        else:
            self.font_combo.setCurrentText("")
        self.font_combo.blockSignals(False)

    def update_font_size_combo(self, char_format):
        """Update font size combo based on char format."""
        size = char_format.fontPointSize()
        self.font_size_combo.blockSignals(True)
        if size > 0:
            size_str = str(int(size))
            if size_str in [self.font_size_combo.itemText(i) for i in range(self.font_size_combo.count())]:
                self.font_size_combo.setCurrentText(size_str)
            else:
                self.font_size_combo.setCurrentText("")
        else:
            self.font_size_combo.setCurrentText("")
        self.font_size_combo.blockSignals(False)

    def update_font_size_combo_for_selection(self, formats):
        """Update font size combo for selection, blank if mixed."""
        self.font_size_combo.blockSignals(True)
        if len(formats["font_sizes"]) == 1:
            size = next(iter(formats["font_sizes"]))
            if size > 0:
                size_str = str(int(size))
                if size_str in [self.font_size_combo.itemText(i) for i in range(self.font_size_combo.count())]:
                    self.font_size_combo.setCurrentText(size_str)
                else:
                    self.font_size_combo.setCurrentText("")
            else:
                self.font_size_combo.setCurrentText("")
        else:
            self.font_size_combo.setCurrentText("")
        self.font_size_combo.blockSignals(False)

    def update_tint(self, tint_color):
        """Update icon tints when theme changes."""
        self.tint_color = tint_color
        for action in ["bold", "italic", "underline", "tts", "align_left", "align_center", "align_right", "manual_save", "oh_shit", "analysis_editor"]:
            getattr(self, f"{action}_action").setIcon(self.controller.get_tinted_icon(f"assets/icons/{action.replace('_', '-')}.svg", tint_color))