# Voice Assistant (Jarvis)

A customizable voice assistant that can perform various tasks through voice commands. This assistant is designed to be platform-independent and work on most systems with basic Python support.

## Features

- **Voice Recognition**: Listens for voice commands and responds accordingly
- **Text-to-Speech**: Responds with natural-sounding speech
- **Website Navigation**: Opens various websites on command
- **Time and Date Information**: Tells the current time and date
- **Media Playback**: Plays music and videos on YouTube
- **Web Search**: Searches Google for information
- **Weather Information**: Gets current weather (requires API key)
- **Reminders**: Sets reminders for tasks
- **Jokes**: Tells random jokes for entertainment
- **News Headlines**: Gets the latest news (requires API key)
- **System Controls**: Adjusts volume, launches applications
- **Customization**: Changes voice, remembers user preferences
- **System Information**: Reports system details

## Installation

1. Clone or download this repository to your local machine
2. Install the required dependencies:

```bash
pip install SpeechRecognition pyttsx3 pygame pywhatkit requests
```

For additional features, you may need:

```bash
# For volume control on Windows
pip install pycaw

# For advanced microphone support
pip install PyAudio
```

## API Keys

Some features require free API keys:

1. **Weather Information**: Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. **News Headlines**: Get a free API key from [News API](https://newsapi.org/)

Add these keys to the corresponding variables in the script:

```python
WEATHER_API_KEY = "your_openweathermap_api_key"
NEWS_API_KEY = "your_news_api_key"  # Add this in the get_news method
```

## Usage

1. Run the script:

```bash
python voice_assistant.py
```

2. Wait for the greeting from the assistant
3. Start speaking commands using the wake word (default is "jarvis")
4. The assistant will process your command and respond accordingly

## Voice Commands

Here are some examples of commands you can use with the assistant:

### Basic Commands
- "jarvis, what time is it?"
- "jarvis, what's the date today?"
- "jarvis, who are you?"
- "jarvis, goodbye" (to exit)

### Web Navigation
- "jarvis, open youtube"
- "jarvis, open google"
- "jarvis, open facebook.com"

### Search
- "jarvis, search for python tutorials"
- "jarvis, look up recipe for chocolate cake"

### Media
- "jarvis, play Bohemian Rhapsody"
- "jarvis, play tutorial on machine learning"

### Information
- "jarvis, what's the weather like?"
- "jarvis, tell me the news"
- "jarvis, tell me a joke"
- "jarvis, system information"

### System Control
- "jarvis, volume up"
- "jarvis, volume down"
- "jarvis, mute"
- "jarvis, launch notepad" (Windows)
- "jarvis, launch safari" (macOS)

### Personalization
- "jarvis, call me John"
- "jarvis, change voice"

### Reminders
- "jarvis, remind me to take medicine at 8 PM"
- "jarvis, remind me about the meeting in 1 hour"

## Customization

You can customize various aspects of the assistant:

1. **Assistant Name**: Change the `ASSISTANT_NAME` constant at the top of the script
2. **Wake Word**: Change the `WAKE_WORD` constant (defaults to lowercase assistant name)
3. **Voice**: The assistant can cycle through available system voices with the "change voice" command
4. **Preferences**: User preferences are stored in a JSON file and can be edited manually

## Troubleshooting

- **Microphone Issues**: Make sure your microphone is properly connected and set as the default input device
- **Speech Recognition Failures**: Speak clearly and reduce background noise
- **Missing PyAudio**: If you encounter issues installing PyAudio, check platform-specific installation guides
- **API Limitations**: Free API keys have usage limits; check the respective API documentation

## Requirements

- Python 3.6+
- Internet connection (for speech recognition, web searches, APIs)
- Microphone
- Speakers

## License

This project is open source and available under the MIT License.
