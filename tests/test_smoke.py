"""Smoke tests to ensure the basic stability of the application."""

from pyautogui import click, drag, locateCenterOnScreen, moveTo, press
from pytest import fail, mark
from sys import path as sys_path
from threading import Thread
from time import sleep

from kivy.app import App
from kivy.lang import Builder

# kludge relative import for Python REPL
sys_path.append('..')
from ..src.gui.app import MurmurApp

# suppress warnings about internal Kivy warning
pytestmark = mark.filterwarnings("ignore:The 'warn' method is deprecated")

_IMAGE_PATHS = {
    'start_stop_button' : 'tests/images/start_stop_button.png',
    'speed_slider_knob' : 'tests/images/speed_slider_knob.png'
}

# test threads tell the main thread about failures in this variable
_FAIL_MSG = None

# Kivy will load the kv file as many times as the App is run, and that is bad
def _clear_kv_from_builder():
    murmur_kv_file = './src/gui/murmur.kv'
    Builder.unload_file(murmur_kv_file)

def test_survive_run_and_quit():
    def delayed_user_actions():
        sleep(2)
        press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    assert App.get_running_app() is None

def test_survive_simulation_by_keypress():
    def delayed_user_actions():
        sleep(2)
        press('g') # start simulation
        sleep(2)
        press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    assert App.get_running_app() is None

def test_survive_simulation_by_mouse():
    def delayed_user_actions():
        global _FAIL_MSG
        sleep(2)
        button_name = 'start_stop_button'
        button_pos = locateCenterOnScreen(_IMAGE_PATHS[button_name])
        if button_pos is None:
            _FAIL_MSG = 'Unable to locate %s on screen' % button_name
            App.get_running_app().stop()
            return
        click(*button_pos) # press start/stop btn to start simulation
        sleep(2)
        press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        fail(_FAIL_MSG)
    assert App.get_running_app() is None

def test_survive_simulation_speed_adjustment():
    def delayed_user_actions():
        global _FAIL_MSG
        sleep(2)
        button_name = 'start_stop_button'
        button_pos = locateCenterOnScreen(_IMAGE_PATHS[button_name])
        if button_pos is None:
            _FAIL_MSG = 'Unable to locate %s on screen' % button_name
            App.get_running_app().stop()
            return
        click(*button_pos) # press start/stop btn to start simulation
        sleep(1)
        knob_name = 'speed_slider_knob'
        knob_pos = locateCenterOnScreen(_IMAGE_PATHS[knob_name])
        if knob_pos is None:
            _FAIL_MSG = 'Unable to locate %s on screen' % knob_name
            App.get_running_app().stop()
            return
        moveTo(knob_pos)
        drag(50, 0, 1, button='left')
        sleep(2)
        press('q') # quit application
        sleep(1)
    _clear_kv_from_builder()
    test_thread = Thread(target=delayed_user_actions)
    test_thread.start()
    MurmurApp().run()
    test_thread.join()
    # if an error happened on test_thread, we still need to fail on the main thread
    if _FAIL_MSG:
        fail(_FAIL_MSG)
    assert App.get_running_app() is None
