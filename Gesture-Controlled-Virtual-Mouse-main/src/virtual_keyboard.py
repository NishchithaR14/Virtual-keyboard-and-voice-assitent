import cv2
import mediapipe as mp
import math
import pyautogui
import time
from playsound import playsound
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os
import cv2
cv2.startWindowThread()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils


# Helper: Load Wordlists
def load_wordlist(language):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "wordlists", f"{language.lower()}_words.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        return words
    else:
        print(f"⚠️ {language} wordlist not found!")
        return []


class KeyboardGestureController:
    def __init__(self):
        self.kg_mode = 1
        self.last_pressed_key = None
        self.last_pressed_time = 0
        self.typed_text = ""
        self.languages = ["English", "Hindi", "Kannada"]
        self.current_language = 0
        self.suggestion_boxes = []

        self.active_modifiers = set()  # 'ctrl', 'shift', 'alt'

        self.caps_on = False  # Track Caps Lock state

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        try:
            self.font_eng = ImageFont.truetype("arial.ttf", 28)
            self.font_hin = ImageFont.truetype(os.path.join(BASE_DIR, "NotoSansDevanagari-Regular.ttf"), 28)
            self.font_kan = ImageFont.truetype(os.path.join(BASE_DIR, "NotoSansKannada-Regular.ttf"), 28)
        except OSError:
            print("⚠️ Font files not found! Place NotoSansDevanagari-Regular.ttf and NotoSansKannada-Regular.ttf in same folder")
            raise

        self.hin_map = {'A':'अ','B':'ब','C':'क','D':'द','E':'ए','F':'फ','G':'ग',
                        'H':'ह','I':'इ','J':'ज','K':'क','L':'ल','M':'म','N':'न',
                        'O':'ओ','P':'प','Q':'क','R':'र','S':'स','T':'त','U':'उ',
                        'V':'व','W':'व','X':'क्ष','Y':'य','Z':'ज़',' ':' ','\n':'\n'}

        self.kan_map = {'A':'ಅ','B':'ಬ','C':'ಕ','D':'ದ','E':'ಎ','F':'ಫ','G':'ಗ',
                        'H':'ಹ','I':'ಇ','J':'ಜ','K':'ಕ','L':'ಲ','M':'ಮ','N':'ನ',
                        'O':'ಒ','P':'ಪ','Q':'ಕ','R':'ರ','S':'ಸ','T':'ತ','U':'ಉ',
                        'V':'ವ','W':'ವ','X':'ಕ್ಷ','Y':'ಯ','Z':'ಝ',' ':' ','\n':'\n'}

        self.word_bank = {lang: load_wordlist(lang) for lang in self.languages}

        self.kannada_phonetic_map = {
            "aa":"ಆ","a":"ಅ","ii":"ಈ","i":"ಇ","uu":"ಊ","u":"ಉ","ee":"ಏ","e":"ಎ",
            "oo":"ಓ","o":"ಒ","ka":"ಕ","kha":"ಖ","ga":"ಗ","gha":"ಘ",
            "cha":"ಚ","chha":"ಛ","ja":"ಜ","jha":"ಝ",
            "ta":"ತ","tha":"ಥ","da":"ದ","dha":"ಧ",
            "na":"ನ","pa":"ಪ","pha":"ಫ","ba":"ಬ","bha":"ಭ",
            "ma":"ಮ","ya":"ಯ","ra":"ರ","la":"ಲ","va":"ವ",
            "sha":"ಶ","ssa":"ಷ","sa":"ಸ","ha":"ಹ","lla":"ಳ",
            "ksha":"ಕ್ಷ","jnya":"ಜ್ಞ"," ":" "
        }

    def phonetic_to_kannada(self, text):
        result = ""
        i = 0
        while i < len(text):
            matched = False
            for l in [5,4,3,2,1]:
                if i+l <= len(text) and text[i:i+l].lower() in self.kannada_phonetic_map:
                    result += self.kannada_phonetic_map[text[i:i+l].lower()]
                    i += l
                    matched = True
                    break
            if not matched:
                result += text[i]
                i += 1
        return result

    def draw_unicode_text(self, img, text, pos, lang="English", color=(255,255,255), size=28):
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        if lang=="Hindi": draw.text(pos,text,font=self.font_hin,fill=color)
        elif lang=="Kannada": draw.text(pos,text,font=self.font_kan,fill=color)
        else: draw.text(pos,text,font=self.font_eng,fill=color)
        return np.array(img_pil)

    def get_suggestions(self, prefix):
        lang = self.languages[self.current_language]
        words = self.word_bank.get(lang, [])
        prefix = prefix.lower()
        return [w for w in words if w.lower().startswith(prefix)][:5]

    def start(self):
        # mp_hands = mp.solutions.hands
        # hands = mp_hands.Hands(max_num_hands=1)
        # mp_draw = mp.solutions.drawing_utils

        keyboard_layout = [
            [('Esc',1.5),('F1',1.1),('F2',1.1),('F3',1.1),('F4',1.1),('F5',1.1),('F6',1.1),('F7',1.1),('F8',1.1),('F9',1.1),('F10',1.5),('F11',1.5),('F12',1.5)],
            [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),(' -',1),('=',1),('Bksp',2.7)],
            [('Tab',2),('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1.2),(' \\',1.53)],
            [('Caps',2.4),('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),(" '",1),('Enter',2.35)],
            [('Shift',2.2),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),(' .',1),(' ?',1),(' /',1),('Shift',2.55)],
            [('Ctrl',1.6),('Win',1.6),('Alt',1.4),('Space',4),('Alt',1.4),('Menu',2.2),('Ctrl',1.6),('Lang',2.1)]
        ]

        special_keys = {
            'Space':'space','Enter':'enter','Bksp':'backspace',
            'Tab':'tab','Shift':'shift','Ctrl':'ctrl','Alt':'alt',
            'Win':'winleft','Caps':'capslock'
        }

        def is_pinch(thumb_tip,index_tip):
            dist = math.hypot(index_tip[0]-thumb_tip[0],index_tip[1]-thumb_tip[1])
            return dist<30

        start_x,start_y = 20,120
        unit_width,key_height = 35,55
        x_spacing,y_spacing = 1,1

        def draw_keyboard(img):
            y = start_y
            for row in keyboard_layout:
                x = start_x
                for key,w in row:
                    kw = int(unit_width*w)
                    # Caps key color green when caps_on is True
                    if key == "Caps" and self.caps_on:
                        color, thickness = (0, 255, 0), -1  # Green filled
                    elif key==self.last_pressed_key and time.time()-self.last_pressed_time<0.5:
                        color,thickness = (0,255,0),-1  # Green if pressed
                    elif key.lower() in self.active_modifiers:
                        color,thickness = (0,200,0),-1  # Green if modifier active
                    else:
                        color,thickness = (255,0,255),2
                    cv2.rectangle(img,(x,y),(x+kw,y+key_height),color,thickness)
                    img = self.draw_unicode_text(img,key,(x+5,y+25),lang=self.languages[self.current_language],color=(255,255,255))
                    x += kw+x_spacing
                y += key_height+y_spacing
            return img

        def detect_key_press(x,y):
            y_cursor=start_y
            for row in keyboard_layout:
                x_cursor=start_x
                for key,w in row:
                    kw=int(unit_width*w)
                    if x_cursor<x<x_cursor+kw and y_cursor<y<y_cursor+key_height:
                        return key
                    x_cursor+=kw+x_spacing
                y_cursor+=key_height+y_spacing
            return None

        def draw_suggestions(img):
            words=self.typed_text.split()
            if not words: self.suggestion_boxes=[]
            else:
                last_word=words[-1]
                suggestions=self.get_suggestions(last_word)
                self.suggestion_boxes=[]
                x,y=50,80
                for sug in suggestions:
                    cv2.rectangle(img,(x,y),(x+150,y+40),(200,200,0),-1)
                    img=self.draw_unicode_text(img,sug,(x+5,y+5),lang=self.languages[self.current_language],color=(0,0,0))
                    self.suggestion_boxes.append((sug,(x,y,x+150,y+40)))
                    x+=160
            return img

        def check_suggestion_press(x,y):
            for sug,(x1,y1,x2,y2) in self.suggestion_boxes:
                if x1<x<x2 and y1<y<y2:
                    words=self.typed_text.split()
                    if words: words[-1]=sug
                    else: self.typed_text=sug
                    self.typed_text=" ".join(words)
                    return True
            return False

        cap=cv2.VideoCapture(0)
        screen_width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        screen_height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cv2.namedWindow("AI Virtual Keyboard",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AI Virtual Keyboard",screen_width,screen_height)

        while self.kg_mode:
            success,img=cap.read()
            img=cv2.flip(img,1)
            img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            results=hands.process(img_rgb)

            img=self.draw_unicode_text(img,self.typed_text,(50,40),lang=self.languages[self.current_language],color=(0,255,0))
            img=self.draw_unicode_text(img,f"Lang: {self.languages[self.current_language]}",(400,40),lang="English",color=(0,255,255))
            img=draw_suggestions(img)
            img=draw_keyboard(img)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img,hand_landmarks,mp_hands.HAND_CONNECTIONS)
                    h,w,_=img.shape
                    thumb_tip=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_pos=(int(thumb_tip.x*w),int(thumb_tip.y*h))
                    index_pos=(int(index_tip.x*w),int(index_tip.y*h))

                    if is_pinch(thumb_pos,index_pos):
                        cx=(thumb_pos[0]+index_pos[0])//2
                        cy=(thumb_pos[1]+index_pos[1])//2

                        if check_suggestion_press(cx,cy):
                            continue

                        key=detect_key_press(cx,cy)
                        if key:
                            if key=="Lang":
                                self.current_language=(self.current_language+1)%len(self.languages)
                            elif key == "Caps":
                                self.caps_on = not self.caps_on
                            elif key in special_keys:
                                action = special_keys[key]
                                if action in ['ctrl','shift','alt']:
                                    if action in self.active_modifiers:
                                        self.active_modifiers.remove(action)
                                    else:
                                        self.active_modifiers.add(action)
                                else:
                                    if self.active_modifiers:
                                        pyautogui.hotkey(*self.active_modifiers, action)
                                    else:
                                        pyautogui.press(action)

                                    if action == 'backspace':
                                        self.typed_text = self.typed_text[:-1]
                                    elif action == 'space':
                                        self.typed_text += ' '
                                    elif action == 'enter':
                                        self.typed_text += '\n'

                            else:
                                if key.isalpha():
                                    if self.caps_on:
                                        key_to_add = key.upper()
                                    else:
                                        key_to_add = key.lower()
                                else:
                                    key_to_add = key

                                if self.active_modifiers:
                                    pyautogui.hotkey(*self.active_modifiers, key_to_add.lower())
                                else:
                                    pyautogui.press(key_to_add.lower())

                                if self.languages[self.current_language]=="Hindi":
                                    self.typed_text += self.hin_map.get(key_to_add.upper(), key_to_add)
                                elif self.languages[self.current_language]=="Kannada":
                                    phonetic_input = self.typed_text + key_to_add.lower()
                                    self.typed_text = self.phonetic_to_kannada(phonetic_input)
                                else:
                                    self.typed_text += key_to_add

                            self.last_pressed_key=key
                            self.last_pressed_time=time.time()
                            try: playsound("click.mp3",block=False)
                            except: pass
                            cv2.waitKey(200)

            cv2.imshow("AI Virtual Keyboard",img)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                self.kg_mode=0

        cap.release()
        cv2.destroyAllWindows()


if __name__=="__main__":
    kg=KeyboardGestureController()
    kg.start()
