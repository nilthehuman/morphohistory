"""The top level root widget (main window) of the application's GUI."""

# pylint: disable=wildcard-import, unused-wildcard-import

from kivy import require as kivy_require
from kivy.config import Config
from kivy.uix.tabbedpanel import TabbedPanel

from .sim import *
from .settings import *

kivy_require('2.1.0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class TopTabbedPanel(TabbedPanel):
    """The application's root widget, enables switching between tabs."""
    pass
