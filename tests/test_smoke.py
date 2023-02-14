"""Smoke tests to ensure the basic stability of the application."""

import pyautogui
try:
    import pydirectinput as input_module
except ImportError:
    import pyautogui as input_module
import pytest
from sys import path as sys_path
from threading import Thread
from time import sleep

from kivy.app import App
from kivy.lang import Builder

# kludge relative import for Python REPL
sys_path.append('..')
from ..src.gui.app import MurmurApp

# suppress warnings about internal Kivy warning
pytestmark = pytest.mark.filterwarnings("ignore:The 'warn' method is deprecated")

# PyAutoGUI will look for these GUI elements on the screen
_IMAGE_PATHS = {
    'start_stop_button'   : 'tests/images/start_stop_button.png',
    'speed_slider_knob'   : 'tests/images/speed_slider_knob.png',
    'fast_forward_button' : 'tests/images/fast_forward_button.png',
    'rewind_button'       : 'tests/images/rewind_button.png'
}

# test threads will tell the main thread about failures in this variable
_FAIL_MSG = None

# Kivy will load the kv file as many times as the App is run, and that is bad
def _clear_kv_from_builder():
    murmur_kv_file = './src/gui/murmur.kv'
    Builder.unload_file(murmur_kv_file)

@pytest.mark.parametrize("keys",
                         [
                             [],
                             ['g'],
                             ['g','g']
                         ])
def test_survive_keypresses(keys):
    def delayed_user_actions():
        sleep(2)
        for key in keys:
            input_module.press(key)
            sleep(2)
        input_module.press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    assert App.get_running_app() is None

@pytest.mark.parametrize("buttons",
                         [
                             ['start_stop_button'],
                             # FIXME: button text changes when clicked...
                             #['start_stop_button', 'start_stop_button'],
                             ['fast_forward_button'],
                             ['fast_forward_button', 'rewind_button']
                         ])
def test_survive_button_clicks(buttons):
    def delayed_user_actions():
        global _FAIL_MSG
        for button in buttons:
            button_pos = pyautogui.locateCenterOnScreen(_IMAGE_PATHS[button])
            if button_pos is None:
                _FAIL_MSG = 'Unable to locate %s on screen' % button
                App.get_running_app().stop()
                return
            input_module.click(*button_pos)
            sleep(2)
            input_module.move(-300, 0) # move cursor off button
        input_module.press('q') # quit application
        sleep(2)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        pytest.fail(_FAIL_MSG)
    assert App.get_running_app() is None

def test_survive_simulation_speed_adjustment():
    def delayed_user_actions():
        global _FAIL_MSG
        sleep(2)
        button = 'start_stop_button'
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
        sleep(2)
        input_module.press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        pytest.fail(_FAIL_MSG)
    assert App.get_running_app() is None
