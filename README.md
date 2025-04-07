# Automation Tool

A powerful desktop automation tool designed to automate user actions including screen interactions, web browsing, and CAPTCHA handling. The tool supports multiple Chrome browser profiles, allowing automation across different user accounts.

## Features

- **Desktop Automation**: Click, type, scroll, drag, and other mouse/keyboard actions
- **Web Automation**: Browser navigation, form filling, element interaction
- **CAPTCHA Handling**: Image-based, text-based, and reCAPTCHA detection
- **Multiple Chrome Profiles**: Run automation across different browser user profiles
- **Script Editor**: Create and edit automation scripts with a user-friendly GUI
- **Recorder**: Record and save your actions as automation scripts
- **Script Player**: Execute automation scripts step-by-step or automatically

## Installation

### Windows Installation

1. Install Python 3.8 or newer from python.org
2. Clone this repository
3. Install required packages
4. Install Tesseract OCR for CAPTCHA handling

## Usage

### Starting the Application

Run the main application with:

```
python main.py
```

For systems without GUI support, you can use the console interface:

```
python simple_app.py
```

### Creating a Script

1. Start the application and click "New Script"
2. Add steps to your script by clicking "Add Step"
3. Choose the step type (Desktop, Web, CAPTCHA, Wait, etc.)
4. Configure the step properties
5. Save your script using File > Save

### Running a Script

1. Load a script using File > Open Script
2. Switch to the "Player" tab
3. Click "Run" to execute the script automatically, or "Step by Step" to run each step individually

### Recording a Script

1. Switch to the "Recorder" tab
2. Click "Start Recording"
3. Perform the actions you want to automate
4. Click "Stop Recording"
5. Save the recorded script

## Working with Chrome Profiles

To use multiple Chrome profiles:

1. Create profiles in Chrome by clicking your profile icon and selecting "Add"
2. In your script, add a "Web" step with the action "Start Browser with Profile"
3. Set the profile path to the Chrome user data directory for the desired profile

## License

This project is licensed under the MIT License - see the LICENSE file for details.
