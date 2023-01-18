"""The app's GUI built with the Kivy toolkit"""

import kivy
kivy.require('2.1.0')

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import ColorProperty, ObjectProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from logging import debug
from os.path import isfile, join
from random import choices
from threading import Thread

from speaker import Speaker, Agora

# Adapted from kivy.org/doc/stable/api-kivy.core.window.html
class KeyeventHandler(Widget):
    """Handles hotkeys to the application's basic features."""

    sim = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keypressed)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keypressed)
        self.keyboard = None

    def on_keypressed(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'g':
            if not self.sim:
                self.sim = Clock.schedule_interval(App.get_running_app().root.children[1].simulate, 0.1)
            else:
                self.sim.cancel()
                self.sim = None
            return True
        elif keycode[1] == 'q':
            debug("Exiting app")
            App.get_running_app().stop()
            return True
        return False

class TopBoxLayout(BoxLayout):
    """The root widget. Holds both the Arena and the control buttons on the right."""
    pass

class ButtonLayout(BoxLayout):
    """The bar with control buttons at the right edge of the screen."""
    pass

class SaveToFilePopup(FloatLayout):
    """TODO..."""
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    text_input = ObjectProperty(None)

class SaveToFileButton(Button):
    """Opens a popup window for writing the current configuration of the Arena to file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.show_save_popup)

    def show_save_popup(self, *args):
        content = SaveToFilePopup(save=self.save, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora mentése", content=content, size_hint=(0.4, 0.6))
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def save(self, path, filename):
        fullpath = join(path, filename)
        savebutton = self.popup.ids.container.children[0].ids.save_button
        if isfile(fullpath) and savebutton.text != "Felülír?":
            savebutton.text = "Felülír?"
            return
        with open(fullpath, 'w') as stream:
            stream.write("alma") # TODO output agora description
        self.dismiss_popup()

class StartStopSimButton(Button):
    """Runs or halts the simulation process."""

    sim = None
    start_text = 'Csapassad neki!'
    stop_text = 'Várj egy kicsit,\nlégy oly kedves!'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.start_text
        self.bind(on_press=self.start)

    def start(self, *args):
        if not self.sim:
            slowdown = App.get_running_app().root.ids.button_layout.ids.speed_slider.value
            self.sim = Clock.schedule_interval(App.get_running_app().root.children[1].simulate, 1.0 - 0.01 * slowdown)
            self.text = self.stop_text
        else:
            self.sim.cancel()
            self.sim = None
            self.text = self.start_text

class SkipToEndButton(Button):
    """Runs or halts the simulation process."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.skip)

    def skip(self, *args):
        # TODO: stop already running simulation
        App.get_running_app().root.children[1].simulate_till_stable()

class SpeakerDot(DragBehavior, Widget):
    """The visual representation of a single speaker on the GUI."""

    color = ColorProperty()

    def __init__(self, n, pos, weight_a, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.size = 20, 20
        self.n = n
        self.speaker = Speaker.fromweight(weight_a)
        self.update_color()
        self.nametag = NameTag(text=str(n) + ': ' + self.speaker.name_tag())
        self.nametag_on = False
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if (self.collide_point(*pos)):
            if not self.nametag_on:
                debug("Turning on nametag for", self.n)
                Window.add_widget(self.nametag)
                self.nametag_on = True
        elif self.nametag_on:
            debug("Turning off nametag for", self.n)
            Window.remove_widget(self.nametag)
            self.nametag_on = False

    #TODO: self.inv_dist_squared = None when any dot is moved!

    def update_color(self):
        yellow = (1.0, 1.0, 0.0)
        purple = (1.0, 0.0, 1.0)
        w = self.speaker.principal_weight()
        self.color = [sum(x) for x in zip([(1-w) * y for y in yellow], [w * p for p in purple])]

    def talk_to(self, hearer):
        self.speaker.talk_to(hearer.speaker)
        self.update_color()

class NameTag(Label):
    """A kind of tooltip that shows how biased a speaker is at the moment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        self.pos = pos

class AgoraWidget(Widget, Agora):
    """An agora of speakers visualized."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.talk_line = None
        self.pick = []

    def simulate(self, dt, graphics=True):
        super().simulate(dt)
        if graphics:
            if self.talk_line:
                self.canvas.remove(self.talk_line)
            self.talk_line = Line(points=[self.pick[0].pos[0]+10, self.pick[0].pos[1]+10, self.pick[1].pos[0]+10, self.pick[1].pos[1]+10], width=2)
            self.canvas.add(Color(0.2, 0.0, 0.8))
            self.canvas.add(self.talk_line)

class DemoAgoraWidget(AgoraWidget):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *args):
        for row in range(10):
            for col in range(10):
                weight_a = 0.05 * (row + col)
                pos = self.width * 0.1 + self.width * 0.09 * col - 10, self.height * 0.9 - self.height * 0.09 * row - 10
                self.add_widget(SpeakerDot(row*10 + col, pos, weight_a))
        self.unbind(size=self.populate)

class MurmurApp(App):
    def build(self):
        KeyeventHandler()
        return TopBoxLayout()

if __name__ == '__main__':
    MurmurApp().run()
