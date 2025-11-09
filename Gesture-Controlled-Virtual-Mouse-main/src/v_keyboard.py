import cv2
import mediapipe as mp
import math
import pyautogui
import time
from playsound import playsound

class KeyboardGestureController:
    def __init__(self):  
        self.kg_mode = 1
        self.last_pressed_key = None
        self.last_pressed_time = 0
        self.typed_text = ""

    def start(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands()
        mp_draw = mp.solutions.drawing_utils

        keyboard_layout = [
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I'],
            ['O', 'P', 'Backspace', 'Ctrl', 'A', 'S', 'D', 'F', 'G'],
            ['H', 'J', 'K', 'L', 'Enter', 'Shift', 'Z', 'X', 'C'],
            ['V', 'B', 'N', 'M', ',', '.', '/', 'Alt', 'Win'],
            ['Space', '1', '2', '3', '4', '5', '6', '7', '8'],
            ['9', '0', '+', '-', '*', '/', '=', '.']
        ]

        special_keys = {
            'Space': 'space', 'Enter': 'enter', 'Backspace': 'backspace',
            'Tab': 'tab', 'Shift': 'shift', 'Ctrl': 'ctrl', 'Alt': 'alt',
            'Win': 'winleft', '+': '+', '-': '-', '': '', '/': '/',
            '=': '=', '.': '.', ',': ','
        }

        key_width, key_height = 60, 60
        x_spacing, y_spacing = 70, 70

        cap = cv2.VideoCapture(0)
        screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        max_row_length = max(len(row) for row in keyboard_layout)
        keyboard_width = max_row_length * x_spacing
        keyboard_height = len(keyboard_layout) * y_spacing

        start_x = (screen_width - keyboard_width) // 2
        start_y = (screen_height - keyboard_height) // 2

        def is_pinch(thumb_tip, index_tip):
            dist = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
            return dist < 30

        def draw_keyboard(img):
            for i, row in enumerate(keyboard_layout):
                for j, key in enumerate(row):
                    x = start_x + j * x_spacing
                    y = start_y + i * y_spacing
                    if key == self.last_pressed_key and time.time() - self.last_pressed_time < 0.5:
                        color = (0, 255, 0)
                        thickness = -1
                    else:
                        color = (255, 0, 255)
                        thickness = 2
                    cv2.rectangle(img, (x, y), (x + key_width, y + key_height), color, thickness)
                    font_scale = 0.8 if len(key) > 1 else 1.2
                    offset = 10 if len(key) > 1 else 15
                    cv2.putText(img, key, (x + offset, y + 40), cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale, (255, 255, 255), 2)

        def detect_key_press(x, y):
            for i, row in enumerate(keyboard_layout):
                for j, key in enumerate(row):
                    key_x = start_x + j * x_spacing
                    key_y = start_y + i * y_spacing
                    if key_x < x < key_x + key_width and key_y < y < key_y + key_height:
                        return key
            return None

        cv2.namedWindow("AI Virtual Keyboard", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AI Virtual Keyboard", screen_width, screen_height)

        while self.kg_mode:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            draw_keyboard(img)
            cv2.putText(img, self.typed_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    h, w, _ = img.shape
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                    index_pos = (int(index_tip.x * w), int(index_tip.y * h))

                    if is_pinch(thumb_pos, index_pos):
                        cx = (thumb_pos[0] + index_pos[0]) // 2
                        cy = (thumb_pos[1] + index_pos[1]) // 2
                        key = detect_key_press(cx, cy)
                        if key:
                            if key in special_keys:
                                pyautogui.press(special_keys[key])
                                if key == 'Backspace':
                                    self.typed_text = self.typed_text[:-1]
                                elif key == 'Space':
                                    self.typed_text += ' '
                                elif key == 'Enter':
                                    self.typed_text += '\n'
                                else:
                                    self.typed_text += f"[{key}]"
                            else:
                                pyautogui.press(key.lower())
                                self.typed_text += key
                            self.last_pressed_key = key
                            self.last_pressed_time = time.time()
                            try:
                                playsound("click.mp3", block=False)
                            except:
                                pass
                            cv2.waitKey(300)

            cv2.imshow("AI Virtual Keyboard", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.kg_mode = 0  # ✅ clean exit condition

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    kg = KeyboardGestureController()
    kg.start()
