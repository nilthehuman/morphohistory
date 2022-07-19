"""The app's GUI built with the Kivy toolkit"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget

class Disc(DragBehavior, Widget):
    def __init__(self, **kwargs):
        self.color = 0.6, 0.4, 0.8
        super(Disc, self).__init__(**kwargs)
        self.size = 20, 20
        self.pos = Window.width * 0.5, Window.height * 0.5

class MurmurApp(App):
    def build(self):
        return Disc()

if __name__ == '__main__':
    MurmurApp().run()
