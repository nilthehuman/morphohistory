"""Main entry point of the application."""

from kivy.app import App
from kivy.core.window import Window

from .gui import KeyeventHandler, TopTabbedPanel

class MurmurApp(App):
    def build(self):
        self.icon = "assets/logo.png"
        root = TopTabbedPanel()
        Window.minimum_width = root.ids.rel_layout.width + root.ids.button_layout.width
        Window.minimum_height = root.ids.rel_layout.height
        KeyeventHandler()
        return root

if __name__ == '__main__':
    MurmurApp().run()
