from sys import version_info
from logging import warning

if version_info < (3, 7):
    warning("You're using an old version of Python. Please consider upgrading to Python 3.7 or newer.")

try:
    from .src.gui.app import MorphoHistoryApp
except ImportError:
    from src.gui.app import MorphoHistoryApp

MorphoHistoryApp().run()
