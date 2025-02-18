#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QSplitter, QTreeWidget, QTextEdit, QToolBar, QAction, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QStackedWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from context_panel import ContextPanel

def build_main_ui(window):
    """
    Builds and attaches the main UI for the given window.
    This function creates the toolbar, project tree, editor, and all other UI components,
    wiring up signals to the methods defined on the window.
    """
    # Set up status bar
    window.setStatusBar(window.statusBar())
    
    # Create the main toolbar
    toolbar = QToolBar("Main Toolbar")
    window.addToolBar(toolbar)
    
    compendium_action = QAction(QIcon.fromTheme("book"), "Compendium", window)
    compendium_action.setStatusTip("Open Compendium")
    compendium_action.triggered.connect(window.open_compendium)
    toolbar.addAction(compendium_action)
    
    prompt_options_action = QAction(QIcon.fromTheme("document-properties"), "Prompt Options", window)
    prompt_options_action.setStatusTip("Configure your writing prompts")
    prompt_options_action.triggered.connect(window.open_prompts_window)
    toolbar.addAction(prompt_options_action)
    
    workshop_action = QAction(QIcon.fromTheme("chat"), "Workshop", window)
    workshop_action.setStatusTip("Open Workshop Chat")
    workshop_action.triggered.connect(window.open_workshop)
    toolbar.addAction(workshop_action)
    
    # Create the main splitter (left: project tree, right: editor and panels)
    main_splitter = QSplitter(Qt.Horizontal)
    
    # Left side: Project Tree
    window.tree = QTreeWidget()
    window.tree.setHeaderLabel("Project Structure")
    window.tree.setContextMenuPolicy(Qt.CustomContextMenu)
    window.tree.customContextMenuRequested.connect(window.show_tree_context_menu)
    window.populate_tree()
    window.tree.currentItemChanged.connect(window.tree_item_changed)
    main_splitter.addWidget(window.tree)
    
    # Right side: Editor and additional panels
    top_right = QWidget()
    top_right_layout = QVBoxLayout(top_right)
    
    # Formatting toolbar (bold, italic, underline, TTS)
    window.formatting_toolbar = QHBoxLayout()
    
    bold_button = QPushButton("B")
    bold_button.setCheckable(True)
    bold_button.setStyleSheet("font-weight: bold;")
    bold_button.clicked.connect(window.toggle_bold)
    window.formatting_toolbar.addWidget(bold_button)
    
    italic_button = QPushButton("I")
    italic_button.setCheckable(True)
    italic_button.setStyleSheet("font-style: italic;")
    italic_button.clicked.connect(window.toggle_italic)
    window.formatting_toolbar.addWidget(italic_button)
    
    underline_button = QPushButton("U")
    underline_button.setCheckable(True)
    underline_button.setStyleSheet("text-decoration: underline;")
    underline_button.clicked.connect(window.toggle_underline)
    window.formatting_toolbar.addWidget(underline_button)
    
    window.tts_button = QPushButton("TTS")
    window.tts_button.setToolTip("Read selected text (or entire scene if nothing is selected)")
    window.tts_button.clicked.connect(window.toggle_tts)
    window.formatting_toolbar.addWidget(window.tts_button)
    
    window.formatting_toolbar.addStretch()
    top_right_layout.addLayout(window.formatting_toolbar)
    
    # Editor
    window.editor = QTextEdit()
    window.editor.setPlaceholderText("Select a node to edit its content...")
    top_right_layout.addWidget(window.editor)
    window.editor.setContextMenuPolicy(Qt.CustomContextMenu)
    window.editor.customContextMenuRequested.connect(window.show_editor_context_menu)
    
    # Scene settings toolbar: manual save, backup, and POV settings
    window.scene_settings_toolbar = QWidget()
    scene_settings_layout = QHBoxLayout(window.scene_settings_toolbar)
    
    # Save group
    save_group = QWidget()
    save_layout = QHBoxLayout(save_group)
    window.manual_save_button = QPushButton("Manual Save")
    window.manual_save_button.setToolTip("Manually save the current scene")
    window.manual_save_button.clicked.connect(window.manual_save_scene)
    save_layout.addWidget(window.manual_save_button)
    
    window.oh_shit_button = QPushButton("Oh Shit")
    window.oh_shit_button.setToolTip("Show backup versions for this scene")
    window.oh_shit_button.clicked.connect(window.on_oh_shit)
    save_layout.addWidget(window.oh_shit_button)
    save_layout.addStretch()
    
    # POV settings group
    pov_group = QWidget()
    pov_layout = QHBoxLayout(pov_group)
    
    window.pov_combo = QComboBox()
    pov_options = ["First Person", "Omniscient", "Third Person Limited", "Custom..."]
    if window.current_pov not in pov_options:
        window.pov_combo.addItem(window.current_pov)
    for option in pov_options:
        window.pov_combo.addItem(option)
    window.pov_combo.setCurrentText(window.current_pov)
    window.pov_combo.setToolTip(f"POV: {window.current_pov}")
    window.pov_combo.currentIndexChanged.connect(window.handle_pov_change)
    pov_layout.addWidget(window.pov_combo)
    
    window.pov_character_combo = QComboBox()
    pov_character_options = ["Alice", "Bob", "Charlie", "Custom..."]
    if window.current_pov_character not in pov_character_options:
        window.pov_character_combo.addItem(window.current_pov_character)
    for option in pov_character_options:
        window.pov_character_combo.addItem(option)
    window.pov_character_combo.setCurrentText(window.current_pov_character)
    window.pov_character_combo.setToolTip(f"POV Character: {window.current_pov_character}")
    window.pov_character_combo.currentIndexChanged.connect(window.handle_pov_character_change)
    pov_layout.addWidget(window.pov_character_combo)
    
    window.tense_combo = QComboBox()
    tense_options = ["Past Tense", "Present Tense", "Custom..."]
    if window.current_tense not in tense_options:
        window.tense_combo.addItem(window.current_tense)
    for option in tense_options:
        window.tense_combo.addItem(option)
    window.tense_combo.setCurrentText(window.current_tense)
    window.tense_combo.setToolTip(f"Tense: {window.current_tense}")
    window.tense_combo.currentIndexChanged.connect(window.handle_tense_change)
    pov_layout.addWidget(window.tense_combo)
    
    pov_layout.addStretch()
    
    scene_settings_layout.addWidget(save_group)
    scene_settings_layout.addSpacing(20)
    scene_settings_layout.addWidget(pov_group)
    scene_settings_layout.addStretch()
    top_right_layout.addWidget(window.scene_settings_toolbar)
    
    # Bottom stacked widget: summary panel and LLM panel
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
    
    # Left container: prompt input and buttons
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    window.prompt_input = QTextEdit()
    window.prompt_input.setPlaceholderText("Enter your action beats here...")
    window.prompt_input.setMinimumHeight(100)
    left_layout.addWidget(window.prompt_input)
    
    left_buttons_layout = QHBoxLayout()
    window.prompt_button = QPushButton("Prompt")
    window.prompt_button.setToolTip("Select a prose prompt")
    window.prompt_button.clicked.connect(window.select_prose_prompt)
    left_buttons_layout.addWidget(window.prompt_button)
    
    window.send_button = QPushButton("Send")
    window.send_button.setToolTip("Send the prompt to the LLM")
    window.send_button.clicked.connect(window.send_prompt)
    left_buttons_layout.addWidget(window.send_button)
    
    window.context_toggle_button = QPushButton("Context")
    window.context_toggle_button.setToolTip("Show extra context settings")
    window.context_toggle_button.setCheckable(True)
    window.context_toggle_button.clicked.connect(window.toggle_context_panel)
    left_buttons_layout.addWidget(window.context_toggle_button)
    left_buttons_layout.addStretch()
    left_layout.addLayout(left_buttons_layout)
    
    input_context_layout.addWidget(left_container, stretch=2)
    
    # Context panel
    window.context_panel = ContextPanel(window.structure, window.project_name)
    window.context_panel.setVisible(False)
    input_context_layout.addWidget(window.context_panel, stretch=1)
    
    llm_layout.addLayout(input_context_layout)
    
    window.preview_text = QTextEdit()
    window.preview_text.setReadOnly(True)
    window.preview_text.setPlaceholderText("LLM output preview will appear here...")
    llm_layout.addWidget(window.preview_text)
    
    button_layout = QHBoxLayout()
    window.apply_button = QPushButton("Apply")
    window.apply_button.setToolTip("Append the preview text to the scene")
    window.apply_button.clicked.connect(window.apply_preview)
    button_layout.addWidget(window.apply_button)
    
    window.retry_button = QPushButton("Retry")
    window.retry_button.setToolTip("Clear preview and re-send the prompt")
    window.retry_button.clicked.connect(window.retry_prompt)
    button_layout.addWidget(window.retry_button)
    button_layout.addStretch()
    llm_layout.addLayout(button_layout)
    
    window.bottom_stack.addWidget(window.summary_panel)
    window.bottom_stack.addWidget(window.llm_panel)
    
    # Combine top_right with bottom_stack in a vertical splitter
    right_splitter = QSplitter(Qt.Vertical)
    right_splitter.addWidget(top_right)
    right_splitter.addWidget(window.bottom_stack)
    right_splitter.setStretchFactor(0, 3)
    right_splitter.setStretchFactor(1, 1)
    
    main_splitter.addWidget(right_splitter)
    main_splitter.setStretchFactor(1, 1)
    window.setCentralWidget(main_splitter)
