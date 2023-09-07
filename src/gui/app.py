"""Main entry point of the application."""

# pylint: disable=wildcard-import, unused-wildcard-import
from os.path import dirname, join
from platform import system
from sys import path

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
if system() == "Windows":
    Config.set('kivy', 'keyboard_mode', 'system')

from kivy import require as kivy_require
kivy_require('2.1.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.resources import resource_add_path, resource_find

from .access_widgets import forall_widgets
from .keyboardhandler import KeyboardHandler
from .root import TopTabbedPanel
from .sim import *
from .settings import *
from .paradigm import *
from .tuning import *


_DIRECTORY = join(dirname(__file__))
_KV_FILES = (join(_DIRECTORY, "root.kv"),
             join(_DIRECTORY, "sim.kv"),
             join(_DIRECTORY, "settings.kv"),
             join(_DIRECTORY, "paradigm.kv"),
             join(_DIRECTORY, "tuning.kv"),
             join(_DIRECTORY, "confirm.kv"))
for file in _KV_FILES:
    Builder.load_file(file)

class MorphoHistoryApp(App):
    def build(self) -> TopTabbedPanel:
        self.title = "morphohistory"
        resource_add_path(path[0])
        resource_add_path(join(path[0], "assets"))
        self.icon = resource_find("logo.png")
        root = TopTabbedPanel()
        Window.minimum_width = (root.ids.sim_layout.ids.agora_layout.width +
                                root.ids.sim_layout.ids.button_layout.width)
        Window.minimum_height = root.ids.sim_layout.ids.agora_layout.height
        self.keyboardhandler = KeyboardHandler()
        return root

    def on_start(self) -> None:
        """Prepare GUI elements that need to know about the Widget tree to complete their setup."""
        forall_widgets(lambda w: w.on_gui_ready() if hasattr(w, 'on_gui_ready') else None, self.root)

if __name__ == '__main__':
    MorphoHistoryApp().run()
