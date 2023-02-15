"""Main entry point of the application."""

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

from .root import *
from .sim import *
from .settings import *

_KV_FILES = ["src/gui/root.kv",
             "src/gui/sim.kv",
             "src/gui/settings.kv"]
for file in _KV_FILES:
    Builder.load_file(file)

class MurmurApp(App):
    def build(self):
        self.icon = "assets/logo.png"
        root = TopTabbedPanel()
        Window.minimum_width = (root.ids.sim_layout.ids.agora_layout.width +
                                root.ids.sim_layout.ids.button_layout.width)
        Window.minimum_height = root.ids.sim_layout.ids.agora_layout.height
        KeyeventHandler()
        return root

if __name__ == '__main__':
    MurmurApp().run()
