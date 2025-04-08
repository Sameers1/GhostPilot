# GhostPilot - AI-Powered Desktop Automation Assistant

## Project Information
- **Creator**: Sameer
- **GitHub**: [Sameers1](https://github.com/Sameers1)
- **Email**: ssb.codex@gmail.com

## Project Vision
GhostPilot is an intelligent desktop automation assistant that:
1. Continuously monitors the screen through periodic screenshots
2. Processes these screenshots through a local LLM (Language Learning Model)
3. Executes automation tasks based on user commands and screen context
4. Provides a natural language interface for desktop automation

## Core Components
1. **Screen Monitoring System**
   - Takes periodic screenshots of the desktop
   - Maintains context of current screen state
   - Tracks changes and user interactions

2. **Local LLM Integration**
   - Runs in Docker container for easy deployment
   - Processes screenshots and user commands
   - Generates step-by-step automation instructions
   - Maintains context of ongoing tasks

3. **Automation Engine**
   - Executes instructions from LLM
   - Handles mouse and keyboard automation
   - Manages application windows and controls
   - Provides feedback on task progress

4. **User Interface**
   - Simple command input interface
   - Status display for ongoing tasks
   - Error reporting and feedback
   - Settings for customization

## Example Workflow
1. User types command: "Open YouTube and search for 'Imagine Dragons'"
2. GhostPilot:
   - Takes initial screenshot
   - Sends screenshot + command to LLM
   - LLM analyzes screen and generates instructions
   - Automation engine executes:
     - Opens browser
     - Navigates to YouTube
     - Types search query
     - Clicks search button
   - Continuously monitors progress through screenshots
   - Adjusts actions based on screen feedback

## Technical Stack
- **Frontend**: PyQt6 for GUI
- **Backend**: Python for automation
- **AI**: Local LLM in Docker
- **Screen Capture**: PyQt6 screen capture
- **Automation**: PyAutoGUI or similar
- **Communication**: REST API between components

## Development Goals
1. **Phase 1**: Basic screenshot and LLM integration
   - Implement screenshot capture
   - Set up local LLM in Docker
   - Basic command processing

2. **Phase 2**: Automation capabilities
   - Mouse and keyboard control
   - Window management
   - Basic task execution

3. **Phase 3**: Advanced features
   - Multi-step task handling
   - Error recovery
   - Context awareness
   - Learning from user corrections

## Contact
For collaboration or questions:
- GitHub: [Sameers1](https://github.com/Sameers1)
- Email: ssb.codex@gmail.com 