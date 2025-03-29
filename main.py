# Import necessary libraries
import speech_recognition as sr
import os
import pyttsx3
import webbrowser
import datetime
import re
import random
import json
import requests
from datetime import datetime, timedelta
import time
import platform
import subprocess
import sys
import threading

# Optional imports - will be used if available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False

# Constants
ASSISTANT_NAME = "Jarvis"  # Change this to whatever name you prefer
WEATHER_API_KEY = ""  # Add your OpenWeatherMap API key here
USER_PREFERENCES_FILE = "user_preferences.json"
WAKE_WORD = ASSISTANT_NAME.lower()

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant."""
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Set rate and volume
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 1.0)
        
        # Get available voices and set a voice
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)  # Default voice (usually male)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        
        # Load user preferences
        self.preferences = self.load_preferences()
        
        # Track if the assistant is active (listening for commands)
        self.active = True
        
        # Initialize audio features if pygame is available
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
    
    def load_preferences(self):
        """Load user preferences from file or create default."""
        try:
            with open(USER_PREFERENCES_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default preferences
            default_preferences = {
                "name": "User",
                "favorite_sites": {
                    "youtube": "https://www.youtube.com",
                    "google": "https://www.google.com",
                    "gmail": "https://mail.google.com",
                    "maps": "https://maps.google.com"
                },
                "reminders": [],
                "voice_index": 0,
                "news_sources": ["bbc-news", "cnn"],
                "location": "New York"  # Default location for weather
            }
            
            # Save default preferences
            with open(USER_PREFERENCES_FILE, 'w') as f:
                json.dump(default_preferences, f, indent=4)
            
            return default_preferences
    
    def save_preferences(self):
        """Save user preferences to file."""
        with open(USER_PREFERENCES_FILE, 'w') as f:
            json.dump(self.preferences, f, indent=4)
    
    def say(self, text):
        """Convert text to speech."""
        print(f"{ASSISTANT_NAME}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Listen for user input and convert to text."""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
            try:
                print("Recognizing...")
                query = self.recognizer.recognize_google(audio, language="en-US")
                print(f"User said: {query}")
                return query.lower()
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.say("Sorry, I'm having trouble accessing the speech recognition service.")
                return ""
            except Exception as e:
                print(f"Error: {str(e)}")
                return ""
    
    def greet(self):
        """Greet the user based on time of day."""
        hour = datetime.now().hour
        
        if 0 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        user_name = self.preferences.get("name", "")
        if user_name:
            greeting += f", {user_name}"
        
        self.say(f"{greeting}! I am {ASSISTANT_NAME}, your voice assistant. How can I help you today?")
    
    def process_command(self, command):
        """Process the user's command and take appropriate action."""
        if not command:
            return
        
        # Check for exit commands
        if any(phrase in command for phrase in ["exit", "quit", "goodbye", "bye", "stop"]):
            self.say(f"Goodbye! Have a great day.")
            self.active = False
            return
        
        # Check for wake word if not already in active command mode
        if WAKE_WORD not in command:
            return
        
        # Remove wake word from command for easier processing
        command = command.replace(WAKE_WORD, "").strip()
        
        # Open websites
        if "open" in command:
            self.open_website(command)
        
        # Get time
        elif any(phrase in command for phrase in ["what time", "current time", "what's the time"]):
            self.tell_time()
        
        # Get date
        elif any(phrase in command for phrase in ["what date", "current date", "what's the date", "what day is it"]):
            self.tell_date()
        
        # Play music/videos
        elif "play" in command:
            self.play_media(command)
        
        # Search the web
        elif "search" in command or "look up" in command or "find" in command:
            search_query = command.replace("search", "").replace("look up", "").replace("find", "").strip()
            self.search_web(search_query)
        
        # Weather information
        elif "weather" in command:
            self.get_weather()
        
        # Set a reminder
        elif "remind me" in command:
            self.set_reminder(command)
        
        # Tell a joke
        elif "joke" in command:
            self.tell_joke()
        
        # Get news
        elif "news" in command:
            self.get_news()
        
        # System controls
        elif any(phrase in command for phrase in ["volume up", "increase volume"]):
            self.adjust_volume(up=True)
        
        elif any(phrase in command for phrase in ["volume down", "decrease volume"]):
            self.adjust_volume(up=False)
        
        elif "mute" in command:
            self.adjust_volume(mute=True)
        
        # Launch applications
        elif "launch" in command or "start" in command or "open" in command:
            app_name = command.replace("launch", "").replace("start", "").replace("open", "").strip()
            self.launch_application(app_name)
        
        # Change assistant voice
        elif "change voice" in command:
            self.change_voice()
        
        # Get system information
        elif "system info" in command or "system information" in command:
            self.get_system_info()
        
        # Set user name
        elif "call me" in command:
            name = command.replace("call me", "").strip()
            self.set_user_name(name)
        
        # Introduce yourself
        elif any(phrase in command for phrase in ["who are you", "introduce yourself", "what can you do"]):
            self.introduce()
        
        # If no specific command is recognized
        else:
            self.say("I'm not sure how to help with that. Please try another command.")
    
    def open_website(self, command):
        """Open a website based on the command."""
        # Check if it's a favorite site
        for site_name, url in self.preferences["favorite_sites"].items():
            if site_name in command:
                self.say(f"Opening {site_name}")
                webbrowser.open(url)
                return
        
        # If not a favorite, try to extract the website name
        match = re.search(r'open\s+(?:the\s+)?(?:website\s+)?([a-zA-Z0-9\s]+)(?:\.com|\.org|\.net)?', command)
        if match:
            site = match.group(1).strip()
            self.say(f"Opening {site}")
            webbrowser.open(f"https://www.{site}.com")
        else:
            self.say("I couldn't understand which website to open.")
    
    def tell_time(self):
        """Tell the current time."""
        current_time = datetime.now().strftime("%I:%M %p")
        self.say(f"The current time is {current_time}")
    
    def tell_date(self):
        """Tell the current date."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.say(f"Today is {current_date}")
    
    def play_media(self, command):
        """Play music or videos based on the command."""
        if not PYWHATKIT_AVAILABLE:
            self.say("I'm sorry, but the pywhatkit module is not installed. Please install it to use this feature.")
            return
        
        # Extract the song/video name
        media = command.replace("play", "").strip()
        
        if not media:
            self.say("What would you like me to play?")
            return
        
        try:
            self.say(f"Playing {media} on YouTube")
            pywhatkit.playonyt(media)
        except Exception as e:
            self.say(f"I encountered an error: {str(e)}")
    
    def search_web(self, query):
        """Search the web for information."""
        if not query:
            self.say("What would you like me to search for?")
            return
        
        self.say(f"Searching for {query}")
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
    
    def get_weather(self):
        """Get weather information for the user's location."""
        if not WEATHER_API_KEY:
            self.say("Weather information is unavailable. Please add your OpenWeatherMap API key to the script.")
            return
        
        location = self.preferences.get("location", "New York")
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if data["cod"] != "404":
                main_data = data["main"]
                weather_data = data["weather"][0]
                temperature = main_data["temp"]
                description = weather_data["description"]
                
                self.say(f"The current weather in {location} is {description} with a temperature of {temperature} degrees Celsius.")
            else:
                self.say("Sorry, I couldn't find weather information for that location.")
        except Exception as e:
            self.say("I'm sorry, I couldn't retrieve the weather information at the moment.")
    
    def set_reminder(self, command):
        """Set a reminder based on the command."""
        # Extract text and time from the command
        match = re.search(r'remind me (?:to|about|that)?\s*(.+)(?:at|in|by)\s*(.+)', command)
        
        if not match:
            self.say("I didn't understand the reminder format. Please try something like 'remind me to take medicine at 8 PM'.")
            return
        
        reminder_text = match.group(1).strip()
        time_text = match.group(2).strip()
        
        # Add the reminder to preferences
        reminder = {
            "text": reminder_text,
            "time": time_text,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.preferences["reminders"].append(reminder)
        self.save_preferences()
        
        self.say(f"I'll remind you to {reminder_text} at {time_text}")
    
    def tell_joke(self):
        """Tell a random joke."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "How does a penguin build its house? Igloos it together!",
            "Why don't skeletons fight each other? They don't have the guts!"
        ]
        
        joke = random.choice(jokes)
        self.say(joke)
    
    def get_news(self):
        """Get the latest news headlines."""
        if not self.preferences.get("news_sources"):
            self.say("No news sources are configured. Please update your preferences.")
            return
        
        NEWS_API_KEY = ""  # Add your News API key here
        if not NEWS_API_KEY:
            self.say("News information is unavailable. Please add your News API key to the script.")
            return
        
        sources = ",".join(self.preferences["news_sources"])
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?sources={sources}&apiKey={NEWS_API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            if data["status"] == "ok" and data["articles"]:
                self.say("Here are the top news headlines:")
                
                for i, article in enumerate(data["articles"][:5]):  # Get top 5 headlines
                    self.say(f"{i+1}. {article['title']}")
                    time.sleep(1)  # Pause between headlines
            else:
                self.say("Sorry, I couldn't find any news headlines at the moment.")
        except Exception as e:
            self.say("I'm sorry, I couldn't retrieve the news at the moment.")
    
    def adjust_volume(self, up=None, mute=False):
        """Adjust system volume."""
        system = platform.system()
        
        if system == "Windows":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                if mute:
                    volume.SetMute(1, None)
                    self.say("Audio muted")
                elif up is not None:
                    if up:
                        self.say("Increasing volume")
                        # Increase by 10%
                        current_volume = volume.GetMasterVolumeLevelScalar()
                        new_volume = min(1.0, current_volume + 0.1)
                        volume.SetMasterVolumeLevelScalar(new_volume, None)
                    else:
                        self.say("Decreasing volume")
                        # Decrease by 10%
                        current_volume = volume.GetMasterVolumeLevelScalar()
                        new_volume = max(0.0, current_volume - 0.1)
                        volume.SetMasterVolumeLevelScalar(new_volume, None)
            except Exception as e:
                self.say("I couldn't adjust the volume. Make sure pycaw is installed.")
        
        elif system == "Darwin":  # macOS
            try:
                if mute:
                    os.system("osascript -e 'set volume output muted true'")
                    self.say("Audio muted")
                elif up is not None:
                    if up:
                        self.say("Increasing volume")
                        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
                    else:
                        self.say("Decreasing volume")
                        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
            except Exception as e:
                self.say("I couldn't adjust the volume")
        
        else:  # Linux and other systems
            self.say("Volume control is not implemented for this operating system")
    
    def launch_application(self, app_name):
        """Launch an application."""
        system = platform.system()
        
        if system == "Windows":
            try:
                # Common applications
                apps = {
                    "notepad": "notepad.exe",
                    "calculator": "calc.exe",
                    "paint": "mspaint.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "edge": "msedge.exe",
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe"
                }
                
                if app_name.lower() in apps:
                    app_path = apps[app_name.lower()]
                    self.say(f"Launching {app_name}")
                    os.startfile(app_path)
                else:
                    self.say(f"I don't know how to launch {app_name}")
            except Exception as e:
                self.say(f"I couldn't launch {app_name}")
        
        elif system == "Darwin":  # macOS
            try:
                # Common macOS applications
                apps = {
                    "safari": "Safari",
                    "chrome": "Google Chrome",
                    "firefox": "Firefox",
                    "terminal": "Terminal",
                    "notes": "Notes",
                    "calculator": "Calculator",
                    "word": "Microsoft Word",
                    "excel": "Microsoft Excel"
                }
                
                if app_name.lower() in apps:
                    app = apps[app_name.lower()]
                    self.say(f"Launching {app_name}")
                    os.system(f"open -a '{app}'")
                else:
                    self.say(f"I don't know how to launch {app_name}")
            except Exception as e:
                self.say(f"I couldn't launch {app_name}")
        
        else:  # Linux and other systems
            self.say("Application launching is not fully implemented for this operating system")
    
    def change_voice(self):
        """Change the voice of the assistant."""
        voices = self.engine.getProperty('voices')
        
        if not voices:
            self.say("No alternative voices found on your system")
            return
        
        # Cycle through available voices
        current_index = self.preferences.get("voice_index", 0)
        new_index = (current_index + 1) % len(voices)
        
        self.engine.setProperty('voice', voices[new_index].id)
        self.preferences["voice_index"] = new_index
        self.save_preferences()
        
        self.say(f"Voice changed. This is my new voice.")
    
    def get_system_info(self):
        """Get and report system information."""
        system_name = platform.system()
        node_name = platform.node()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()
        
        self.say(f"You are running {system_name} {release} on a {machine} machine.")
        self.say(f"Your computer name is {node_name}.")
    
    def set_user_name(self, name):
        """Set the user's name in preferences."""
        if name:
            self.preferences["name"] = name
            self.save_preferences()
            self.say(f"I'll call you {name} from now on.")
        else:
            self.say("I didn't catch your name.")
    
    def introduce(self):
        """Introduce the assistant and explain its capabilities."""
        self.say(f"I am {ASSISTANT_NAME}, your personal voice assistant. I can help you with various tasks like:")
        self.say("Opening websites, telling the time and date, playing music or videos, searching the web")
        self.say("Getting weather information, setting reminders, telling jokes, and getting news headlines")
        self.say("I can also adjust your system volume, launch applications, and get system information")
        self.say(f"Just start your command with '{WAKE_WORD}' and I'll be ready to help!")

    def run(self):
        """Run the voice assistant in a loop."""
        self.greet()
        
        while self.active:
            command = self.listen()
            self.process_command(command)

if __name__ == "__main__":
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nStopping the voice assistant...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")