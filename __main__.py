from sys import version_info
from logging import getLogger, INFO

if version_info < (3, 7):
    warning("You're using an old version of Python. Please consider upgrading to Python 3.7 or newer.")

from src.gui.app import MorphoHistoryApp

getLogger().setLevel(INFO)

MorphoHistoryApp().run()
