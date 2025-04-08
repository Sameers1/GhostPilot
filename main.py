import sys
import os
import base64
import requests
import keyboard
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                           QPushButton, QTextEdit, QSpinBox, QHBoxLayout,
                           QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QScreen

class GhostPilot(QWidget):
    """
    GhostPilot - AI-Powered Desktop Automation Assistant
    Takes screenshots and analyzes them using a local LLM (LLaVA) running in Docker.
    """
    def __init__(self):
        super().__init__()
        self.screenshot_active = False
        self.is_processing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.take_screenshot)
        self.hotkey = 'F10'  # Define hotkey before UI initialization
        self.init_ui()
        self.check_llm_status()
        # Setup global hotkey
        keyboard.add_hotkey('f10', self.take_single_screenshot)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('GhostPilot - AI Automation Assistant')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet('''
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QLabel {
                padding: 8px;
                border-radius: 6px;
                background-color: #313244;
                font-weight: 500;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QSpinBox {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 6px;
                padding: 4px;
                min-height: 24px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #45475a;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #74c7ec;
                selection-color: #1e1e2e;
            }
            QProgressBar {
                border: 2px solid #89b4fa;
                border-radius: 8px;
                text-align: center;
                height: 25px;
                margin: 8px;
                background-color: #313244;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #313244;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        ''')
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 8)
        
        # Status section
        status_layout = QHBoxLayout()
        status_layout.setSpacing(12)
        
        # Status label
        self.status_label = QLabel('Screenshots: OFF')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # Hotkey label
        self.hotkey_label = QLabel(f'Hotkey: {self.hotkey}')
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.hotkey_label)
        
        # LLM Status label
        self.llm_status = QLabel('LLM Status: Checking...')
        self.llm_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.llm_status)
        
        layout.addLayout(status_layout)
        
        # Interval control
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(12)
        interval_label = QLabel('Screenshot Interval (seconds):')
        self.interval_spinner = QSpinBox()
        self.interval_spinner.setRange(1, 60)
        self.interval_spinner.setValue(5)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinner)
        interval_layout.addStretch()
        
        layout.addLayout(interval_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Toggle button
        self.toggle_button = QPushButton('Start Monitoring')
        self.toggle_button.clicked.connect(self.toggle_screenshots)
        self.toggle_button.setFixedWidth(120)
        button_layout.addWidget(self.toggle_button)
        
        # Single screenshot button
        self.single_shot_button = QPushButton('Take Single Screenshot')
        self.single_shot_button.clicked.connect(self.take_single_screenshot)
        self.single_shot_button.setFixedWidth(120)
        button_layout.addWidget(self.single_shot_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('Analyzing screenshot... %p%')
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Analysis area
        self.analysis_area = QTextEdit()
        self.analysis_area.setReadOnly(True)
        self.analysis_area.setPlaceholderText("Screen analysis and automation suggestions will appear here...")
        self.analysis_area.setMinimumHeight(300)
        layout.addWidget(self.analysis_area, 1)
        
        # Credits section in a single line
        credits_layout = QHBoxLayout()
        credits_layout.setSpacing(20)
        
        credits_label = QLabel('Created by Sameer |')
        credits_label.setStyleSheet('background: transparent; color: #6c7086;')
        credits_layout.addWidget(credits_label)
        
        github_label = QLabel('<a href="https://github.com/Sameers1" style="color: #89b4fa; text-decoration: none;">GitHub: Sameers1</a> |')
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet('background: transparent;')
        credits_layout.addWidget(github_label)
        
        contact_label = QLabel('<a href="mailto:ssb.codex@gmail.com" style="color: #89b4fa; text-decoration: none;">Contact: ssb.codex@gmail.com</a>')
        contact_label.setOpenExternalLinks(True)
        contact_label.setStyleSheet('background: transparent;')
        credits_layout.addWidget(contact_label)
        
        credits_layout.addStretch()
        layout.addLayout(credits_layout)
        
        self.setLayout(layout)

    @pyqtSlot(str)
    def _append_text(self, text):
        """Thread-safe method to append text to the analysis area"""
        self.analysis_area.append(text)
        self.analysis_area.verticalScrollBar().setValue(
            self.analysis_area.verticalScrollBar().maximum()
        )

    def log_message(self, message):
        """Thread-safe logging to the analysis area"""
        QMetaObject.invokeMethod(
            self,
            "_append_text",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, message)
        )

    def check_llm_status(self):
        """Check if Ollama is available and LLaVA model is ready"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "llava",
                    "prompt": "Hi",
                    "stream": False
                }
            )
            if response.status_code == 200:
                self.llm_status.setText('LLM Status: LLaVA Ready')
                self.log_message("Connected to Ollama LLM (LLaVA model) successfully!")
            else:
                self.llm_status.setText('LLM Status: Error - Model Not Available')
                self.log_message("Error: Could not connect to LLaVA model. Please ensure it's installed:")
                self.log_message("Run: docker exec ollama ollama pull llava")
        except Exception as e:
            self.llm_status.setText('LLM Status: Error - Connection Failed')
            self.log_message("Error connecting to Ollama container. Please check:")
            self.log_message("1. Is Docker running?")
            self.log_message("2. Is the Ollama container running? (docker ps)")
            self.log_message("3. Run 'docker-compose up -d' to start the container")
            self.log_message(f"\nError details: {str(e)}")

    def toggle_screenshots(self):
        """Toggle screenshot capture and analysis"""
        self.screenshot_active = not self.screenshot_active
        if self.screenshot_active:
            interval = self.interval_spinner.value() * 1000  # Convert to milliseconds
            self.timer.start(interval)
            self.toggle_button.setText('Stop Monitoring')
            self.status_label.setText('Screenshots: ON')
            self.interval_spinner.setEnabled(False)
            self.log_message("Starting screen monitoring and analysis...")
        else:
            self.timer.stop()
            self.toggle_button.setText('Start Monitoring')
            self.status_label.setText('Screenshots: OFF')
            self.interval_spinner.setEnabled(True)
            self.log_message("Screen monitoring stopped.")

    def take_screenshot(self):
        """Capture and analyze screenshot"""
        try:
            # Get primary screen
            screen = QApplication.primaryScreen()
            if screen is not None:
                # Capture the screen
                screenshot = screen.grabWindow(0)
                
                # Create screenshots directory if it doesn't exist
                if not os.path.exists('screenshots'):
                    os.makedirs('screenshots')
                
                # Save with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'screenshots/screenshot_{timestamp}.png'
                screenshot.save(filename)
                
                # Analyze the screenshot
                self.analyze_screenshot(filename)
            else:
                self.log_message("Error: Could not get primary screen")
                
        except Exception as e:
            self.log_message(f"Error taking screenshot: {str(e)}")
    
    def take_single_screenshot(self):
        """Take a single screenshot and analyze it"""
        # Temporarily disable the monitoring if it's active
        was_active = self.screenshot_active
        if was_active:
            self.toggle_screenshots()
        
        # Take one screenshot
        self.take_screenshot()
        
        # Restore monitoring if it was active
        if was_active:
            self.toggle_screenshots()

    def analyze_screenshot(self, image_path):
        """Send screenshot to LLaVA for analysis using a separate thread"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.toggle_button.setEnabled(False)
        self.single_shot_button.setEnabled(False)
        
        # Create and configure analysis thread
        self.analysis_thread = AnalysisThread(image_path)
        self.analysis_thread.analysis_complete.connect(self._on_analysis_complete)
        self.analysis_thread.analysis_error.connect(self._on_analysis_error)
        self.analysis_thread.start()

    def _on_analysis_complete(self, result):
        self.log_message(result)
        self._reset_ui_state()

    def _on_analysis_error(self, error_message):
        self.log_message(error_message)
        self._reset_ui_state()

    def _reset_ui_state(self):
        self.progress_bar.hide()
        self.toggle_button.setEnabled(True)
        self.single_shot_button.setEnabled(True)
        self.is_processing = False

class AnalysisThread(QThread):
    analysis_complete = pyqtSignal(str)
    analysis_error = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        
    def run(self):
        try:
            # Read and encode the image
            with open(self.image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the request
            payload = {
                "model": "llava",
                "prompt": """Analyze this screenshot for automation opportunities:
1. Identify clickable elements (buttons, links, menus)
2. Note any text input fields
3. Describe the current application state
4. Suggest possible automation actions

Be concise and focus on actionable elements.""",
                "stream": False,
                "images": [image_data]
            }
            
            # Send to Ollama
            response = requests.post(
                'http://localhost:11434/api/generate',
                json=payload
            )
            
            if response.status_code == 200:
                analysis = response.json().get('response', 'No analysis provided')
                self.analysis_complete.emit(f"\nAnalysis of {os.path.basename(self.image_path)}:\n{analysis}\n")
            else:
                self.analysis_error.emit(f"Error: LLM returned status code {response.status_code}")
                
        except Exception as e:
            self.analysis_error.emit(f"Error analyzing screenshot: {str(e)}")

    @pyqtSlot(str)
    def _append_text(self, text):
        """Thread-safe method to append text to the analysis area"""
        self.analysis_area.append(text)
        self.analysis_area.verticalScrollBar().setValue(
            self.analysis_area.verticalScrollBar().maximum()
        )

    def log_message(self, message):
        """Thread-safe logging to the analysis area"""
        QMetaObject.invokeMethod(
            self,
            "_append_text",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, message)
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GhostPilot()
    window.show()
    sys.exit(app.exec())