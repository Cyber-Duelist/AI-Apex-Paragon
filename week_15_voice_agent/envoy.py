import sys
import threading
import json
from PyQt6.QtCore import QUrl, Qt, QThread, pyqtSignal, pyqtSlot, QEventLoop
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QSplitter)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from flask import Flask, request, jsonify

# --- INTERNAL API THREAD ---
# Runs a Flask server to receive commands from main.py (Entropy)
app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

class APIThread(QThread):
    # Signals to communicate with the main Qt GUI thread safely
    navigate_signal = pyqtSignal(str)
    read_dom_signal = pyqtSignal()
    click_signal = pyqtSignal(str)
    theme_signal = pyqtSignal(str)
    
    def __init__(self, browser_window):
        super().__init__()
        self.browser_window = browser_window
        
    def run(self):
        @app.route('/navigate', methods=['POST'])
        def navigate():
            url = request.json.get('url')
            if not url.startswith('http'):
                url = 'https://' + url
            self.navigate_signal.emit(url)
            return jsonify({"status": "navigating", "url": url})
            
        @app.route('/theme', methods=['POST'])
        def change_theme():
            theme = request.json.get('theme', 'dark')
            self.theme_signal.emit(theme)
            return jsonify({"status": "theme_changed", "theme": theme})
            
        @app.route('/page_text', methods=['GET'])
        def get_page_text():
            # We must wait for the Qt thread to return the text
            self.browser_window.dom_result = None
            self.read_dom_signal.emit()
            
            # Wait for Qt to fulfill the request
            while self.browser_window.dom_result is None:
                QThread.msleep(50)
                
            return jsonify({"text": self.browser_window.dom_result})
            
        @app.route('/click', methods=['POST'])
        def click_link():
            link_text = request.json.get('text', '')
            self.click_signal.emit(link_text)
            return jsonify({"status": "clicked", "target": link_text})

        @app.route('/listen', methods=['GET'])
        def listen_microphone():
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    print("ENVOY: Native Mic Listening...")
                    audio = r.listen(source, timeout=10, phrase_time_limit=15)
                text = r.recognize_google(audio)
                print(f"ENVOY: Heard -> {text}")
                return jsonify({"status": "success", "text": text})
            except sr.WaitTimeoutError:
                return jsonify({"status": "timeout", "text": ""})
            except sr.UnknownValueError:
                return jsonify({"status": "unrecognized", "text": ""})
            except Exception as e:
                print(f"ENVOY: Listen error -> {e}")
                return jsonify({"status": "error", "text": ""})

        # Run on port 8001 to avoid conflicting with FastAPI on 8000
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(host='127.0.0.1', port=8001, debug=False, use_reloader=False)


# --- MAIN GUI ---
class EnvoyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ENVOY - The Omni-Modal Browser")
        self.resize(1600, 900)
        
        self.dark_qss = """
            QMainWindow { background: #09090b; }
            QSplitter::handle { background-color: transparent; width: 8px; }
            QLineEdit {
                background-color: rgba(24, 24, 27, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-top: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 14px;
                padding: 12px 18px;
                color: #ffffff;
                font-size: 14px;
                font-family: 'Inter', sans-serif;
            }
            QLineEdit:focus { border: 1px solid rgba(99, 102, 241, 0.6); }
            QPushButton {
                background: transparent;
                border-radius: 10px;
                color: rgba(255, 255, 255, 0.55);
                font-weight: 500;
                padding: 10px;
                font-size: 16px;
                border: 1px solid transparent;
            }
            QPushButton:hover { background: rgba(39, 39, 42, 0.7); color: #ffffff; }
        """
        
        self.light_qss = """
            QMainWindow { background: #f8fafc; }
            QSplitter::handle { background-color: transparent; width: 8px; }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(0, 0, 0, 0.05);
                border-radius: 14px;
                padding: 12px 18px;
                color: #0f172a;
                font-size: 14px;
                font-family: 'Inter', sans-serif;
            }
            QLineEdit:focus { border: 1px solid rgba(79, 70, 229, 0.4); }
            QPushButton {
                background: transparent;
                border-radius: 10px;
                color: #64748b;
                font-weight: 500;
                padding: 10px;
                font-size: 16px;
                border: 1px solid transparent;
            }
            QPushButton:hover { background: rgba(0, 0, 0, 0.04); color: #0f172a; }
        """
        
        self.setStyleSheet(self.dark_qss)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Splitter separates AI Sidebar and Main Web Browser
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANEL: AI SIDEBAR (Arc Style) ---
        ai_panel = QWidget()
        ai_layout = QVBoxLayout(ai_panel)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        self.ai_view = QWebEngineView()
        
        # Auto-grant microphone and camera permissions for the AI view
        self.ai_view.page().featurePermissionRequested.connect(self.grant_permissions)
        self.ai_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        self.ai_view.setUrl(QUrl("http://127.0.0.1:8000"))
        ai_layout.addWidget(self.ai_view)
        
        # --- RIGHT PANEL: MAIN BROWSER (Arc Floating Rounded View) ---
        browser_panel = QWidget()
        browser_layout = QVBoxLayout(browser_panel)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        
        # Command Palette / Toolbar (SigmaOS Style)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 0, 10, 15)
        self.btn_back = QPushButton("◀")
        self.btn_forward = QPushButton("▶")
        self.btn_reload = QPushButton("↻")
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address...")
        
        toolbar_layout.addWidget(self.btn_back)
        toolbar_layout.addWidget(self.btn_forward)
        toolbar_layout.addWidget(self.btn_reload)
        toolbar_layout.addWidget(self.url_bar)
        
        # Web Engine View for the main browser
        self.web_view = QWebEngineView()
        
        # CRITICAL: Spoof Firefox User-Agent to force YouTube to serve VP9/WebM video formats
        # Since standard PyQt6 WebEngine does not contain proprietary H.264/MP4 codecs.
        self.web_view.page().profile().setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
        
        import os
        home_path = os.path.abspath("home.html")
        self.web_view.setUrl(QUrl.fromLocalFile(home_path))
        
        browser_layout.addLayout(toolbar_layout)
        browser_layout.addWidget(self.web_view)
        
        # Add to splitter
        splitter.addWidget(ai_panel)
        splitter.addWidget(browser_panel)
        
        # Set 25% / 75% width ratio
        splitter.setSizes([400, 1200])
        main_layout.addWidget(splitter)
        
        # Connect Browser Signals
        self.btn_back.clicked.connect(self.web_view.back)
        self.btn_forward.clicked.connect(self.web_view.forward)
        self.btn_reload.clicked.connect(self.web_view.reload)
        self.url_bar.returnPressed.connect(self.navigate_from_bar)
        self.web_view.urlChanged.connect(self.update_url_bar)

        # Start internal Flask API in background
        self.api_thread = APIThread(self)
        self.api_thread.navigate_signal.connect(self.navigate_from_ai)
        self.api_thread.read_dom_signal.connect(self.extract_dom_for_ai)
        self.api_thread.click_signal.connect(self.click_link_from_ai)
        self.api_thread.theme_signal.connect(self.change_theme)
        self.dom_result = None
        self.api_thread.start()

    def change_theme(self, theme):
        if theme == "light":
            self.setStyleSheet(self.light_qss)
        else:
            self.setStyleSheet(self.dark_qss)
        
        # Inject theme change into the AI Sidebar
        js_code = f"document.documentElement.setAttribute('data-theme', '{theme}');"
        self.ai_view.page().runJavaScript(js_code)

    def grant_permissions(self, securityOrigin, feature):
        self.ai_view.page().setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def navigate_from_bar(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.web_view.setUrl(QUrl(url))

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())

    @pyqtSlot(str)
    def navigate_from_ai(self, url):
        print(f"ENVOY: AI commanded navigation to {url}")
        self.web_view.setUrl(QUrl(url))

    @pyqtSlot()
    def extract_dom_for_ai(self):
        # Run JavaScript to extract visible text from the page
        js_code = "document.body.innerText;"
        
        def callback(result):
            self.dom_result = result if result else "No text found on page."
            
        self.web_view.page().runJavaScript(js_code, callback)

    @pyqtSlot(str)
    def click_link_from_ai(self, link_text):
        print(f"ENVOY: AI commanded clicking link: {link_text}")
        js_code = f"""
        (function() {{
            var query = "{link_text.lower()}";
            
            // Smart Heuristics for YouTube / Media Sites
            if (query === "video" || query.includes("first video") || query.includes("latest video")) {{
                var videoEl = document.querySelector('a#video-title, a#thumbnail, ytd-video-renderer a, ytd-grid-video-renderer a');
                if (videoEl) {{
                    videoEl.scrollIntoView({{behavior: "smooth", block: "center"}});
                    videoEl.click();
                    return "Clicked Video: " + (videoEl.innerText || videoEl.title || "Unknown Title");
                }}
            }}
            
            var elements = document.querySelectorAll('a, button, [role="button"], [role="link"], yt-formatted-string, h3, span');
            var target = null;
            var shortest = 999999;
            
            for (var i = 0; i < elements.length; i++) {{
                var el = elements[i];
                var text = (el.innerText || el.textContent || "").toLowerCase();
                
                // Ensure element is visible
                var rect = el.getBoundingClientRect();
                var isVisible = (rect.width > 0 && rect.height > 0);
                
                if (isVisible && text.includes(query)) {{
                    if (text.length < shortest) {{
                        target = el;
                        shortest = text.length;
                    }}
                }}
            }}
            
            if (target) {{
                target.scrollIntoView({{behavior: "smooth", block: "center"}});
                target.click();
                return "Clicked: " + (target.innerText || target.textContent).substring(0, 50);
            }}
            return "Element not found.";
        }})();
        """
        def callback(result):
            print(f"ENVOY: Click Result -> {result}")
            
        self.web_view.page().runJavaScript(js_code, callback)

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    window = EnvoyBrowser()
    window.show()
    sys.exit(qt_app.exec())
