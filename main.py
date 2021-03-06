import concurrent.futures
import os
import sys
import threading
from time import sleep

import keyboard
import pyautogui
import PySimpleGUI as sg

# TODO: remap/catch the key so it doesn't do it's previous action

if getattr(sys, 'frozen', False): # Running as compiled
    os.chdir(sys._MEIPASS) # change current working directory to sys._MEIPASS

sg.theme('DarkAmber')
layout = [[sg.Text('Set the key to detect:'), sg.Button('Click Me!', key='-SELECT-')], [sg.Text('Last X keys'), sg.Slider(range=(1, 10), default_value=1, orientation='horizontal', key='-SLIDER-')], [sg.Button('START', button_color='green', key='-START-')]]

window = sg.Window('Lock pressed keys', layout, icon='MMA.ico')

class UsefulKey:
    def __init__(self, key):
        self.do_run = False
        self.key = key

    def check_useful_key_pressed(self):
        thread = threading.current_thread()
        while thread.do_run:
            if keyboard.read_key() == self.key:
                sleep(0.2)
                if self.do_run:
                    self.do_run = False
                else:
                    self.do_run = True
                    save_queue = queue.clean_queue()
                    threading.Thread(target=self.keep_key_pressed, args=(save_queue, )).start()

    def keep_key_pressed(self, save_queue: list):
        while self.do_run:
            for element in save_queue:
                pyautogui.keyDown(element)
        for element in save_queue:
            pyautogui.keyUp(element)

class Queue:
    def __init__(self, maxsize: int = 10, n: int = 1):
        self.maxsize = maxsize
        self.n = n
        self.queue = []
        self.can_change = False

    def put(self, item):
        if len(self.queue) == self.maxsize:
            self.queue.pop(0)
        self.queue.append(item)

    def get(self):
        return self.queue.pop(0)

    def clean_queue(self):
        r = []
        for element in self.queue:
            if element != useful_key.key and element not in r and element != '':
                r.append(element)
        return r[-self.n:]

def set_useful_key():
    while True:
        if keyboard.read_key():
            return keyboard.read_key()

def register_keys():
    while queue.can_change:
        queue.put(keyboard.read_key())

run = False

while True:
    event, values = window.Read(timeout=100)
    if event is None or event in [sg.WIN_CLOSED]:
        os._exit(0)
    if event == '-SELECT-':
        with concurrent.futures.ThreadPoolExecutor() as executor:
            useful_key = UsefulKey(executor.submit(set_useful_key).result())
        window['-SELECT-'].Update(text=f'{useful_key.key}')
    if event == '-START-' and 'useful_key' in globals():
        queue = Queue(maxsize=values['-SLIDER-']*3+10 if values['-SLIDER-'] < 4 else values['-SLIDER-']*3, n=int(values['-SLIDER-']))
        if run == True:
            run = False
            queue.can_change = False
            thread.do_run = False
            window['-START-'].Update(text='START', button_color='green')
        else:
            run = True
            queue.can_change = True
            window['-START-'].Update(text='STOP', button_color='red')
            threading.Thread(target=register_keys).start()
            thread = threading.Thread(target=useful_key.check_useful_key_pressed)
            thread.do_run = True
            thread.start()
