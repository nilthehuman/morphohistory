from sys import version_info
from kivy.logger import Logger

if version_info < (3, 7):
    Logger.warning("You're using an old version of Python. Please consider upgrading to Python 3.7 or newer.")

from src.gui.app import MurmurApp

MurmurApp().run()
