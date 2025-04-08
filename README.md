# Hello World PyQt6 Application

A simple PyQt6 application that displays "Hello World!" in a window.

## Features
- Simple GUI window
- PyQt6-based interface
- Cross-platform compatible

## Requirements
- Python 3.x
- PyQt6

## Installation
```bash
pip install PyQt6
```

## Usage
Run the application:
```bash
python main.py
```

## Building Executable
To create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name HelloWorldApp main.py
```
The executable will be created in the `dist` folder. 