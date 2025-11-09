import eel
import os
from queue import Queue
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
from Gesture_Controller import Controller


class ChatBot:
    started = False
    userinputQueue = Queue()

    @staticmethod
    def isUserInput():
        return not ChatBot.userinputQueue.empty()

    @staticmethod
    def popUserInput():
        return ChatBot.userinputQueue.get()

    @staticmethod
    def close_callback(route, websockets):
        exit()

    @staticmethod
    @eel.expose
    def getUserInput(msg):
        ChatBot.userinputQueue.put(msg)
        print(msg)

    @staticmethod
    def close():
        ChatBot.started = False

    @staticmethod
    def addUserMsg(msg):
        eel.addUserMsg(msg)

    @staticmethod
    def addAppMsg(msg):
        eel.addAppMsg(msg)

    @staticmethod
    def start():
        path = os.path.dirname(os.path.abspath(__file__))
        eel.init(path + r'\web', allowed_extensions=['.js', '.html'])
        try:
            eel.start(
                'index.html',
                mode='chrome',
                host='localhost',
                port=27005,
                block=False,
                size=(350, 480),
                position=(10, 100),
                disable_cache=True,
                close_callback=ChatBot.close_callback
            )
            ChatBot.started = True
            while ChatBot.started:
                try:
                    eel.sleep(10.0)
                except:
                    # main thread exited
                    break

        except:
            pass


def main():
    # You can keep your gesture controller or other logic here if needed.
    pass
