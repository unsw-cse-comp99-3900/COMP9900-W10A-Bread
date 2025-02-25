#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QSplitter, QTreeWidget, QTextEdit, QToolBar, QAction, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QStackedWidget, QFontComboBox, QLabel
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from context_panel import ContextPanel
# Import the ThemeManager for icon tint mapping
from theme_manager import ThemeManager


def build_main_ui(window):
    # Ensure the main window has a current_theme attribute; default to "Standard" if not set.
    if not hasattr(window, "current_theme"):
        window.current_theme = "Standard"
    # Determine the tint color using the explicit mapping.
    tint_str = ThemeManager.ICON_TINTS.get(window.current_theme, "black")
    tint = QColor(tint_str)
    # store the tint for later use (e.g. in status icons)
    window.icon_tint = tint

    window.setStatusBar(window.statusBar())

    # Global Actions Toolbar (always visible)
    global_toolbar = QToolBar("Global Actions")
    window.addToolBar(global_toolbar)

    window.compendium_action = QAction(window.get_tinted_icon(
        "assets/icons/book.svg", tint_color=tint), "", window)
    window.compendium_action.setToolTip(
        "Compendium: Opens the Compendium to view and edit your worldbuilding database")
    window.compendium_action.triggered.connect(window.open_compendium)
    global_toolbar.addAction(window.compendium_action)

    window.prompt_options_action = QAction(window.get_tinted_icon(
        "assets/icons/settings.svg", tint_color=tint), "", window)
    window.prompt_options_action.setToolTip(
        "Prompt Options: Configure your writing prompts and LLM settings")
    window.prompt_options_action.triggered.connect(window.open_prompts_window)
    global_toolbar.addAction(window.prompt_options_action)

    window.workshop_action = QAction(window.get_tinted_icon(
        "assets/icons/message-square.svg", tint_color=tint), "", window)
    window.workshop_action.setToolTip("Workshop Chat: Opens the Workshop Chat")
    window.workshop_action.triggered.connect(window.open_workshop)
    global_toolbar.addAction(window.workshop_action)

    window.focus_mode_action = QAction(window.get_tinted_icon(
        "assets/icons/maximize-2.svg", tint_color=tint), "", window)
    window.focus_mode_action.setToolTip("Focus Mode: Enter Focus Mode")
    window.focus_mode_action.triggered.connect(window.open_focus_mode)
    global_toolbar.addAction(window.focus_mode_action)

    # Main layout: Left is the project tree, right is the editor area and toolbars
    main_splitter = QSplitter(Qt.Horizontal)

    # Project tree on the left
    window.tree = QTreeWidget()
    window.tree.setHeaderLabel("Project Structure")
    window.tree.setContextMenuPolicy(Qt.CustomContextMenu)
    window.tree.customContextMenuRequested.connect(
        window.show_tree_context_menu)
    window.populate_tree()
    window.tree.currentItemChanged.connect(window.tree_item_changed)
    main_splitter.addWidget(window.tree)

    # Right side: Editor area with an Editor Toolbar on top
    right_side = QWidget()
    right_layout = QVBoxLayout(right_side)

    # Editor Toolbar: Merges formatting actions and scene-specific controls
    editor_toolbar = QToolBar("Editor Toolbar", window)

    # --- Formatting Actions ---
    window.bold_action = QAction(window.get_tinted_icon(
        "assets/icons/bold.svg", tint_color=tint), "", window)
    window.bold_action.setToolTip("Bold")
    window.bold_action.setCheckable(True)
    window.bold_action.triggered.connect(window.toggle_bold)
    editor_toolbar.addAction(window.bold_action)

    window.italic_action = QAction(window.get_tinted_icon(
        "assets/icons/italic.svg", tint_color=tint), "", window)
    window.italic_action.setToolTip("Italic")
    window.italic_action.setCheckable(True)
    window.italic_action.triggered.connect(window.toggle_italic)
    editor_toolbar.addAction(window.italic_action)

    window.underline_action = QAction(window.get_tinted_icon(
        "assets/icons/underline.svg", tint_color=tint), "", window)
    window.underline_action.setToolTip("Underline")
    window.underline_action.setCheckable(True)
    window.underline_action.triggered.connect(window.toggle_underline)
    editor_toolbar.addAction(window.underline_action)

    window.tts_action = QAction(window.get_tinted_icon(
        "assets/icons/play-circle.svg", tint_color=tint), "", window)
    window.tts_action.setToolTip("Play TTS (or Stop if playing)")
    window.tts_action.triggered.connect(window.toggle_tts)
    editor_toolbar.addAction(window.tts_action)

    window.align_left_action = QAction(window.get_tinted_icon(
        "assets/icons/align-left.svg", tint_color=tint), "", window)
    window.align_left_action.setToolTip("Align Left")
    window.align_left_action.triggered.connect(window.align_left)
    editor_toolbar.addAction(window.align_left_action)

    window.align_center_action = QAction(window.get_tinted_icon(
        "assets/icons/align-center.svg", tint_color=tint), "", window)
    window.align_center_action.setToolTip("Center Align")
    window.align_center_action.triggered.connect(window.align_center)
    editor_toolbar.addAction(window.align_center_action)

    window.align_right_action = QAction(window.get_tinted_icon(
        "assets/icons/align-right.svg", tint_color=tint), "", window)
    window.align_right_action.setToolTip("Align Right")
    window.align_right_action.triggered.connect(window.align_right)
    editor_toolbar.addAction(window.align_right_action)

    # Font selection widgets as part of the toolbar
    from PyQt5.QtWidgets import QFontComboBox
    font_combo = QFontComboBox()
    font_combo.setToolTip("Select a font")
    font_combo.currentFontChanged.connect(
        lambda font: window.editor.setCurrentFont(font))
    editor_toolbar.addWidget(font_combo)

    font_size_combo = QComboBox()
    font_sizes = [10, 12, 14, 16, 18, 20, 24, 28, 32]
    for size in font_sizes:
        font_size_combo.addItem(str(size))
    font_size_combo.setCurrentText("12")
    font_size_combo.setToolTip("Select font size")
    font_size_combo.currentIndexChanged.connect(
        lambda: window.set_font_size(int(font_size_combo.currentText())))
    editor_toolbar.addWidget(font_size_combo)

    # --- Separator between formatting and scene-specific controls ---
    editor_toolbar.addSeparator()

    # --- Scene-Specific Actions ---
    window.manual_save_action = QAction(window.get_tinted_icon(
        "assets/icons/save.svg", tint_color=tint), "", window)
    window.manual_save_action.setToolTip(
        "Manual Save: Manually save the current scene")
    window.manual_save_action.triggered.connect(window.manual_save_scene)
    editor_toolbar.addAction(window.manual_save_action)

    window.oh_shit_action = QAction(window.get_tinted_icon(
        "assets/icons/share.svg", tint_color=tint), "", window)
    window.oh_shit_action.setToolTip(
        "Oh Shit: Show backup versions for this scene")
    window.oh_shit_action.triggered.connect(window.on_oh_shit)
    editor_toolbar.addAction(window.oh_shit_action)

    # --- Separator for scene settings (POV, Character, Tense) ---
    editor_toolbar.addSeparator()

    # POV dropdown
    window.pov_combo = QComboBox()
    window.pov_combo.setEditable(True)
    window.pov_combo.lineEdit().setReadOnly(True)
    window.pov_combo.lineEdit().setPlaceholderText("Perspective")
    pov_options = ["First Person", "Omniscient",
                   "Third Person Limited", "Custom..."]
    for option in pov_options:
        window.pov_combo.addItem(option)
    window.pov_combo.setCurrentIndex(-1)
    window.pov_combo.setToolTip("Select Perspective")
    window.pov_combo.currentIndexChanged.connect(window.handle_pov_change)
    editor_toolbar.addWidget(window.pov_combo)

    # POV Character dropdown
    window.pov_character_combo = QComboBox()
    window.pov_character_combo.setEditable(True)
    window.pov_character_combo.lineEdit().setReadOnly(True)
    window.pov_character_combo.lineEdit().setPlaceholderText("Character")
    window.pov_character_combo.setMinimumWidth(150)
    pov_character_options = ["Alice", "Bob", "Charlie", "Custom..."]
    for option in pov_character_options:
        window.pov_character_combo.addItem(option)
    window.pov_character_combo.setCurrentIndex(-1)
    window.pov_character_combo.setToolTip("Select POV Character")
    window.pov_character_combo.currentIndexChanged.connect(
        window.handle_pov_character_change)
    editor_toolbar.addWidget(window.pov_character_combo)

    # Tense dropdown
    window.tense_combo = QComboBox()
    window.tense_combo.setEditable(True)
    window.tense_combo.lineEdit().setReadOnly(True)
    window.tense_combo.lineEdit().setPlaceholderText("Tense")
    tense_options = ["Past Tense", "Present Tense", "Custom..."]
    for option in tense_options:
        window.tense_combo.addItem(option)
    window.tense_combo.setCurrentIndex(-1)
    window.tense_combo.setToolTip("Select Tense")
    window.tense_combo.currentIndexChanged.connect(window.handle_tense_change)
    editor_toolbar.addWidget(window.tense_combo)

    # Add the merged Editor Toolbar above the editor
    right_layout.addWidget(editor_toolbar)

    # ---- New: Editor and bottom panels in a vertical splitter ----

    # Scene editor with added border/shadow effect
    window.editor = QTextEdit()
    window.editor.setPlaceholderText("Select a node to edit its content...")
    window.editor.setContextMenuPolicy(Qt.CustomContextMenu)
    window.editor.customContextMenuRequested.connect(
        window.show_editor_context_menu)
    window.editor.setStyleSheet("border: 1px solid #ccc; padding: 2px;")

    # Bottom stacked widget (summary panel and LLM panel)
    window.bottom_stack = QStackedWidget()

    # Summary panel
    window.summary_panel = QWidget()
    summary_layout = QHBoxLayout(window.summary_panel)
    summary_layout.addStretch()
    window.create_summary_button = QPushButton("Create Summary")
    window.create_summary_button.clicked.connect(window.create_summary)
    summary_layout.addWidget(window.create_summary_button)
    window.save_summary_button = QPushButton("Save Summary")
    window.save_summary_button.clicked.connect(window.save_summary)
    summary_layout.addWidget(window.save_summary_button)
    summary_layout.addStretch()

    # LLM panel
    window.llm_panel = QWidget()
    llm_layout = QVBoxLayout(window.llm_panel)
    input_context_layout = QHBoxLayout()
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    window.prompt_input = QTextEdit()
    window.prompt_input.setPlaceholderText("Enter your action beats here...")
    window.prompt_input.setMinimumHeight(100)
    left_layout.addWidget(window.prompt_input)
    left_buttons_layout = QHBoxLayout()
    left_layout.addLayout(left_buttons_layout)
    window.prompt_dropdown = QComboBox()
    window.prompt_dropdown.setToolTip("Select a prose prompt")
    window.prompt_dropdown.addItem("Select Prose Prompt")
    window.prompt_dropdown.currentIndexChanged.connect(
        window.prompt_dropdown_changed)
    left_buttons_layout.addWidget(window.prompt_dropdown)
    # Modified Send Button using tinted icon
    window.send_button = QPushButton()
    window.send_button.setIcon(window.get_tinted_icon(
        "assets/icons/send.svg", tint_color=tint))
    window.send_button.setToolTip("Sends the action beats to the LLM")
    window.send_button.clicked.connect(window.send_prompt)
    left_buttons_layout.addWidget(window.send_button)

    # Modified Context Toggle Button using tinted icons
    window.context_toggle_button = QPushButton()
    window.context_toggle_button.setIcon(
        window.get_tinted_icon("assets/icons/book.svg", tint_color=tint))
    window.context_toggle_button.setToolTip(
        "Lets you decide which additional information to send with the prompt")
    window.context_toggle_button.setCheckable(True)

    def toggle_context():
        window.toggle_context_panel()
        window.context_toggle_button.setText("")
        if window.context_panel.isVisible():
            window.context_toggle_button.setIcon(window.get_tinted_icon(
                "assets/icons/book-open.svg", tint_color=tint))
        else:
            window.context_toggle_button.setIcon(
                window.get_tinted_icon("assets/icons/book.svg", tint_color=tint))

    window.context_toggle_button.clicked.connect(toggle_context)
    left_buttons_layout.addWidget(window.context_toggle_button)

    window.model_indicator = QLabel("")
    window.model_indicator.setStyleSheet(
        "font-weight: bold; padding-left: 10px;")
    window.model_indicator.setToolTip("Selected prompt's model")
    left_buttons_layout.addWidget(window.model_indicator)
    left_buttons_layout.addStretch()
    left_layout.addStretch()
    input_context_layout.addWidget(left_container, stretch=2)
    window.context_panel = ContextPanel(window.structure, window.project_name)
    window.context_panel.setVisible(False)
    input_context_layout.addWidget(window.context_panel, stretch=1)
    llm_layout.addLayout(input_context_layout)
    window.preview_text = QTextEdit()
    window.preview_text.setReadOnly(True)
    window.preview_text.setPlaceholderText(
        "LLM output preview will appear here...")
    llm_layout.addWidget(window.preview_text)
    button_layout = QHBoxLayout()
    # Apply Button using tinted feather icon
    window.apply_button = QPushButton()
    window.apply_button.setIcon(window.get_tinted_icon(
        "assets/icons/feather.svg", tint_color=tint))
    window.apply_button.setToolTip(
        "Appends the LLM's output to your current scene")
    window.apply_button.clicked.connect(window.apply_preview)
    button_layout.addWidget(window.apply_button)
    button_layout.addStretch()
    llm_layout.addLayout(button_layout)
    window.bottom_stack.addWidget(window.summary_panel)
    window.bottom_stack.addWidget(window.llm_panel)

    # Vertical splitter for editor and bottom panels
    editor_bottom_splitter = QSplitter(Qt.Vertical)
    editor_bottom_splitter.addWidget(window.editor)
    editor_bottom_splitter.addWidget(window.bottom_stack)
    editor_bottom_splitter.setStretchFactor(0, 3)
    editor_bottom_splitter.setStretchFactor(1, 1)
    right_layout.addWidget(editor_bottom_splitter)

    main_splitter.addWidget(right_side)
    main_splitter.setStretchFactor(1, 1)
    window.setCentralWidget(main_splitter)
