# ============================================
# PROTON VOICE ASSISTANT - MAIN SERVICE
# Final Year Project 2025
# ============================================

import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import subprocess
from threading import Thread
import json
import logging
import requests
from collections import Counter

# Import custom modules
try:
    import Gesture_Controller
    import app
    import virtual_keyboard
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    filename='proton_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("=" * 60)
logging.info("PROTON VOICE ASSISTANT STARTED")
logging.info("=" * 60)

# ============================================
# CONFIGURATION MANAGEMENT
# ============================================
def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            logging.info("Configuration loaded successfully")
            return config
    except FileNotFoundError:
        logging.warning("config.json not found, creating default configuration")
        default_config = {
            "app_paths": {
                "notepad": "notepad.exe",
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            },
            "settings": {
                "wake_word": "proton",
                "voice_id": 0,
                "microphone_index": 0,
                "phrase_time_limit": 5,
                "language": "en-IN"
            },
            "user_info": {
                "name": "User",
                "location": "Mumbai"
            },
            "api_keys": {
                "openweather": "5eb95e3b6fc80323d9f72fb8781cdc1e",
                "news_api": "1689657fc02b4de9a310881d5ebaaa93"
            }
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing config.json: {e}")
        return {}

# Load configuration
config = load_config()

# ============================================
# OBJECT INITIALIZATION
# ============================================
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[config.get('settings', {}).get('voice_id', 0)].id)

# ============================================
# VARIABLES
# ============================================
file_exp_status = False
files = []
path = ''
is_awake = True

# ============================================
# PATH MAPS FROM CONFIG
# ============================================
app_paths = config.get('app_paths', {
    "notepad": "notepad.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
})

# ============================================
# ULTIMATE WEBSITES DICTIONARY
# ============================================
websites = {
    # Education
    "w3schools": "https://www.w3schools.com",
    "khan academy": "https://www.khanacademy.org",
    "coursera": "https://www.coursera.org",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "wikipedia": "https://www.wikipedia.org",
    
    # Google Services
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "classroom": "https://classroom.google.com",
    "drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "slides": "https://slides.google.com",
    "meet": "https://meet.google.com",
    "calendar": "https://calendar.google.com",
    "google": "https://google.com",
    
    # Productivity
    "canva": "https://www.canva.com",
    "notion": "https://www.notion.so",
    "trello": "https://trello.com",
    
    # PDF Tools
    "pdf to word": "https://www.ilovepdf.com/pdf_to_word",
    "word to pdf": "https://www.ilovepdf.com/word_to_pdf",
    "compress pdf": "https://www.ilovepdf.com/compress_pdf",
    
    # AI Tools
    "chatgpt": "https://chat.openai.com",
    "openai": "https://www.openai.com",
    "gemini": "https://gemini.google.com",
    "perplexity": "https://www.perplexity.ai",
    "blackbox ai": "https://www.blackbox.ai",
    
    # Social Media
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com",
    "twitter": "https://twitter.com",
    "linkedin": "https://linkedin.com",
    "reddit": "https://www.reddit.com",
    
    # Job Portals
    "linkedin jobs": "https://www.linkedin.com/jobs",
    "indeed": "https://www.indeed.com",
    "naukri": "https://www.naukri.com",
    "glassdoor": "https://www.glassdoor.com",
    
    # Shopping
    "amazon": "https://amazon.in",
    "flipkart": "https://flipkart.com",
    "myntra": "https://www.myntra.com",
    
    # Tech
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com"
}

# ============================================
# CATEGORIES MAPPING
# ============================================
categories = {
    "Education": ["w3schools", "khan academy", "coursera", "geeksforgeeks", "wikipedia"],
    "Google": ["youtube", "gmail", "classroom", "drive", "docs", "sheets", "slides", "meet", "calendar", "google"],
    "AI": ["chatgpt", "openai", "gemini", "perplexity", "blackbox ai"],
    "Social Media": ["instagram", "facebook", "twitter", "linkedin", "reddit"],
    "Job Portals": ["linkedin jobs", "indeed", "naukri", "glassdoor"],
    "Shopping": ["amazon", "flipkart", "myntra"],
    "Tech": ["github", "stackoverflow"]
}

number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

# ============================================
# COMMAND LOGGING & ANALYTICS
# ============================================
def log_command(command, status="success", category="general"):
    """Log every command for analytics"""
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "command": command,
        "status": status,
        "category": category
    }
    
    try:
        with open('command_history.json', 'a', encoding='utf-8') as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write('\n')
        logging.info(f"Command logged: {command} - {status}")
    except Exception as e:
        logging.error(f"Failed to log command: {e}")

def generate_usage_report():
    """Generate usage statistics"""
    try:
        with open('command_history.json', 'r', encoding='utf-8') as f:
            commands = [json.loads(line) for line in f]
        
        if not commands:
            return "No usage data available yet"
        
        total = len(commands)
        success = sum(1 for c in commands if c['status'] == 'success')
        categories_count = Counter(c.get('category', 'general') for c in commands)
        
        report = f"""
╔════════════════════════════════════════╗
║   PROTON USAGE STATISTICS              ║
╚════════════════════════════════════════╝

Total Commands: {total}
Successful: {success} ({success/total*100:.1f}%)
Failed: {total-success} ({(total-success)/total*100:.1f}%)

Command Categories:
"""
        for cat, count in categories_count.most_common():
            report += f"  • {cat}: {count} ({count/total*100:.1f}%)\n"
        
        return report
    except FileNotFoundError:
        return "No usage data available yet"
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return "Error generating statistics"

# ============================================
# WEATHER FEATURE
# ============================================
def get_weather(city=None):
    """Get current weather information"""
    if city is None:
        city = config.get("user_info", {}).get("location", "Mumbai")
    
    api_key = config.get("api_keys", {}).get("openweather", "")
    
    if not api_key:
        logging.warning("Weather API key not configured")
        return "Weather API key not configured. Please add to config.json"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        
        weather_msg = f"Weather in {city}: {temp}°C, feels like {feels_like}°C. {description}. Humidity: {humidity}%"
        
        logging.info(f"Weather fetched for {city}: {temp}°C")
        return weather_msg
        
    except requests.exceptions.Timeout:
        logging.error("Weather API timeout")
        return "Weather service is taking too long to respond"
    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API error: {e}")
        return "Unable to fetch weather information. Check your internet connection."
    except KeyError as e:
        logging.error(f"Weather data parsing error: {e}")
        return f"City '{city}' not found. Please check the spelling."

# ============================================
# CORE FUNCTIONS
# ============================================
import threading

# Thread-safe speak engine
engine_lock = threading.Lock()

def speak_text(text):
    """Thread-safe pyttsx3 speaker"""
    def run():
        with engine_lock:
            engine.say(text)
            engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

def reply(audio):
    """Send audio + voice output"""
    try:
        app.ChatBot.addAppMsg(audio)
        print(f"Proton: {audio}")
        speak_text(audio)
        logging.info(f"Response: {audio}")
    except Exception as e:
        logging.error(f"Error in reply: {e}")
        print(f"Proton: {audio}")


def wish():
    """Greet user based on time"""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")
    
    user_name = config.get("user_info", {}).get("name", "")
    if user_name and user_name != "User":
        reply(f"I am Proton, {user_name}. How may I help you?")
    else:
        reply("I am Proton, how may I help you?")

def record_audio():
    """Record and recognize audio from microphone"""
    mic_index = config.get('settings', {}).get('microphone_index', 0)
    phrase_limit = config.get('settings', {}).get('phrase_time_limit', 5)
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = r.listen(source, phrase_time_limit=phrase_limit)
        
        voice_data = r.recognize_google(audio)
        print(f"Recognized: {voice_data}")
        logging.info(f"Voice input: {voice_data}")
        return voice_data.lower()
        
    except sr.UnknownValueError:
        logging.warning("Could not understand audio")
        return ""
    except sr.RequestError as e:
        logging.error(f"Speech recognition service error: {e}")
        reply("Speech service unavailable. Check your internet connection.")
        return ""
    except Exception as e:
        logging.error(f"Error in record_audio: {e}")
        return ""

# ============================================
# CATEGORY WEBSITE SELECTION
# ============================================
def list_category(category_name):
    """List and open websites from a category"""
    if category_name not in categories:
        reply(f"Sorry, I don't have a category named {category_name}")
        logging.warning(f"Unknown category requested: {category_name}")
        return
    
    sites = categories[category_name]
    reply(f"Here are the websites in {category_name}:")
    
    for i, site in enumerate(sites, 1):
        print(f"{i}: {site}")
        reply(f"{i}: {site}")
    
    reply("Please say the number of the website you want to open.")
    voice_choice = record_audio()
    
    if not voice_choice:
        reply("I didn't hear a number. Please try again.")
        return
    
    voice_choice = voice_choice.strip().lower()
    
    # Convert spoken number words to digits
    if voice_choice in number_words:
        choice_num = number_words[voice_choice] - 1
    else:
        try:
            choice_num = int(voice_choice) - 1
        except ValueError:
            reply("Could not understand your choice. Please say a number.")
            logging.warning(f"Invalid choice: {voice_choice}")
            return
    
    # Check if choice is valid
    if 0 <= choice_num < len(sites):
        selected_site = sites[choice_num]
        reply(f"Opening {selected_site}")
        webbrowser.open(websites[selected_site])
        log_command(f"open {selected_site}", "success", "website")
    else:
        reply("Number out of range. Please try again.")
        logging.warning(f"Choice out of range: {choice_num}")

# ============================================
# MAIN RESPOND FUNCTION
# ============================================
def respond(voice_data):
    """Process and respond to voice commands"""
    global file_exp_status, files, is_awake, path
    
    print(f"Command: {voice_data}")
    voice_data = voice_data.replace('proton', '').strip()
    
    try:
        app.eel.addUserMsg(voice_data)
    except:
        pass
    
    # -------- WAKE UP COMMAND --------
    if not is_awake:
        if 'wake up' in voice_data:
            is_awake = True
            wish()
            log_command("wake up", "success", "system")
        return
    
    # -------- GREETINGS --------
    if 'hello' in voice_data or 'hi' in voice_data:
        wish()
        log_command("greeting", "success", "info")
        return
    
    elif 'what is your name' in voice_data or 'your name' in voice_data:
        reply('My name is Proton!')
        log_command("name query", "success", "info")
        return
    
    # -------- DATE & TIME --------
    elif 'date' in voice_data and 'update' not in voice_data:
        reply(today.strftime("%B %d, %Y"))
        log_command("date query", "success", "info")
        return
    
    elif 'time' in voice_data:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        reply(f"The time is {current_time}")
        log_command("time query", "success", "info")
        return
    
    # -------- WEATHER --------
    elif 'weather' in voice_data:
        city = None
        if ' in ' in voice_data:
            parts = voice_data.split(' in ')
            if len(parts) > 1:
                city = parts[1].strip()
        
        weather_info = get_weather(city)
        reply(weather_info)
        log_command(f"weather: {city or 'default'}", "success", "info")
        return
    
    # -------- USAGE STATISTICS --------
    elif 'usage stats' in voice_data or 'statistics' in voice_data or 'usage report' in voice_data:
        report = generate_usage_report()
        print(report)
        reply("Usage statistics generated. Check terminal or logs.")
        log_command("stats request", "success", "system")
        return
    
    # -------- SEARCH --------
    elif 'search' in voice_data:
        query = voice_data.replace("search", "").strip()
        if query:
            reply(f'Searching for {query}')
            webbrowser.open(f'https://google.com/search?q={query}')
            log_command(f"search: {query}", "success", "web")
        else:
            reply("What should I search for?")
        return
    
    # -------- YOUTUBE SEARCH --------
    elif 'youtube' in voice_data and 'search' in voice_data:
        query = voice_data.replace("youtube", "").replace("search", "").strip()
        if query:
            reply(f'Searching YouTube for {query}')
            webbrowser.open(f'https://www.youtube.com/results?search_query={query}')
            log_command(f"youtube search: {query}", "success", "web")
        else:
            webbrowser.open("https://youtube.com")
            log_command("open youtube", "success", "website")
        return
    
    # -------- LOCATION --------
    elif 'location' in voice_data or 'navigate' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        if temp_audio:
            app.eel.addUserMsg(temp_audio)
            reply(f'Locating {temp_audio}')
            url = f'https://google.nl/maps/place/{temp_audio}'
            webbrowser.open(url)
            log_command(f"location: {temp_audio}", "success", "web")
        return
    
    # -------- EXIT COMMANDS --------
    elif 'bye' in voice_data or 'by' in voice_data or 'goodbye' in voice_data:
        reply("Good bye! Have a nice day.")
        is_awake = False
        log_command("sleep", "success", "system")
        return
    
    elif 'exit' in voice_data or 'terminate' in voice_data or 'quit' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        reply("Shutting down. Goodbye!")
        log_command("shutdown", "success", "system")
        app.ChatBot.close()
        sys.exit()
    
    # -------- OPEN CATEGORIES --------
    for category in categories:
        if f"open {category.lower()}" in voice_data:
            list_category(category)
            return
    
    # -------- OPEN SPECIFIC WEBSITES --------
    for site in websites:
        if f"open {site}" in voice_data or f"{site}" in voice_data:
            reply(f"Opening {site}")
            webbrowser.open(websites[site])
            log_command(f"open {site}", "success", "website")
            return
    
    # -------- OPEN APPLICATIONS --------
    for appname, pathval in app_paths.items():
        if f"open {appname}" in voice_data or f"launch {appname}" in voice_data:
            reply(f"Opening {appname}")
            try:
                subprocess.Popen(pathval)
                log_command(f"open {appname}", "success", "app")
            except Exception as e:
                reply(f"Could not open {appname}. Check the path in config.")
                logging.error(f"Failed to open {appname}: {e}")
                log_command(f"open {appname}", "failed", "app")
            return
    
    # -------- GESTURE RECOGNITION --------
    if 'launch gesture' in voice_data or 'start gesture' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Gesture recognition launched successfully')
            log_command("launch gesture", "success", "system")
        return
    
    elif 'stop gesture' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
            log_command("stop gesture", "success", "system")
        else:
            reply('Gesture recognition is not active')
        return
    
    # -------- VIRTUAL KEYBOARD --------
    elif 'launch virtual keyboard' in voice_data or 'start keyboard' in voice_data:
        try:
            vk = virtual_keyboard.KeyboardGestureController()
            t = Thread(target=vk.start)
            t.start()
            reply("Virtual Keyboard launched successfully!")
            log_command("launch keyboard", "success", "system")
        except Exception as e:
            reply(f"Failed to launch virtual keyboard")
            logging.error(f"Keyboard launch error: {e}")
            log_command("launch keyboard", "failed", "system")
        return
    
    elif 'stop virtual keyboard' in voice_data or 'stop keyboard' in voice_data:
        try:
            virtual_keyboard.KeyboardGestureController.kg_mode = 0
            reply("Virtual Keyboard stopped.")
            log_command("stop keyboard", "success", "system")
        except Exception as e:
            reply("No virtual keyboard is currently running.")
            logging.error(f"Keyboard stop error: {e}")
        return
    
    # -------- KEYBOARD SHORTCUTS --------
    shortcuts = {
        "copy": 'c',
        "paste": 'v',
        "cut": 'x',
        "select all": 'a',
        "save": 's',
        "new tab": 't',
        "close tab": 'w',
        "switch tab": Key.tab
    }
    
    for key_name, key_value in shortcuts.items():
        if key_name in voice_data:
            with keyboard.pressed(Key.ctrl):
                keyboard.press(key_value)
                keyboard.release(key_value)
            reply(f"{key_name.title()} executed")
            log_command(f"shortcut: {key_name}", "success", "system")
            return
    
    # -------- SCROLL & SCREENSHOT --------
    if 'scroll down' in voice_data:
        keyboard.press(Key.page_down)
        keyboard.release(Key.page_down)
        reply("Scrolled down")
        log_command("scroll down", "success", "system")
        return
    
    elif 'scroll up' in voice_data:
        keyboard.press(Key.page_up)
        keyboard.release(Key.page_up)
        reply("Scrolled up")
        log_command("scroll up", "success", "system")
        return
    
    elif 'screenshot' in voice_data or 'capture screen' in voice_data:
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            reply(f"Screenshot saved as {filename}")
            log_command("screenshot", "success", "system")
        except Exception as e:
            reply("Failed to take screenshot")
            logging.error(f"Screenshot error: {e}")
        return
    
            # -------- FILE NAVIGATION (FIXED - WORKS FOR ALL FILES/FOLDERS) --------
    elif 'list' in voice_data or 'show files' in voice_data:
        counter = 0
        path = os.path.expanduser("~")
        try:
            files = listdir(path)
            filestr = ""
            for f in files:
                counter += 1
                print(f"{counter}: {f}")
                filestr += f"{counter}: {f}<br>"
            file_exp_status = True
            reply('These are the files in your home directory')
            app.ChatBot.addAppMsg(filestr)
            log_command("list files", "success", "system")
        except Exception as e:
            reply("Could not access files")
            logging.error(f"File list error: {e}")
        return
    
    elif file_exp_status:
        if 'open' in voice_data:
            # Extract the number from voice command
            parts = voice_data.split()
            file_number = None
            
            # Try to find a number in the command
            for part in parts:
                if part.isdigit():
                    file_number = int(part)
                    break
            
            if file_number is None:
                reply("Please say the file number after open")
                logging.warning("No file number provided in command")
                return
            
            # Convert to index (1-based to 0-based)
            index = file_number - 1
            
            if 0 <= index < len(files):
                file_to_open = files[index]
                full_path = os.path.join(path, file_to_open)
                
                print(f"DEBUG: Attempting to open #{file_number}: {file_to_open}")
                print(f"DEBUG: Full path: {full_path}")
                print(f"DEBUG: Exists: {os.path.exists(full_path)}")
                
                # Check if path exists and is accessible
                if os.path.exists(full_path):
                    try:
                        if os.path.isfile(full_path):
                            # It's a file - open it in default application
                            reply(f"Opening file {file_to_open}")
                            os.startfile(full_path)
                            file_exp_status = False
                            log_command(f"open file: {file_to_open}", "success", "system")
                            logging.info(f"Opened file: {full_path}")
                            
                        elif os.path.isdir(full_path):
                            # It's a folder - try multiple methods
                            reply(f"Opening folder {file_to_open}")
                            
                            success = False
                            
                            # Method 1: subprocess with explorer (most reliable)
                            try:
                                subprocess.Popen(['explorer', full_path])
                                success = True
                                logging.info(f"Opened folder (method 1): {full_path}")
                            except Exception as e1:
                                logging.warning(f"Method 1 failed: {e1}")
                            
                            # Method 2: subprocess with shell
                            if not success:
                                try:
                                    subprocess.Popen(f'explorer "{full_path}"', shell=True)
                                    success = True
                                    logging.info(f"Opened folder (method 2): {full_path}")
                                except Exception as e2:
                                    logging.warning(f"Method 2 failed: {e2}")
                            
                            # Method 3: os.system (last resort)
                            if not success:
                                try:
                                    os.system(f'start "" "{full_path}"')
                                    success = True
                                    logging.info(f"Opened folder (method 3): {full_path}")
                                except Exception as e3:
                                    logging.warning(f"Method 3 failed: {e3}")
                            
                            if success:
                                file_exp_status = False
                                log_command(f"open folder: {file_to_open}", "success", "system")
                            else:
                                reply("Could not open folder. Check permissions.")
                                logging.error(f"All methods failed for: {full_path}")
                            
                        else:
                            # Not a regular file or folder (could be symlink, device, etc.)
                            reply(f"{file_to_open} is not a regular file or folder")
                            logging.warning(f"Unknown file type: {full_path}")
                            
                    except PermissionError:
                        reply('No permission to access this file or folder')
                        logging.error(f"Permission denied: {full_path}")
                    except Exception as e:
                        reply(f"Error opening {file_to_open}")
                        logging.error(f"File open error: {e}")
                else:
                    # Path doesn't exist or is inaccessible
                    reply(f"{file_to_open} does not exist or cannot be accessed")
                    logging.error(f"Path does not exist or is inaccessible: {full_path}")
            else:
                reply(f"File number {file_number} is out of range. Please choose between 1 and {len(files)}")
                logging.warning(f"File number out of range: {file_number}")
            
            return



# ============================================
# DRIVER CODE
# ============================================
if __name__ == "__main__":
    try:
        # Start GUI thread
        t1 = Thread(target=app.ChatBot.start)
        t1.start()
        
        # Wait for GUI to initialize
        while not app.ChatBot.started:
            time.sleep(0.5)
        
        # Initial greeting
        wish()
        
        # Main loop
        while True:
            if app.ChatBot.isUserInput():
                voice_data = app.ChatBot.popUserInput()
            else:
                voice_data = record_audio()
            
            wake_word = config.get('settings', {}).get('wake_word', 'proton')
            
            if wake_word in voice_data:
                try:
                    respond(voice_data)
                except SystemExit:
                    reply("Exiting successfully")
                    logging.info("System exit requested")
                    break
                except Exception as e:
                    logging.error(f"Error in main loop: {e}", exc_info=True)
                    reply("An error occurred. Please try again.")
    
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt - shutting down")
        reply("Shutting down")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Critical error in main: {e}", exc_info=True)
        print(f"Critical error: {e}")
        sys.exit(1) 