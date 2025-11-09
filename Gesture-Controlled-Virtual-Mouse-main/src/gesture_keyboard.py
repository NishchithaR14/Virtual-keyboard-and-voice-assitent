import cv2
import mediapipe as mp
import math
import pyautogui
import time
import threading

# Optional: use simpleaudio or playsound; we'll try playsound if available in non-blocking thread
try:
    from playsound import playsound
    def play_click_sound():
        try:
            playsound("click.mp3", block=True)
        except:
            pass
except Exception:
    def play_click_sound():
        pass


class GestureKeyboard:
    def __init__(self, cam_index=0):   # ✅ fixed __init__
        self.kg_mode = True
        self.last_pressed_key = None
        self.last_pressed_time = 0.0
        self.typed_text = ""
        self.cam_index = cam_index

        # smoothing factor for EMA of key cursor
        self.ema_alpha = 0.35
        self.smoothed_cursor = None

        # pinch stability: require N consecutive frames
        self.pinch_frames_required = 3
        self.pinch_counter = 0
        self.last_pinch_state = False

        # visual press cooldown (seconds)
        self.press_cooldown = 0.35

        # keyboard layout - (label, width_multiplier)
        self.keyboard_layout = [
            [('Esc',1),('F1',1.2),('F2',1.2),('F3',1.2),('F4',1.2),('F5',1.2),('F6',1.2),('F7',1.2),('F8',1.2),('F9',1.2),('F10',1.1),('F11',1.1),('F12',1.1)],
            [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1),('Bksp',2)],
            [('Tab',1.5),('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1),('\\',1.52)],
            [('Caps',1.75),('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),("'",1),('Enter',2.30)],
            [('Shift',2.25),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),('.',1),('/',1),('Shift',2.83)],
            [('Ctrl',1.25),('Win',1.25),('Alt',1.25),('Space',6),('Alt',1.25),('Win',1.25),('Menu',1.25),('Ctrl',1.90)]
        ]

        self.special_keys = {
            'Space': 'space', 'Enter': 'enter', 'Bksp': 'backspace',
            'Tab': 'tab', 'Shift': 'shift', 'Ctrl': 'ctrl', 'Alt': 'alt',
            'Win': 'winleft', 'Caps': 'capslock', 'Esc': 'esc', 'Menu': 'menu'
        }

        # visual grid parameters
        self.start_x = 20
        self.start_y = 60
        self.unit_width = 36
        self.key_height = 54
        self.x_spacing = 3
        self.y_spacing = 4

        # For drawing & detection we will cache rectangles [(x,y,w,h,label), ...]
        self.key_rects = []
        self.build_key_rects()

    def build_key_rects(self):
        """Compute and cache rectangles for each key to speed up detection."""
        self.key_rects = []
        y = self.start_y
        for row in self.keyboard_layout:
            x = self.start_x
            for label, w in row:
                kw = int(self.unit_width * w)
                rect = (x, y, kw, self.key_height, label)
                self.key_rects.append(rect)
                x += kw + self.x_spacing
            y += self.key_height + self.y_spacing

    def is_pinch(self, thumb_tip, index_tip, hand_bbox_size):
        """Adaptive pinch threshold using hand bounding box size (hand_bbox_size ~ max distance across hand)."""
        dist = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
        threshold = max(18, hand_bbox_size * 0.12)
        return dist < threshold, dist

    def get_hand_bbox_size(self, landmarks, img_w, img_h):
        """Compute approximate hand bbox diagonal size to adapt thresholds."""
        xs = [int(l.x * img_w) for l in landmarks]
        ys = [int(l.y * img_h) for l in landmarks]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        diag = math.hypot(maxx - minx, maxy - miny)
        return max(1, diag)

    def draw_keyboard(self, img):
        """Draw the keyboard and highlight hovered / pressed keys."""
        now = time.time()
        for (x, y, kw, kh, label) in self.key_rects:
            rect_color = (255, 0, 255)
            fill = False

            if label == self.last_pressed_key and (now - self.last_pressed_time) < self.press_cooldown:
                rect_color = (0, 200, 0)
                fill = True

            if fill:
                cv2.rectangle(img, (x, y), (x + kw, y + kh), rect_color, -1)
                text_color = (255, 255, 255)
            else:
                cv2.rectangle(img, (x, y), (x + kw, y + kh), rect_color, 2)
                text_color = (255, 255, 255)

            font_scale = 0.56 if len(label) > 3 else 0.68
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = x + (kw - text_size[0]) // 2
            text_y = y + (kh + text_size[1]) // 2
            cv2.putText(img, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    def detect_key_at(self, px, py):
        for (x, y, kw, kh, label) in self.key_rects:
            if x <= px <= x + kw and y <= py <= y + kh:
                return label
        return None

    def press_key(self, key_label):
        now = time.time()
        if now - self.last_pressed_time < self.press_cooldown:
            return
        self.last_pressed_time = now
        self.last_pressed_key = key_label

        if key_label in self.special_keys:
            k = self.special_keys[key_label]
            try:
                pyautogui.press(k)
            except Exception:
                pass
            if key_label == 'Bksp':
                self.typed_text = self.typed_text[:-1]
            elif key_label == 'Space':
                self.typed_text += ' '
            elif key_label == 'Enter':
                self.typed_text += '\n'
            else:
                self.typed_text += f"[{key_label}]"
        else:
            try:
                pyautogui.press(key_label.lower())
            except Exception:
                pass
            self.typed_text += key_label

        threading.Thread(target=play_click_sound, daemon=True).start()

    def run(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6)
        mp_draw = mp.solutions.drawing_utils

        cap = cv2.VideoCapture(self.cam_index)
        if not cap.isOpened():
            print("Camera not found. Exiting.")
            return

        screen_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        screen_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        win_name = "AI Virtual Keyboard - Press 'q' to Quit"
        cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win_name, min(1280, screen_w), min(720, screen_h))

        while self.kg_mode:
            success, img = cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            self.draw_keyboard(img)

            preview_text = self.typed_text[-180:]
            cv2.rectangle(img, (10, 10), (screen_w - 10, 50), (0, 0, 0), -1)
            cv2.putText(img, preview_text.replace('\n', ' ↵ '), (14, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                h, w, _ = img.shape
                thumb_lm = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_lm = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_pos = (int(thumb_lm.x * w), int(thumb_lm.y * h))
                index_pos = (int(index_lm.x * w), int(index_lm.y * h))

                hand_bbox_size = self.get_hand_bbox_size([l for l in hand_landmarks.landmark], w, h)

                pinched, pinch_dist = self.is_pinch(thumb_pos, index_pos, hand_bbox_size)

                cx = (thumb_pos[0] + index_pos[0]) // 2
                cy = (thumb_pos[1] + index_pos[1]) // 2

                if self.smoothed_cursor is None:
                    self.smoothed_cursor = (cx, cy)
                else:
                    sx = int(self.ema_alpha * cx + (1 - self.ema_alpha) * self.smoothed_cursor[0])
                    sy = int(self.ema_alpha * cy + (1 - self.ema_alpha) * self.smoothed_cursor[1])
                    self.smoothed_cursor = (sx, sy)

                cv2.circle(img, self.smoothed_cursor, 10, (0, 180, 255), -1)
                cv2.line(img, thumb_pos, index_pos, (200, 200, 200), 2)

                hovered_key = self.detect_key_at(self.smoothed_cursor[0], self.smoothed_cursor[1])
                if hovered_key:
                    for (x, y, kw, kh, label) in self.key_rects:
                        if label == hovered_key:
                            cv2.rectangle(img, (x, y), (x + kw, y + kh), (0, 140, 255), 4)
                            break

                if pinched:
                    self.pinch_counter += 1
                else:
                    self.pinch_counter = 0

                if self.pinch_counter >= self.pinch_frames_required:
                    if hovered_key and (time.time() - self.last_pressed_time) > self.press_cooldown:
                        self.press_key(hovered_key)
                        time.sleep(0.08)
                        self.pinch_counter = 0

                cv2.putText(img, f"pinch:{int(pinch_dist)}", (14, screen_h - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

            cv2.imshow(win_name, img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.kg_mode = False
            elif key == ord('c'):
                self.typed_text = ""

        cap.release()
        cv2.destroyAllWindows()


# ✅ fixed __name__ check
if __name__ == "__main__":
    kb = GestureKeyboard(cam_index=0)
    kb.run()
