from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QTextBrowser, QLabel, QApplication, QSplitter, QWidget, QShortcut
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QKeySequence, QPalette, QColor, QDesktopServices
from urllib.parse import urlparse, unquote 
import wikipediaapi
import requests
from io import BytesIO
from settings.llm_api_aggregator import WWApiAggregator
from util.find_dialog import FindDialog

class LLMThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, prompt, overrides):
        super().__init__()
        self.prompt = prompt
        self.overrides = overrides

    def run(self):
        try:
            response = WWApiAggregator.send_prompt_to_llm(self.prompt, self.overrides)
            self.response_signal.emit(response if response else "LLM did not return a response.")
        except Exception as e:
            self.response_signal.emit(f"Error sending prompt: {e}")

class WikidataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wikipedia Search and LLM Processor")
        self.setGeometry(100, 100, 1000, 800)
        
        # Set window flags 
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        # Set the window as non-modal
        self.setWindowModality(Qt.NonModal)

        # Initialize default Wikipedia API instance (English language)
        self.wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='WritingwayApp/1.0 (contact@example.com)',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

        # Main layout
        main_layout = QVBoxLayout(self)

        # --- TOP BAR: search field, language code input, and buttons ---
        top_bar_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search term...")
        top_bar_layout.addWidget(self.search_field)
        
        # QLineEdit for entering language code, default is "en"
        self.language_input = QLineEdit()
        self.language_input.setPlaceholderText("Enter language code...")
        self.language_input.setText("en")
        self.language_input.setMaximumWidth(50)
        top_bar_layout.addWidget(self.language_input)
        
        self.search_button = QPushButton("Search Wikipedia")
        self.search_button.clicked.connect(self.perform_search)
        top_bar_layout.addWidget(self.search_button)
        
        self.expand_button = QPushButton("Show Full Article")
        self.expand_button.clicked.connect(self.show_full_article)
        self.expand_button.setEnabled(False)
        top_bar_layout.addWidget(self.expand_button)
        
        # Shortcut Ctrl+F for in-article search
        self.shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_find.activated.connect(self.open_find_dialog)
        self.find_dialog = None

        main_layout.addLayout(top_bar_layout)

        # --- MAIN VERTICAL SPLITTER ---
        self.main_splitter = QSplitter(Qt.Vertical)

        # --- TOP SECTION: article image and text ---
        self.wiki_splitter = QSplitter(Qt.Vertical)
        
        # Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMaximumHeight(300)
        self.image_label.setScaledContents(False)
        self.wiki_splitter.addWidget(self.image_label)
        
        # Article text
        self.result_display = QTextBrowser()
        self.result_display.setOpenExternalLinks(False)
        self.wiki_splitter.addWidget(self.result_display)
        self.result_display.anchorClicked.connect(self.handle_link_click) 
        
        # Set palette for result_display to customize inactive highlighting
        palette = self.result_display.palette()
        palette.setColor(QPalette.Inactive, QPalette.Highlight, QColor("yellow"))
        palette.setColor(QPalette.Inactive, QPalette.HighlightedText, QColor("black"))
        self.result_display.setPalette(palette)
        
        # Set proportions (image: 1, text: 3)
        self.wiki_splitter.setStretchFactor(0, 1)
        self.wiki_splitter.setStretchFactor(1, 3)
        self.main_splitter.addWidget(self.wiki_splitter)

        # --- BOTTOM SECTION: LLM ---
        self.llm_widget = QWidget()
        llm_layout = QHBoxLayout(self.llm_widget)
        
        # Left panel: prompt and button
        prompt_layout = QVBoxLayout()
        prompt_label = QLabel("Enter prompt:")
        prompt_layout.addWidget(prompt_label)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Remember to set the maximum timeout in the settings and the number of tokens...")
        prompt_layout.addWidget(self.prompt_input)
        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.send_message)
        prompt_layout.addWidget(self.send_button)
        llm_layout.addLayout(prompt_layout)
        
        # Right panel: LLM response
        answer_layout = QVBoxLayout()
        answer_label = QLabel("LLM Response:")
        answer_layout.addWidget(answer_label)
        self.answer_display = QTextBrowser()
        answer_layout.addWidget(self.answer_display)
        llm_layout.addLayout(answer_layout)
        
        self.main_splitter.addWidget(self.llm_widget)
        self.main_splitter.setStretchFactor(0, 4)
        self.main_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.main_splitter)

        # Storage for full article text
        self.full_article_text = ""

        self.setLayout(main_layout)

    def perform_search(self):
        query = self.search_field.text()
        selected_language = self.language_input.text().strip() or "en"
    
        # Create a new instance of the Wikipedia API for the selected language
        wiki_wiki = wikipediaapi.Wikipedia(
            language=selected_language,
            user_agent='WritingwayApp/1.0 (contact@example.com)',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

        if query:
            page = wiki_wiki.page(query)
            if page.exists():
                # Prepare the text of the article
                processed_text = page.text[:5000].replace('\n', '<br>')
                sections = self.get_sections(page)
                categories = self.get_categories(page)
                links = self.get_links(page)
                self.full_article_text = page.text

                # Generate valid Wikipedia links
                html_links = []
                for link_title in links[:10]:
                    # Encode the title for the URL
                    encoded_title = link_title.replace(' ', '_')
                    encoded_title = requests.utils.quote(encoded_title)
                    wikipedia_url = f"https://{selected_language}.wikipedia.org/wiki/{encoded_title}"
                    html_links.append(f'<li><a href="{wikipedia_url}">{link_title}</a></li>')

                # Build HTML content
                html_content = f"""
                <h1>{page.title}</h1>
                <h2>Basic Information</h2>
                <p>{processed_text} [...]</p>
                <h2>Main Sections</h2>
                <ul>
                    {''.join(f'<li>{section}</li>' for section in sections)}
                </ul>
                <h2>Categories</h2>
                <p>{', '.join(categories)}</p>
                <h2>Important Links</h2>
                <ul>
                    {''.join(html_links)}
                </ul>
                <p><i>Showing first 5000 characters. Full article has {len(page.text):,} characters.</i></p>
                """
            
                # Display content
                self.result_display.setHtml(html_content)

                # Download and display image
                image_url = self.get_page_image(page.title, selected_language)
                if image_url:
                    response = requests.get(image_url)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    if pixmap.height() > 300:
                        pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.clear()

                self.expand_button.setEnabled(True)
            else:
                self.result_display.setPlainText("Article not found.")
                self.image_label.clear()
                self.expand_button.setEnabled(False)
        else:
            self.result_display.clear()
            self.image_label.clear()
            self.expand_button.setEnabled(False)

    def handle_link_click(self, url):
        # Convert QUrl to string
        url_str = url.toString()
    
        # Parse the URL
        parsed_url = urlparse(url_str)
    
        # Check if it's a Wikipedia link
        if parsed_url.hostname and parsed_url.hostname.endswith('.wikipedia.org'):
            try:
                # Extract the language and title of the article
                lang = parsed_url.hostname.split('.')[0]
                title_encoded = parsed_url.path.split('/wiki/')[-1]
            
                # Decode title (replace spaces and special characters)
                title = unquote(title_encoded.replace('_', ' '))
            
                # Set the language and search for the article
                self.language_input.setText(lang)
                self.search_field.setText(title)
                self.perform_search()
            
            except Exception as e:
                print(f"Error processing Wikipedia link: {e}")
        else:
            # Open other links in your default browser
            QDesktopServices.openUrl(url)

    def show_full_article(self):
        html_content = self.full_article_text.replace('\n', '<br>')
        self.result_display.setHtml(html_content)
        self.expand_button.setEnabled(False)

    def get_page_image(self, title, language):
        try:
            url = f"https://{language}.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
            response = requests.get(url)
            data = response.json()
            pages = data['query']['pages']
            page_id = next(iter(pages))
            return pages[page_id].get('thumbnail', {}).get('source')
        except Exception as e:
            print(f"Error fetching image: {e}")
            return None

    def get_sections(self, page):
        return [s.title for s in page.sections if s.level == 2][:10]

    def get_categories(self, page):
        return [c.split(':')[-1] for c in page.categories.keys()][:15]

    def get_links(self, page):
        return [link for link in page.links.keys()][:20]

    def send_message(self):
        user_prompt = self.prompt_input.toPlainText().strip()
        if not user_prompt:
            self.answer_display.setPlainText("Please enter prompt.")
            return

        # Prevent another thread from starting if one is already running
        if getattr(self, 'llm_thread_running', False):
            return
        self.llm_thread_running = True

        final_prompt = f"{self.full_article_text}\n\n{user_prompt}"
        self.answer_display.setPlainText("Sending messages to LLM. Please be patient as it may take a while.")
        self.send_button.setEnabled(False)

        overrides = {
            "provider": "Local",
            "model": "Local Model",
            "max_tokens": 128000,
            "temperature": 1.0
        }

        # Starting the LLM thread
        self.llm_thread = LLMThread(final_prompt, overrides)
        self.llm_thread.response_signal.connect(self.update_llm_response)
        self.llm_thread.start()


    def update_llm_response(self, response):
        self.answer_display.setPlainText(response)
        self.send_button.setEnabled(True)
        self.llm_thread_running = False

    def open_find_dialog(self):
        if self.find_dialog is None:
            # Pass the widget in which to search (e.g. self.result_display)
            self.find_dialog = FindDialog(self.result_display, self)
        self.find_dialog.show()
        self.find_dialog.raise_()  # Ensure the dialog is on top
        self.find_dialog.search_field.setFocus()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = WikidataDialog()
    window.show()
    sys.exit(app.exec_())
