"""Smoke tests to ensure the basic stability of the application."""

from logging import getLogger, WARNING
getLogger().setLevel(WARNING)
from os.path import dirname, join

import pyautogui
try:
    import pydirectinput as input_module
except ImportError:
    import pyautogui as input_module
import pytest
from sys import path as sys_path
from threading import Thread
from time import sleep

from platform import system
if system() == "Windows":
    from kivy.config import Config
    Config.set('kivy', 'keyboard_mode', 'systemandmulti')

from kivy.app import App

# kludge relative import for Python REPL
sys_path.append('..')
from src.gui.app import MorphoHistoryApp

# suppress warnings about internal Kivy warning
pytestmark = pytest.mark.filterwarnings("ignore:The 'warn' method is deprecated")

# PyAutoGUI will look for these GUI elements on the screen
_IMAGE_DIRECTORY = join(dirname(__file__), "images")
_IMAGE_PATHS = {
    'start_button'        : join(_IMAGE_DIRECTORY, "start_button.png"),
    'stop_button'         : join(_IMAGE_DIRECTORY, "stop_button.png"),
    'speed_slider_knob'   : join(_IMAGE_DIRECTORY, "speed_slider_knob.png"),
    'fast_forward_button' : join(_IMAGE_DIRECTORY, "fast_forward_button.png"),
    'rewind_button'       : join(_IMAGE_DIRECTORY, "rewind_button.png"),
    'first_tab_header'    : join(_IMAGE_DIRECTORY, "first_tab_header.png"),
    'second_tab_header'   : join(_IMAGE_DIRECTORY, "second_tab_header.png")
}

# test threads will tell the main thread about failures in this variable
_FAIL_MSG = None

@pytest.mark.parametrize("keys",
                         [
                             [],
                             ['g'],
                             ['g','g']
                         ])
def test_survive_keypresses(keys):
    def delayed_user_actions():
        sleep(1)
        for key in keys:
            input_module.press(key)
            sleep(1)
        input_module.press('q') # quit application
        sleep(1)
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MorphoHistoryApp().run()
    test_thread.join()
    assert App.get_running_app() is None

@pytest.mark.parametrize("buttons",
                         [
                             ['start_button'],
                             ['start_button', 'stop_button'],
                             ['fast_forward_button'],
                             ['fast_forward_button', 'rewind_button'],
                             ['second_tab_header', 'first_tab_header']
                         ])
def test_survive_button_clicks(buttons):
    def delayed_user_actions():
        global _FAIL_MSG
        for button in buttons:
            sleep(1)
            button_pos = pyautogui.locateCenterOnScreen(_IMAGE_PATHS[button])
            if button_pos is None:
                _FAIL_MSG = 'Unable to locate %s on screen' % button
                App.get_running_app().stop()
                return
            input_module.click(*button_pos)
            sleep(1)
            input_module.move(-300, 0) # move cursor off button
        input_module.press('q') # quit application
        sleep(1)
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MorphoHistoryApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        pytest.fail(_FAIL_MSG)
    assert App.get_running_app() is None

def test_survive_simulation_speed_adjustment():
    def delayed_user_actions():
        global _FAIL_MSG
        sleep(1)
        button = 'start_button'
        button_pos = pyautogui.locateCenterOnScreen(_IMAGE_PATHS[button])
        if button_pos is None:
            _FAIL_MSG = 'Unable to locate %s on screen' % button
            App.get_running_app().stop()
            return
        input_module.click(*button_pos) # press start/stop btn to start simulation
        sleep(1)
        knob = 'speed_slider_knob'
        knob_pos = pyautogui.locateCenterOnScreen(_IMAGE_PATHS[knob])
        if knob_pos is None:
            _FAIL_MSG = 'Unable to locate %s on screen' % knob
            App.get_running_app().stop()
            return
        input_module.moveTo(knob_pos)
        input_module.drag(50, 0, 1, button='left')
        sleep(1)
        input_module.press('q') # quit application
        sleep(1)
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MorphoHistoryApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        pytest.fail(_FAIL_MSG)
    assert App.get_running_app() is None
