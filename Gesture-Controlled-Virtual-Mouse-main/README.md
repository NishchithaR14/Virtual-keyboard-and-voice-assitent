# Touchless HCI System Using Virtual Keyboard and Voice Assistant

A touchless Human-Computer Interaction (HCI) system that allows users to interact with a computer using hand gestures and voice commands, without physically touching a keyboard.

## Project Overview

This project combines a gesture-controlled virtual keyboard with a voice assistant to provide a contactless way of interacting with a computer.

The virtual keyboard uses a webcam to detect hand landmarks using MediaPipe and processes the camera frames using OpenCV. Hand gestures are mapped to keyboard keys, allowing users to type without physically touching a keyboard.

The voice assistant uses SpeechRecognition to convert speech into text and pyttsx3 to provide voice responses. It can execute predefined commands such as opening websites, searching the web, and performing system-related actions.

A Flask web interface is used to start and stop the different features.

## Features

- Gesture-controlled virtual keyboard
- Real-time hand tracking using MediaPipe
- 21 hand landmark detection
- Pinch-based key selection
- English, Hindi and Kannada keyboard support
- Kannada phonetic typing support
- Word suggestions
- Voice assistant
- Speech-to-text processing
- Text-to-speech responses
- Predefined voice commands
- Flask-based web interface
- Start / Stop controls for features

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- OpenCV
- MediaPipe
- SpeechRecognition
- pyttsx3
- PyAutoGUI
- Pynput
- NumPy

## How It Works

### 1. Virtual Keyboard

1. The webcam captures the user's hand.
2. OpenCV processes the camera frames.
3. MediaPipe detects the hand and its 21 landmarks.
4. The system tracks the finger positions.
5. A pinch gesture is detected.
6. The corresponding virtual keyboard key is selected.
7. The key press is sent to the system using keyboard automation.

### 2. Voice Assistant

1. The microphone captures the user's voice.
2. SpeechRecognition converts the speech into text.
3. The system checks the recognized command.
4. The corresponding predefined action is executed.
5. pyttsx3 provides voice feedback when required.

### 3. Flask Interface

The Flask application provides a simple interface from which the user can:

- Start the Gesture Keyboard
- Start the Voice Assistant
- Stop the running feature

## Main Components

```text
Project
│
├── src/
│   ├── main.py
│   ├── virtual_keyboard.py
│   ├── speechrecog.py
│   └── app.py
│
└── README.md
