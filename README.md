Sparky AI Assistant

Sparky is a voice-based AI assistant that utilizes speech recognition and the OpenAI GPT-3.5 model to engage in meaningful conversations with users. The assistant features a bilingual interface (English and Serbian) and can process speech input, respond intelligently, and display video feeds. Sparky is designed for interactive experiences, such as real-time AI conversations and multimedia display.

Features:
 - Bilingual Support: Operates in English and Serbian;
 - Speech Recognition: Accepts commands using the speech_recognition library;
 - Text-to-Speech: Provides verbal responses using pyttsx3 and gTTS;
 - AI-Powered Responses: Utilizes the OpenAI GPT-3.5 model;
 - Video Integration: Displays both live camera feeds and looping video content.

Installation Instructions:
 - To install the required packages, run the following command: pip install pyttsx3 SpeechRecognition openai gTTS Pillow opencv-python pygame

Setup Instructions:
 - Set your OpenAI API key;
 - Add a looping video file named video1.mp4 in the project directory.

Usage
 - Language Selection: Choose between English or Serbian;
 - User Name Input: Enter your name when prompted;
 - Voice Commands: Begin each command with the keyword Sparky. Example commands include: "Sparky, what is the weather today?", "Sparky, tell me a joke." Exit: Say "Sparky quit" or "Sparky exit" to close the application.
