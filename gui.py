"""The app's GUI built with the Kivy toolkit"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget

# Adapted from kivy.org/doc/stable/api-kivy.core.window.html
class KeyeventHandler(Widget):
    def __init__(self, **kwargs):
        super(KeyeventHandler, self).__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keypressed)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.keyboard = None

    def on_keypressed(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'q':
            App.get_running_app().stop()
            return True
        return False

class Disc(DragBehavior, Widget):
    def __init__(self, **kwargs):
        self.color = 0.6, 0.4, 0.8
        super(Disc, self).__init__(**kwargs)
        self.size = 20, 20
        self.pos = Window.width * 0.5, Window.height * 0.5

    def on_pos(self, *args):
        pass #print(self.x, self.y)

class MurmurApp(App):
    def build(self):
        KeyeventHandler()
        return Disc()

if __name__ == '__main__':
    MurmurApp().run()
