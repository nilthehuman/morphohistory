"""Main entry point of the application."""

# pylint: disable=wildcard-import, unused-wildcard-import
from os.path import dirname, join
from platform import system

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
if system() == "Windows":
    Config.set('kivy', 'keyboard_mode', 'system')

from kivy import require as kivy_require
kivy_require('2.1.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

from .keyboardhandler import KeyboardHandler
from .root import *
from .sim import *
from .settings import *
from .paradigm import *


_DIRECTORY = join(dirname(__file__))
_KV_FILES = (join(_DIRECTORY, "root.kv"),
             join(_DIRECTORY, "sim.kv"),
             join(_DIRECTORY, "settings.kv"),
             join(_DIRECTORY, "paradigm.kv"),
             join(_DIRECTORY, "confirm.kv"))
for file in _KV_FILES:
    Builder.load_file(file)

class MorphoHistoryApp(App):
    def build(self):
        self.title = "morphohistory"
        self.icon = "assets/logo.png"
        root = TopTabbedPanel()
        Window.minimum_width = (root.ids.sim_layout.ids.agora_layout.width +
                                root.ids.sim_layout.ids.button_layout.width)
        Window.minimum_height = root.ids.sim_layout.ids.agora_layout.height
        KeyboardHandler()
        return root

if __name__ == '__main__':
    MorphoHistoryApp().run()
