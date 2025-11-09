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
import Gesture_Controller
import app
from threading import Thread
import subprocess
import virtual_keyboard

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status

# ----------------- Path Maps ---------------------
app_paths = {
    "whatsapp": r"C:\Users\YourName\AppData\Local\WhatsApp\WhatsApp.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "vs code": r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad": "notepad.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe"
}

# ----------------- Ultimate Websites Dictionary ---------------------
websites = {
    # Education
    "w3schools": "https://www.w3schools.com",
    "khan academy": "https://www.khanacademy.org",
    "coursera": "https://www.coursera.org",
    "edx": "https://www.edx.org",
    "udemy": "https://www.udemy.com",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "wikipedia": "https://www.wikipedia.org",
    
    # Google
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "classroom": "https://classroom.google.com",
    "drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "slides": "https://slides.google.com",
    "meet": "https://meet.google.com",
    "calendar": "https://calendar.google.com",
    "photos": "https://photos.google.com",
    "keep": "https://keep.google.com",
    "translate": "https://translate.google.com",
    "news": "https://news.google.com",
    "google": "https://google.com",
    
    # Productivity
    "word online": "https://office.live.com/start/Word.aspx",
    "excel online": "https://office.live.com/start/Excel.aspx",
    "powerpoint online": "https://office.live.com/start/PowerPoint.aspx",
    "canva": "https://www.canva.com",
    "notion": "https://www.notion.so",
    "trello": "https://trello.com",
    "slack": "https://slack.com",
    
    # PDF / Word / Document Conversion
    "pdf to word": "https://www.ilovepdf.com/pdf_to_word",
    "word to pdf": "https://www.ilovepdf.com/word_to_pdf",
    "pdf merge": "https://www.ilovepdf.com/merge_pdf",
    "word merge": "https://www.mergeword.com",
    "pdf split": "https://www.ilovepdf.com/split_pdf",
    "compress pdf": "https://www.ilovepdf.com/compress_pdf",
    "pdf to jpg": "https://www.ilovepdf.com/pdf_to_jpg",
    "jpg to pdf": "https://www.ilovepdf.com/jpg_to_pdf",
    "pdf editor": "https://www.pdfescape.com",
    "online converter": "https://www.online-convert.com",
    "convertio": "https://convertio.co",
    "smallpdf": "https://smallpdf.com",
    "zamzar": "https://www.zamzar.com",
    
    # AI Tools
    "chatgpt": "https://chat.openai.com",
    "openai": "https://www.openai.com",
    "bard": "https://bard.google.com",
    "midjourney": "https://www.midjourney.com",
    "dall-e": "https://openai.com/dall-e",
    "huggingface": "https://huggingface.co",
    "runway ml": "https://runwayml.com",
    "copy.ai": "https://www.copy.ai",
    "jasper ai": "https://www.jasper.ai",
    "replit": "https://replit.com",
    "gemini": "https://www.gemini.ai",
    "perplexity": "https://www.perplexity.ai",
    "grok ai": "https://grok.ai",
    "blackbox ai": "https://blackbox.ai",
    
    # Social Media
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com",
    "twitter": "https://twitter.com",
    "linkedin": "https://linkedin.com",
    "snapchat": "https://www.snapchat.com",
    "reddit": "https://www.reddit.com",
    
    # Job Portals
    "linkedin jobs": "https://www.linkedin.com/jobs",
    "indeed": "https://www.indeed.com",
    "naukri": "https://www.naukri.com",
    "monster": "https://www.monster.com",
    "glassdoor": "https://www.glassdoor.com",
    "times jobs": "https://www.timesjobs.com",
    "shine": "https://www.shine.com",
    
    # Shopping / Makeup
    "amazon": "https://amazon.in",
    "flipkart": "https://flipkart.com",
    "nykaa": "https://www.nykaa.com",
    "myntra": "https://www.myntra.com",
    "sephora": "https://www.sephora.com",
    
    # Photo / Video Editing
    "pixlr": "https://pixlr.com",
    "fotor": "https://www.fotor.com",
    "beFunky": "https://www.befunky.com",
    "adobe express": "https://www.adobe.com/express",
    "photopea": "https://www.photopea.com",
    "picksart": "https://www.picksart.com",
    "canva": "https://www.canva.com",
    
    # Others / Tech
    "github": "https://github.com",
    "gitlab": "https://gitlab.com",
    "stackoverflow": "https://stackoverflow.com",
    "techcrunch": "https://techcrunch.com",
    "product hunt": "https://www.producthunt.com"
}

# ----------------- Categories Mapping ---------------------
categories = {
    "Education": ["w3schools", "khan academy", "coursera", "edx", "udemy", "geeksforgeeks", "wikipedia"],
    "Google": ["youtube", "gmail", "classroom", "drive", "docs", "sheets", "slides", "meet", "calendar", "photos", "keep", "translate", "news", "google"],
    "Productivity": ["word online", "excel online", "powerpoint online", "canva", "notion", "trello", "slack"],
    "PDF Tools": ["pdf to word", "word to pdf", "pdf merge", "word merge", "pdf split", "compress pdf", "pdf to jpg", "jpg to pdf", "pdf editor", "online converter", "convertio", "smallpdf", "zamzar"],
    "AI": ["chatgpt", "openai", "bard", "midjourney", "dall-e", "huggingface", "runway ml", "copy.ai", "jasper ai", "replit", "gemini", "perplexity", "grok ai", "blackbox ai"],
    "Social Media": ["instagram", "facebook", "twitter", "linkedin", "snapchat", "reddit"],
    "Job Portals": ["linkedin jobs", "indeed", "naukri", "monster", "glassdoor", "times jobs", "shine"],
    "Shopping": ["amazon", "flipkart", "nykaa", "myntra", "sephora"],
    "Photo Editing": ["pixlr", "fotor", "beFunky", "adobe express", "photopea", "picksart", "canva"],
    "Tech": ["github", "gitlab", "stackoverflow", "techcrunch", "product hunt"]
}

number_words = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10
}

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
    reply("I am Proton, how may I help you?")

def record_audio():
    with sr.Microphone(device_index=0) as source:  
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=5)

    voice_data = ""
    try:
        voice_data = r.recognize_google(audio)
        print(f"Recognized: {voice_data}")
    except:
        pass
    return voice_data.lower()

# ----------------- Category Website Selection ---------------------
# ----------------- Category Website Selection ---------------------
def list_category(category_name):
    if category_name not in categories:
        reply(f"Sorry, I don't have a category named {category_name}")
        return
    sites = categories[category_name]
    reply(f"Here are the websites in {category_name}:")
    for i, site in enumerate(sites, 1):
        print(f"{i}: {site}")
        reply(f"{i}: {site}")
    
    # Ask user for number
    reply("Please say the number of the website you want to open.")
    voice_choice = record_audio()  # Listen to user
    voice_choice = voice_choice.strip().lower()

    # Convert spoken number words to digits
    if voice_choice in number_words:
        choice_num = number_words[voice_choice] - 1
    else:
        try:
            choice_num = int(voice_choice) - 1
        except:
            reply("Could not understand your choice. Please say a number.")
            return

    # Check if choice is valid
    if 0 <= choice_num < len(sites):
        selected_site = sites[choice_num]
        reply(f"Opening {selected_site}...")
        webbrowser.open(websites[selected_site])
    else:
        reply("Number out of range. Please try again.")

    
 
# ----------------- Respond Function ---------------------
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print("Command:", voice_data)
    voice_data = voice_data.replace('proton', '').strip()
    app.eel.addUserMsg(voice_data)

    if not is_awake:
        if 'wake up' in voice_data:
            is_awake = True
            wish()
        return

    # Greetings & Info
    if 'hello' in voice_data:
        wish()
        return
    elif 'what is your name' in voice_data:
        reply('My name is Proton!')
        return
    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))
        return
    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])
        return

    # Search & Location
    if 'search' in voice_data:
        query = voice_data.replace("search", "")
        reply('Searching for ' + query)
        webbrowser.open('https://google.com/search?q=' + query)
        return

    if 'search' in voice_data:
        query = voice_data.replace("search", "")
        reply('Searching for ' + query)
        webbrowser.open('https://www.youtube.com/' + query)
        return

    if 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio
        webbrowser.open(url)
        return

    # Exit Commands
    if ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False
        return
    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()

    # -------- OPEN CATEGORIES --------
    for category in categories:
        if f"open {category.lower()}" in voice_data:
            list_category(category)
            return

    # -------- OPEN SPECIFIC WEBSITES --------
    for site in websites:
        if f"open {site}" in voice_data:
            reply(f"Opening {site}")
            webbrowser.open(websites[site])
            return

    # -------- OPEN APPLICATIONS --------
    for appname, pathval in app_paths.items():
        if f"open {appname}" in voice_data:
            reply(f"Opening {appname}")
            try:
                subprocess.Popen(pathval)
            except:
                reply(f"Could not open {appname}, check path")
            return

    # -------- Gesture Recognition --------
    if 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched Successfully')
        return

    elif 'stop gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        return
    
    elif 'launch virtual keyboard' in voice_data:
        try:
            vk = virtual_keyboard.KeyboardGestureController()  # Create a new instance
            t = Thread(target=vk.start)  # Run in background thread
            t.start()
            reply("Virtual Keyboard launched successfully!")
        except Exception as e:
            reply(f"Failed to launch virtual keyboard: {e}")

    elif 'stop virtual keyboard' in voice_data:
        try:
            virtual_keyboard.KeyboardGestureController.kg_mode = 0  # Stop loop
            reply("Virtual Keyboard stopped.")
        except:
            reply("No virtual keyboard is currently running.")

    # -------- Keyboard Shortcuts --------
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
    for key in shortcuts:
        if key in voice_data:
            with keyboard.pressed(Key.ctrl):
                keyboard.press(shortcuts[key])
                keyboard.release(shortcuts[key])
            reply(key.capitalize() + " executed")
            return

    # -------- Scroll / Screenshot --------
    if 'scroll down' in voice_data:
        keyboard.press(Key.page_down); keyboard.release(Key.page_down)
        reply("Scrolled down")
        return
    elif 'scroll up' in voice_data:
        keyboard.press(Key.page_up); keyboard.release(Key.page_up)
        reply("Scrolled up")
        return
    elif 'screenshot' in voice_data:
        pyautogui.screenshot("screenshot.png")
        reply("Screenshot taken")
        return

    # -------- File Navigation --------
    elif 'list' in voice_data:
        counter = 0
        path = os.path.expanduser("~")
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ': ' + f)
            filestr += str(counter) + ': ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status:
        if 'open' in voice_data:
            parts = voice_data.split()
            if parts[-1].isdigit():
                index = int(parts[-1]) - 1
                if 0 <= index < len(files):
                    file_to_open = files[index]
                    full_path = os.path.join(path, file_to_open)
                    if isfile(full_path):
                        os.startfile(full_path)
                        file_exp_status = False
                    else:
                        try:
                            path = os.path.join(path, file_to_open)
                            files = listdir(path)
                        except:
                            reply('No permission to access this folder')
            else:
                reply("Please say the file number after open")

        elif 'back' in voice_data:
            if path == 'C://':
                reply('This is the root directory')
            else:
                path = os.path.dirname(path)
                files = listdir(path)
                reply('Went back')
                file_exp_status = True

    else:
        reply('I am not functioned to do this!')

# ------------------Driver Code--------------------
t1 = Thread(target=app.ChatBot.start)
t1.start()

while not app.ChatBot.started:
    time.sleep(0.5)

wish()

while True:
    if app.ChatBot.isUserInput():
        voice_data = app.ChatBot.popUserInput()
    else:
        voice_data = record_audio()

    if 'proton' in voice_data:
        try:
            respond(voice_data)
        except SystemExit:
            reply("Exit Successful")
            break
        except Exception as e:
            print("Exception:", e)
            break
