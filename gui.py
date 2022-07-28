"""The app's GUI built with the Kivy toolkit"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import ColorProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from itertools import product
from logging import debug
from random import choices
from threading import Thread
from time import sleep

from speaker import Speaker

# Adapted from kivy.org/doc/stable/api-kivy.core.window.html
class KeyeventHandler(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keypressed)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.keyboard = None

    def on_keypressed(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'g':
            event = Clock.schedule_interval(App.get_running_app().root.children[1].simulate, 0.1)
            return True
        elif keycode[1] == 'q':
            debug("Exiting app")
            App.get_running_app().stop()
            return True
        return False

# not sure if this is the way to go
class SimulationThread(Thread):
    def __init__(self):
        Thread.__init__(self)
#        super().__init__(threadID, name, counter)
    def run(self):
        print ("Starting " + self.name)
        sleep(5)
        print (self.name)
        print ("Exiting " + self.name)

# usage:
#        self.simul_thread = SimulationThread(1, "SimulThread", 1)
#        self.simul_thread.start() # test

class TopBoxLayout(BoxLayout):
    pass

class ButtonLayout(BoxLayout):
    pass

class StartStopSimButton(Button):
    sim = None
    start_text = 'Csapassad neki!'
    stop_text = 'Várj egy kicsit,\nlégy oly kedves!'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.start_text
        self.bind(on_press=self.start)

    def start(self, *args):
        if not self.sim:
            self.sim = Clock.schedule_interval(App.get_running_app().root.children[1].simulate, 0.1)
            self.text = self.stop_text
        else:
            self.sim.cancel()
            self.sim = None
            self.text = self.start_text

# inherit from Speaker?
class Disc(DragBehavior, Widget):
    color = ColorProperty()

    def __init__(self, n, pos, weight_a, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.size = 20, 20
        self.n = n
        self.speaker = Speaker.fromweight(weight_a)
        self.update_color()
        self.nametag = NameTag(text=str(n)) # + TODO.name_tag())
        self.nametag_on = False
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_pos(self, *args):
        pass #print(self.x, self.y)

    #def on_touch_down(self, touch):
    #    super().on_touch_down(touch)
    #    if (self.collide_point(touch.pos[0], touch.pos[1])):
    #        print("mine!", self.n)

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

    def update_color(self):
        yellow = (1.0, 1.0, 0.0)
        purple = (1.0, 0.0, 1.0)
        w = self.speaker.principal_weight()
        self.color = [sum(x) for x in zip([(1-w) * y for y in yellow], [w * p for p in purple])]

    def talk_to(self, hearer):
        self.speaker.talk_to(hearer.speaker)
        self.update_color()

class NameTag(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        self.pos = pos

class Agora(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.talk_line = None

    def simulate(self, dt):
        debug("Starting simulation")
        pairs = [(s, t) for (s, t) in product(self.children, self.children) if s != t]
        inv_dist_sq = lambda p, q: 1 / ((p[0] - q[0])**2 + (p[1] - q[1])**2)
        inv_dist_squared = [ inv_dist_sq(s.pos, t.pos) for (s, t) in pairs ]
        pick = choices(pairs, weights=inv_dist_squared, k=1)[0]
        debug(pick[0].n, "picked to talk to", pick[1].n)
        if self.talk_line:
            self.canvas.remove(self.talk_line)
        self.talk_line = Line(points=[pick[0].pos[0]+10, pick[0].pos[1]+10, pick[1].pos[0]+10, pick[1].pos[1]+10], width=2)
        self.canvas.add(Color(0.2, 0.0, 0.8))
        self.canvas.add(self.talk_line)
        pick[0].talk_to(pick[1])
        return True # keep going

class DemoAgora(Agora):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *args):
        for row in range(10):
            for col in range(10):
                weight_a = 0.05 * (row + col)
                pos = self.width * 0.1 + self.width * 0.09 * col - 10, self.height * 0.9 - self.height * 0.09 * row - 10
                self.add_widget(Disc(row*10 + col, pos, weight_a))
        self.unbind(size=self.populate)

class MurmurApp(App):
    def build(self):
        KeyeventHandler()
        return TopBoxLayout()

if __name__ == '__main__':
    MurmurApp().run()
