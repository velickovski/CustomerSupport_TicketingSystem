# Real-Time Chat Application with TTS Integration

This project is a real-time chat application that utilizes Socket.IO for communication between the client and the server. The application also integrates Text-to-Speech (TTS) functionality using Parler TTS, which allows the chat responses to be read aloud in real-time as they are generated.

## Features

- **Real-time Messaging**: Communicate instantly with the server and other clients using Socket.IO.
- **Markdown Support**: Messages can be formatted using markdown syntax.
- **Text-to-Speech (TTS)**: The bot's responses can be spoken aloud using TTS, which is generated on the backend and streamed to the client.
- **TTS Toggle**: Users can toggle the TTS functionality on or off as needed.
- **Responsive Design**: The chat application is designed to be responsive and user-friendly on both desktop and mobile devices.

## Technologies Used

- **Frontend**:
  - HTML, CSS, JavaScript
  - [Socket.IO](https://socket.io/) for real-time communication
  - [Showdown.js](https://github.com/showdownjs/showdown) for markdown conversion
  - [Font Awesome](https://fontawesome.com/) for icons

- **Backend**:
  - Python (Flask or any preferred framework)
  - [Socket.IO](https://pypi.org/project/python-socketio/) for real-time communication
  - [Parler TTS](https://github.com/parler-tts/parler-tts) for Text-to-Speech
  - [PyTorch](https://pytorch.org/) for running the TTS model

## Installation

### Prerequisites

- Python 3.7+
- Node.js and npm
- A CUDA-enabled GPU (if you want to use GPU acceleration for TTS)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cognirum/LLamaGuard-TTS-OpenAI-DEMO-APP.git
   cd LLamaGuard-TTS-OpenAI-DEMO-APP


