import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle('Hello World App')
window.setGeometry(100, 100, 280, 80) # x, y, width, height

# Create a label widget
hello_label = QLabel('Hello World!', parent=window)

# Optional: Use a layout to manage the widget placement (good practice)
layout = QVBoxLayout()
layout.addWidget(hello_label)
window.setLayout(layout)

# Show the window
window.show()

# Start the application's event loop
sys.exit(app.exec()) 