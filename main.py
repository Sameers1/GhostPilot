import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                           QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QScreen, QPixmap

class HelloWorldApp(QWidget):
    """
    A Hello World application with screenshot functionality.
    Takes screenshots every 5 seconds when enabled.
    """
    def __init__(self):
        super().__init__()
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.take_screenshot)
        self.screenshots_active = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        try:
            # Set window properties
            self.setWindowTitle('Screenshot App')
            self.setGeometry(100, 100, 300, 150)
            
            # Create widgets
            self.hello_label = QLabel('Hello World!', parent=self)
            self.hello_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.status_label = QLabel('Screenshots: OFF', parent=self)
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.toggle_button = QPushButton('Start Screenshots', self)
            self.toggle_button.clicked.connect(self.toggle_screenshots)
            
            # Create layouts
            main_layout = QVBoxLayout()
            button_layout = QHBoxLayout()
            
            # Add widgets to layouts
            main_layout.addWidget(self.hello_label)
            main_layout.addWidget(self.status_label)
            button_layout.addWidget(self.toggle_button)
            main_layout.addLayout(button_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            print(f"Error initializing UI: {str(e)}")
            sys.exit(1)
    
    def toggle_screenshots(self):
        """Toggle screenshot functionality"""
        self.screenshots_active = not self.screenshots_active
        
        if self.screenshots_active:
            self.screenshot_timer.start(5000)  # 5000 ms = 5 seconds
            self.toggle_button.setText('Stop Screenshots')
            self.status_label.setText('Screenshots: ON')
        else:
            self.screenshot_timer.stop()
            self.toggle_button.setText('Start Screenshots')
            self.status_label.setText('Screenshots: OFF')
    
    def take_screenshot(self):
        """Take a screenshot of the primary screen"""
        try:
            # Create screenshots directory if it doesn't exist
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            
            # Get the primary screen
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshots/screenshot_{timestamp}.png'
            
            # Save the screenshot
            screenshot.save(filename, 'png')
            print(f'Screenshot saved: {filename}')
            
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")

def main():
    """Main function to run the application"""
    try:
        app = QApplication(sys.argv)
        window = HelloWorldApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 