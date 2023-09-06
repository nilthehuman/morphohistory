from sys import version_info
from logging import getLogger, INFO, warn

if version_info < (3, 11):
    warn("You're using an old version of Python. Please upgrade to Python 3.11 or newer.")

from src.gui.app import MorphoHistoryApp

getLogger().setLevel(INFO)

MorphoHistoryApp().run()
