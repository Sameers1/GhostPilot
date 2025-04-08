import sys
import os
import base64
import requests
import keyboard
import hashlib
import psutil
import GPUtil
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                           QPushButton, QTextEdit, QSpinBox, QHBoxLayout,
                           QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QScreen, QImage

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
        self.analysis_cache = {}
        self.cache_timeout = timedelta(minutes=5)
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
        
        # Status labels container
        status_container = QWidget()
        status_container.setStyleSheet('background: transparent;')
        status_container_layout = QHBoxLayout(status_container)
        status_container_layout.setSpacing(12)
        status_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label
        self.status_label = QLabel('Screenshots: OFF')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumWidth(120)
        status_container_layout.addWidget(self.status_label)
        
        # Hotkey label
        self.hotkey_label = QLabel(f'Hotkey: {self.hotkey}')
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_label.setMinimumWidth(100)
        status_container_layout.addWidget(self.hotkey_label)
        
        # LLM Status label
        self.llm_status = QLabel('LLM Status: Checking...')
        self.llm_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.llm_status.setMinimumWidth(150)
        status_container_layout.addWidget(self.llm_status)
        
        # CPU/GPU Usage labels
        self.cpu_label = QLabel('CPU: 0%')
        self.cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cpu_label.setMinimumWidth(80)
        status_container_layout.addWidget(self.cpu_label)
        
        self.gpu_label = QLabel('GPU: N/A')
        self.gpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gpu_label.setMinimumWidth(80)
        status_container_layout.addWidget(self.gpu_label)
        
        status_layout.addWidget(status_container)
        
        # Create timer for updating system stats
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(2000)  # Update every 2 seconds
        
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
        self.toggle_button = QPushButton('Start\nMonitoring')
        self.toggle_button.clicked.connect(self.toggle_screenshots)
        self.toggle_button.setFixedWidth(100)
        self.toggle_button.setFixedHeight(50)
        button_layout.addWidget(self.toggle_button)
        
        # Single screenshot button
        self.single_shot_button = QPushButton('Take Single\nScreenshot')
        self.single_shot_button.clicked.connect(self.take_single_screenshot)
        self.single_shot_button.setFixedWidth(100)
        self.single_shot_button.setFixedHeight(50)
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

    def update_system_stats(self):
        """Update CPU and GPU usage stats"""
        # Update CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_label.setText(f'CPU: {cpu_percent}%')
        
        # Update GPU usage if available
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Get first GPU
                self.gpu_label.setText(f'GPU: {gpu.load*100:.0f}%')
            else:
                self.gpu_label.setText('GPU: N/A')
        except:
            self.gpu_label.setText('GPU: N/A')
    
    def toggle_screenshots(self):
        """Toggle screenshot capture and analysis"""
        self.screenshot_active = not self.screenshot_active
        if self.screenshot_active:
            interval = self.interval_spinner.value() * 1000  # Convert to milliseconds
            self.timer.start(interval)
            self.toggle_button.setText('Stop\nMonitoring')
            self.status_label.setText('Screenshots: ON')
            self.interval_spinner.setEnabled(False)
            self.log_message("Starting screen monitoring and analysis...")
        else:
            self.timer.stop()
            self.toggle_button.setText('Start\nMonitoring')
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
                
                # Show resizing status
                self.progress_bar.show()
                self.progress_bar.setRange(0, 0)
                self.progress_bar.setFormat('Resizing screenshot...')
                self.log_message("Resizing screenshot for analysis...")
                
                # Resize the screenshot to reduce processing time
                scaled_width = 1024  # Reduced width while maintaining aspect ratio
                scaled_screenshot = screenshot.scaled(scaled_width, 
                                                    scaled_width * screenshot.height() // screenshot.width(),
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)
                
                # Convert to QImage for efficient processing
                image = scaled_screenshot.toImage()
                
                # Calculate image hash for caching
                image_bytes = image.constBits().asstring(image.sizeInBytes())
                image_hash = hashlib.md5(image_bytes).hexdigest()
                
                # Check cache before processing
                cache_entry = self.analysis_cache.get(image_hash)
                if cache_entry and (datetime.now() - cache_entry['timestamp']) < self.cache_timeout:
                    self.progress_bar.hide()
                    self.log_message(cache_entry['analysis'])
                    return
                
                # Create screenshots directory if it doesn't exist
                if not os.path.exists('screenshots'):
                    os.makedirs('screenshots')
                
                # Save with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'screenshots/screenshot_{timestamp}.png'
                scaled_screenshot.save(filename)
                
                # Update progress bar for analysis phase
                self.progress_bar.setFormat('Analyzing with LLM...')
                self.log_message("Sending to LLM for analysis...")
                
                # Analyze the screenshot
                self.analyze_screenshot(filename, image_hash)
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

    def analyze_screenshot(self, image_path, image_hash=None):
        """Send screenshot to LLaVA for analysis using a separate thread"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.toggle_button.setEnabled(False)
        self.single_shot_button.setEnabled(False)
        
        # Create and configure analysis thread
        self.analysis_thread = AnalysisThread(image_path, image_hash)
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
    
    def __init__(self, image_path, image_hash=None):
        super().__init__()
        self.image_path = image_path
        self.image_hash = image_hash
        
    def run(self):
        try:
            # Read and encode the image
            with open(self.image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the request with a more focused prompt
            payload = {
                "model": "llava",
                "prompt": "Identify UI elements and automation opportunities. List clickable items, input fields, and key actions. Be brief and specific.",
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
                result = f"\nAnalysis of {os.path.basename(self.image_path)}:\n{analysis}\n"
                
                # Update cache if hash is provided
                if self.image_hash:
                    window.analysis_cache[self.image_hash] = {
                        'analysis': result,
                        'timestamp': datetime.now()
                    }
                
                self.analysis_complete.emit(result)
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