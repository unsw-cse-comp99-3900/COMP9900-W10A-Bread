#!/usr/bin/env python
"""
text_analysis_gui.py

A PyQt5-based GUI that uses the core analysis module to:
- Provide a text editor for input.
- Highlight problematic sentences based on complexity, weak formulations, passive constructions, 
  non-standard speech verbs, filter words, telling not showing, weak verbs, overused words,
  pronoun clarity issues, and repetitive sentence starts.
- Features a collapsible interface with splitters for maximizing the text area.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QFrame, QCheckBox,
    QGroupBox, QGridLayout, QTabWidget, QSplitter, QScrollArea
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QBrush, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from .text_analysis import (
    analyze_text, detect_passive, detect_weak_formulations, detect_nonstandard_speech_verbs,
    detect_filter_words, detect_telling_not_showing, analyze_verb_strength,
    detect_overused_words, check_pronoun_clarity, analyze_dialogue_balance,
    detect_repeated_sentence_starts, comprehensive_analysis
)

GENRE_TARGET_GRADES = {
    "Romance": 9,
    "Thriller": 11,
    "Hard Sci-Fi": 13,
    "Space Opera": 12,
    "Young Adult": 9,
    "Mystery": 10,
    "Fantasy": 11,
    "Historical Fiction": 12,
    "Literary Fiction": 13,
    "Horror": 11,
    "Non-Fiction": 12,
    "Biography": 11,
    "Self-help": 10,
    "Satire": 12,
    "Adventure": 10,
    "Crime": 11,
    "Paranormal": 10,
    "Dystopian": 12,
    "Memoir": 10,
    "Comedy": 9
}
CUSTOM_OPTION = "Custom"

# Define colors for each issue type
COLORS = {
    "complex": QColor("#FFC0C0"),      # Red - Complex sentences
    "weak": QColor("#CCFFCC"),         # Green - Weak formulations/passive voice
    "nonstandard": QColor("#ADD8E6"),  # Light blue - Non-standard speech verbs
    "filter": QColor("#FFE4B5"),       # Light orange - Filter words
    "telling": QColor("#E6E6FA"),      # Lavender - Telling not showing
    "weak_verb": QColor("#FFDAB9"),    # Peach - Weak verbs
    "overused": QColor("#F0E68C"),     # Khaki - Overused words
    "pronoun": QColor("#FFB6C1"),      # Light pink - Unclear pronoun references
    "repetitive": QColor("#D8BFD8")    # Thistle - Repetitive sentence starts
}

class ComprehensiveAnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(Exception)

    def __init__(self, full_text, target_grade):
        super().__init__()
        self.full_text = full_text
        self.target_grade = target_grade
        self.enabled_analyses = {}

    def run(self):
        try:
            results = comprehensive_analysis(self.full_text, self.target_grade)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(e)

from PyQt5.QtCore import Qt

class TextAnalysisApp(QWidget):
    def __init__(self, parent=None, initial_text="", save_callback=None):
        super().__init__(parent)
        # Force this widget to be a top-level window even if a parent is passed.
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("Writingway Text Analysis Editor")
        self.resize(1000, 800)
        self.save_callback = save_callback  # Store the callback for when Save is clicked
        self.init_ui()
        # Preload the text editor with the provided initial text
        self.text_edit.setPlainText(initial_text)
        self.analysis_results = None

    def init_ui(self):
        # Main layout for the entire application
        main_layout = QVBoxLayout(self)
        
        # Create tabs widget 
        self.tabs = QTabWidget()
        
        # === Main Analysis Tab ===
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Create the main splitter for the analysis tab
        self.main_splitter = QSplitter(Qt.Vertical)
        
        # Top section - Legend and instructions
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Legend in a collapsible section
        legend_group = self.create_legend()
        top_layout.addWidget(legend_group)
        
        instruction = QLabel("Enter your text below. Problematic text will be highlighted according to the legend.")
        top_layout.addWidget(instruction)
        
        # Middle section - Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setMinimumHeight(300)  # Ensure editor is always visible
        
        # Bottom section - Controls
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Analysis controls group
        controls_group = QGroupBox("Analysis Controls")
        controls_layout = QHBoxLayout()
        
        # Genre selection
        genre_layout = QVBoxLayout()
        genre_label = QLabel("Select Genre:")
        genre_layout.addWidget(genre_label)

        self.genre_combo = QComboBox()
        genre_options = list(GENRE_TARGET_GRADES.keys()) + [CUSTOM_OPTION]
        self.genre_combo.addItems(genre_options)
        self.genre_combo.currentTextChanged.connect(self.genre_changed)
        genre_layout.addWidget(self.genre_combo)

        self.custom_label = QLabel("Target Grade:")
        self.custom_entry = QLineEdit()
        self.custom_entry.setFixedWidth(50)
        custom_grade_layout = QHBoxLayout()
        custom_grade_layout.addWidget(self.custom_label)
        custom_grade_layout.addWidget(self.custom_entry)
        self.custom_label.hide()
        self.custom_entry.hide()
        genre_layout.addLayout(custom_grade_layout)
        
        controls_layout.addLayout(genre_layout)

        # Analysis options
        options_layout = QVBoxLayout()
        options_label = QLabel("Analysis Types:")
        options_layout.addWidget(options_label)

        # Create scrollable area for checkboxes
        self.analysis_options = {}
        analysis_options_scroll = QScrollArea()
        analysis_options_scroll.setWidgetResizable(True)
        analysis_options_widget = QWidget()
        analysis_options_layout = QVBoxLayout(analysis_options_widget)
        self.create_analysis_checkboxes(analysis_options_layout)
        analysis_options_scroll.setWidget(analysis_options_widget)
        options_layout.addWidget(analysis_options_scroll)
        
        controls_layout.addLayout(options_layout)
        controls_group.setLayout(controls_layout)
        bottom_layout.addWidget(controls_group)

        # Analysis button
        self.analyze_button = QPushButton("Run Analysis")
        self.analyze_button.clicked.connect(self.run_analysis)
        bottom_layout.addWidget(self.analyze_button)

        # Results summary label
        self.results_label = QLabel("")
        self.results_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.results_label.setLineWidth(1)
        self.results_label.setWordWrap(True)
        bottom_layout.addWidget(self.results_label)
        
        # Add the main splitter widgets
        self.main_splitter.addWidget(top_widget)
        self.main_splitter.addWidget(self.text_edit)
        self.main_splitter.addWidget(bottom_widget)
        
        # Set initial splitter sizes to give text editor most space
        self.main_splitter.setSizes([150, 400, 150])
        
        # Add the main splitter to the analysis tab
        analysis_layout.addWidget(self.main_splitter)
        
        # === Settings Tab ===
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Create scrollable area for settings
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_content = QWidget()
        settings_content_layout = QVBoxLayout(settings_content)
        self.setup_settings_tab(settings_content_layout)
        settings_scroll.setWidget(settings_content)
        settings_layout.addWidget(settings_scroll)
        
        # Add both tabs to the tab widget
        self.tabs.addTab(analysis_tab, "Text Analysis")
        self.tabs.addTab(settings_tab, "Settings")
        
        # Add the tab widget to the main layout
        main_layout.addWidget(self.tabs)

        # NEW: Save & Close button to return updated text
        save_close_button = QPushButton("Save & Close")
        save_close_button.clicked.connect(self.save_and_close)
        main_layout.addWidget(save_close_button)

    def create_legend(self):
        legend_group = QGroupBox("Highlighting Legend")
        legend_layout = QGridLayout()

        # Create color swatches and labels for each issue type
        legend_items = [
            ("Complex sentences", COLORS["complex"]),
            ("Weak formulations/passive voice", COLORS["weak"]),
            ("Non-standard speech verbs", COLORS["nonstandard"]),
            ("Filter words (narrative distance)", COLORS["filter"]),
            ("Telling not showing", COLORS["telling"]),
            ("Weak verbs", COLORS["weak_verb"]),
            ("Overused words", COLORS["overused"]),
            ("Unclear pronoun references", COLORS["pronoun"]),
            ("Repetitive sentence starts", COLORS["repetitive"]),
        ]

        for i, (label_text, color) in enumerate(legend_items):
            row, col = divmod(i, 3)  # 3 columns of legend items
            
            # Create color swatch
            swatch = QFrame()
            swatch.setFixedSize(20, 20)
            swatch.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            
            # Create label
            label = QLabel(label_text)
            
            # Add to grid
            legend_layout.addWidget(swatch, row, col*2)
            legend_layout.addWidget(label, row, col*2+1)

        legend_group.setLayout(legend_layout)
        return legend_group

    def create_analysis_checkboxes(self, layout):
        # Core sentence analysis
        self.analysis_options["complexity"] = QCheckBox("Sentence complexity")
        self.analysis_options["complexity"].setChecked(True)
        layout.addWidget(self.analysis_options["complexity"])

        # Weak formulations and passive
        self.analysis_options["weak_formulations"] = QCheckBox("Weak formulations/passive voice")
        self.analysis_options["weak_formulations"].setChecked(True)
        layout.addWidget(self.analysis_options["weak_formulations"])

        # Speech verbs
        self.analysis_options["speech_verbs"] = QCheckBox("Non-standard speech verbs")
        self.analysis_options["speech_verbs"].setChecked(True)
        layout.addWidget(self.analysis_options["speech_verbs"])

        # New analysis types
        self.analysis_options["filter_words"] = QCheckBox("Filter words")
        self.analysis_options["filter_words"].setChecked(True)
        layout.addWidget(self.analysis_options["filter_words"])
        
        self.analysis_options["telling"] = QCheckBox("Telling not showing")
        self.analysis_options["telling"].setChecked(True)
        layout.addWidget(self.analysis_options["telling"])
        
        self.analysis_options["weak_verbs"] = QCheckBox("Weak verbs")
        self.analysis_options["weak_verbs"].setChecked(True)
        layout.addWidget(self.analysis_options["weak_verbs"])
        
        self.analysis_options["overused"] = QCheckBox("Overused words")
        self.analysis_options["overused"].setChecked(True)
        layout.addWidget(self.analysis_options["overused"])
        
        self.analysis_options["pronoun_clarity"] = QCheckBox("Unclear pronoun references")
        self.analysis_options["pronoun_clarity"].setChecked(True)
        layout.addWidget(self.analysis_options["pronoun_clarity"])
        
        self.analysis_options["repetitive"] = QCheckBox("Repetitive sentence starts")
        self.analysis_options["repetitive"].setChecked(True)
        layout.addWidget(self.analysis_options["repetitive"])

    def setup_settings_tab(self, layout):
        # Thresholds group
        thresholds_group = QGroupBox("Analysis Thresholds")
        thresholds_layout = QGridLayout()
        
        # Overused words threshold
        thresholds_layout.addWidget(QLabel("Overused words threshold:"), 0, 0)
        self.overused_threshold = QLineEdit("3")
        self.overused_threshold.setFixedWidth(50)
        thresholds_layout.addWidget(self.overused_threshold, 0, 1)
        
        # Overused words window size
        thresholds_layout.addWidget(QLabel("Overused words window (chars):"), 1, 0)
        self.overused_window = QLineEdit("1000")
        self.overused_window.setFixedWidth(50)
        thresholds_layout.addWidget(self.overused_window, 1, 1)
        
        # Repetitive sentence starts threshold
        thresholds_layout.addWidget(QLabel("Repetitive starts threshold:"), 2, 0)
        self.repetitive_threshold = QLineEdit("3")
        self.repetitive_threshold.setFixedWidth(50)
        thresholds_layout.addWidget(self.repetitive_threshold, 2, 1)
        
        thresholds_group.setLayout(thresholds_layout)
        layout.addWidget(thresholds_group)
        
        # Appearance settings
        appearance_group = QGroupBox("Interface Customization")
        appearance_layout = QVBoxLayout()
        
        # Add a button to maximize the text editor
        self.maximize_editor_btn = QPushButton("Maximize Text Editor")
        self.maximize_editor_btn.clicked.connect(self.toggle_maximize_editor)
        appearance_layout.addWidget(self.maximize_editor_btn)
        
        # Add a button to restore default layout
        self.restore_layout_btn = QPushButton("Restore Default Layout")
        self.restore_layout_btn.clicked.connect(self.restore_default_layout)
        appearance_layout.addWidget(self.restore_layout_btn)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # User guide
        guide_group = QGroupBox("Tips")
        guide_layout = QVBoxLayout(guide_group)
        
        tip_text = QLabel(
            "<b>Interface Tips:</b><br>"
            "• Drag the splitter handles to resize sections<br>"
            "• Double-click a splitter handle to collapse/expand a section<br>"
            "• Use 'Maximize Text Editor' for a distraction-free writing experience<br>"
            "• Switch to the Analysis tab to see your text and run analysis<br>"
            "• Click 'Restore Default Layout' to reset the interface"
        )
        tip_text.setWordWrap(True)
        guide_layout.addWidget(tip_text)
        
        guide_group.setLayout(guide_layout)
        layout.addWidget(guide_group)
        
        # Add spacer to push everything to the top
        layout.addStretch()

    def toggle_maximize_editor(self):
        """Maximize or restore the text editor area"""
        # First switch to the analysis tab
        self.tabs.setCurrentIndex(0)
        
        if self.maximize_editor_btn.text() == "Maximize Text Editor":
            # Save current sizes for later restoration
            self.saved_sizes = self.main_splitter.sizes()
            
            # Set sizes to emphasize the editor (nearly invisible top and bottom)
            self.main_splitter.setSizes([1, 10000, 1])
            self.maximize_editor_btn.setText("Restore Layout")
        else:
            # Restore previous sizes or defaults
            if hasattr(self, 'saved_sizes'):
                self.main_splitter.setSizes(self.saved_sizes)
            else:
                self.restore_default_layout()
            self.maximize_editor_btn.setText("Maximize Text Editor")

    def restore_default_layout(self):
        """Reset the splitters to default positions"""
        # First switch to the analysis tab
        self.tabs.setCurrentIndex(0)
        
        # Restore default splitter sizes
        self.main_splitter.setSizes([150, 400, 150])
        self.maximize_editor_btn.setText("Maximize Text Editor")

    def genre_changed(self, text):
        if text == CUSTOM_OPTION:
            self.custom_label.show()
            self.custom_entry.show()
        else:
            self.custom_label.hide()
            self.custom_entry.hide()

    def run_analysis(self):
        full_text = self.text_edit.toPlainText()
        if not full_text:
            self.results_label.setText("Please enter text to analyze.")
            return
            
        selected_genre = self.genre_combo.currentText()
        if selected_genre == CUSTOM_OPTION:
            try:
                target_grade = float(self.custom_entry.text())
            except ValueError:
                self.results_label.setText("Invalid custom grade level. Please enter a valid number.")
                return
        else:
            target_grade = GENRE_TARGET_GRADES.get(selected_genre, 8)

        # Retain the original text
        self.text_edit.setPlainText(full_text)
        self.results_label.setText("Analyzing text...")

        # Get enabled analyses
        enabled_analyses = {key: checkbox.isChecked() for key, checkbox in self.analysis_options.items()}

        # Get thresholds
        try:
            overused_threshold = int(self.overused_threshold.text())
            overused_window = int(self.overused_window.text())
            repetitive_threshold = int(self.repetitive_threshold.text())
        except ValueError:
            self.results_label.setText("Invalid threshold values. Please enter valid numbers.")
            return

        self.worker = ComprehensiveAnalysisWorker(full_text, target_grade)
        self.worker.enabled_analyses = enabled_analyses
        self.worker.finished.connect(lambda results: self.update_highlighting(results, enabled_analyses))
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def update_highlighting(self, results, enabled_analyses):
        cursor = self.text_edit.textCursor()
        
        # Create format objects for each issue type
        formats = {
            "complex": QTextCharFormat(),
            "weak": QTextCharFormat(),
            "nonstandard": QTextCharFormat(),
            "filter": QTextCharFormat(),
            "telling": QTextCharFormat(),
            "weak_verb": QTextCharFormat(),
            "overused": QTextCharFormat(),
            "pronoun": QTextCharFormat(),
            "repetitive": QTextCharFormat()
        }
        
        # Set colors for each format
        for issue_type, color in COLORS.items():
            formats[issue_type].setBackground(QBrush(color))

        # Clear any existing formatting
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        clear_format = QTextCharFormat()
        cursor.setCharFormat(clear_format)
        
        # Track statistics for summary
        stats = {
            "complex_sentences": 0,
            "weak_formulations": 0,
            "nonstandard_speech": 0,
            "filter_words": 0,
            "telling_not_showing": 0,
            "weak_verbs": 0,
            "overused_words": 0,
            "pronoun_clarity": 0,
            "repetitive_starts": 0
        }

        # Apply highlighting for complex sentences
        if enabled_analyses.get("complexity", False):
            for sent in results["sentence_analysis"]:
                if sent["complex"]:
                    cursor.setPosition(sent["start"])
                    cursor.setPosition(sent["end"], QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(formats["complex"])
                    stats["complex_sentences"] += 1

        # Apply highlighting for weak formulations and passive
        if enabled_analyses.get("weak_formulations", False):
            for sent in results["sentence_analysis"]:
                sent_text = sent["sentence"]
                sent_doc = sent["doc"]
                sent_start = sent["start"]
                
                # Weak formulations
                weak_spans = detect_weak_formulations(sent_text, sent_doc)
                for span in weak_spans:
                    token_start = sent_start + span[0]
                    token_end = sent_start + span[1]
                    cursor.setPosition(token_start)
                    cursor.setPosition(token_end, QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(formats["weak"])
                    stats["weak_formulations"] += 1
                
                # Passive voice
                passive_spans = detect_passive(sent_text, sent_doc)
                for span in passive_spans:
                    token_start = sent_start + span[0]
                    token_end = sent_start + span[1]
                    cursor.setPosition(token_start)
                    cursor.setPosition(token_end, QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(formats["weak"])
                    stats["weak_formulations"] += 1

        # Apply highlighting for non-standard speech verbs
        if enabled_analyses.get("speech_verbs", False):
            for sent in results["sentence_analysis"]:
                sent_text = sent["sentence"]
                sent_start = sent["start"]
                
                nonstandard_spans = detect_nonstandard_speech_verbs(sent_text)
                for span in nonstandard_spans:
                    tag_start = sent_start + span[0]
                    tag_end = sent_start + span[1]
                    cursor.setPosition(tag_start)
                    cursor.setPosition(tag_end, QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(formats["nonstandard"])
                    stats["nonstandard_speech"] += 1

        # Apply highlighting for filter words
        if enabled_analyses.get("filter_words", False):
            for start, end, word in results["filter_words"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["filter"])
                stats["filter_words"] += 1

        # Apply highlighting for telling not showing
        if enabled_analyses.get("telling", False):
            for start, end, phrase in results["telling_not_showing"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["telling"])
                stats["telling_not_showing"] += 1

        # Apply highlighting for weak verbs
        if enabled_analyses.get("weak_verbs", False):
            for start, end, construction, verb_type in results["weak_verbs"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["weak_verb"])
                stats["weak_verbs"] += 1

        # Apply highlighting for overused words
        if enabled_analyses.get("overused", False):
            for start, end, word, count in results["overused_words"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["overused"])
                stats["overused_words"] += 1

        # Apply highlighting for pronoun clarity
        if enabled_analyses.get("pronoun_clarity", False):
            for start, end, pronoun in results["pronoun_clarity"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["pronoun"])
                stats["pronoun_clarity"] += 1

        # Apply highlighting for repetitive sentence starts
        if enabled_analyses.get("repetitive", False):
            for start, end, pattern in results["repeated_sentence_starts"]:
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(formats["repetitive"])
                stats["repetitive_starts"] += 1

        # Update results summary
        self.update_results_summary(stats, results["dialogue_ratio"])

    def update_results_summary(self, stats, dialogue_ratio):
        summary = "Analysis Results Summary:\n"
        
        # Count total issues
        total_issues = sum(stats.values())
        
        summary += f"Total issues found: {total_issues}\n"
        summary += f"- Complex sentences: {stats['complex_sentences']}\n"
        summary += f"- Weak formulations/passive: {stats['weak_formulations']}\n"
        summary += f"- Non-standard speech verbs: {stats['nonstandard_speech']}\n"
        summary += f"- Filter words: {stats['filter_words']}\n"
        summary += f"- Telling not showing: {stats['telling_not_showing']}\n"
        summary += f"- Weak verbs: {stats['weak_verbs']}\n"
        summary += f"- Overused words: {stats['overused_words']}\n"
        summary += f"- Unclear pronoun references: {stats['pronoun_clarity']}\n"
        summary += f"- Repetitive sentence starts: {stats['repetitive_starts']}\n"
        
        # Add dialogue ratio
        dialogue_percentage = round(dialogue_ratio * 100, 1)
        summary += f"\nDialogue percentage: {dialogue_percentage}%"
        if dialogue_percentage > 70:
            summary += " (dialogue-heavy)"
        elif dialogue_percentage < 20:
            summary += " (narrative-heavy)"
        
        self.results_label.setText(summary)

    def handle_error(self, exception):
        self.results_label.setText(f"Error during analysis: {exception}")

    def save_and_close(self):
        """Called when the 'Save & Close' button is clicked.
        Retrieves the current text from the analysis editor, calls the save_callback
        (if provided) with the updated text, and then closes this window.
        """
        updated_text = self.text_edit.toPlainText()
        if self.save_callback:
            self.save_callback(updated_text)
        self.close()

def main():
    app = QApplication(sys.argv)
    # For standalone testing, no initial text or callback is provided.
    window = TextAnalysisApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
