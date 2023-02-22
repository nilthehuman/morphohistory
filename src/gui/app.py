"""Main entry point of the application."""

# pylint: disable=wildcard-import, unused-wildcard-import
from os.path import dirname

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

from .root import *
from .sim import *
from .settings import *
from .paradigm import *


root = join(dirname(__file__))
_KV_FILES = (join(root, "root.kv"),
             join(root, "sim.kv"),
             join(root, "settings.kv"),
             join(root, "paradigm.kv"),
             join(root, "confirm.kv"))
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
        KeyeventHandler()
        return root

if __name__ == '__main__':
    MorphoHistoryApp().run()
