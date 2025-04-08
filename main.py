import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class HelloWorldApp(QWidget):
    """
    A simple Hello World application using PyQt6.
    This class creates a window with a centered label displaying 'Hello World!'
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        try:
            # Set window properties
            self.setWindowTitle('Hello World App')
            self.setGeometry(100, 100, 280, 80)  # x, y, width, height
            
            # Create and configure the label
            self.hello_label = QLabel('Hello World!', parent=self)
            self.hello_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text
            
            # Set up the layout
            layout = QVBoxLayout()
            layout.addWidget(self.hello_label)
            self.setLayout(layout)
            
        except Exception as e:
            print(f"Error initializing UI: {str(e)}")
            sys.exit(1)

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