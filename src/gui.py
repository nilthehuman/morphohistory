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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from copy import deepcopy
from functools import partial
from json import dumps, load
from logging import debug
from math import sqrt, sin, cos, pi
from os.path import isfile, join
from random import choices

from .speaker import Speaker, Agora

# Adapted from kivy.org/doc/stable/api-kivy.core.window.html
class KeyeventHandler(Widget):
    """Handles hotkeys to the application's basic features."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keypressed)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keypressed)
        self.keyboard = None

    def on_keypressed(self, _keyboard, keycode, *_):
        if keycode[1] == 'g':
            Root().ids.agora.start_stop_sim()
            return True
        elif keycode[1] == 'q':
            debug("Exiting app")
            App.get_running_app().stop()
            return True
        return False

class TopBoxLayout(BoxLayout):
    """The root widget. Holds both the Agora and the control buttons on the right."""
    pass

class ButtonLayout(GridLayout):
    """The bar with control buttons at the right edge of the screen."""
    pass

class SaveToFilePopup(FloatLayout):
    """A popup window for picking a location to save the Agora to file."""
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    text_input = ObjectProperty(None)

class LoadFromFilePopup(FloatLayout):
    """A popup window for picking a file to load the Agora from."""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class FastForwardPopup(BoxLayout):
    """A popup window to show the progress of a fast forward."""
    cancel = ObjectProperty(None)

class SaveToFileButton(Button):
    """Opens a popup window for writing the current configuration of the Agora to file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.show_save_popup)

    def show_save_popup(self, *_):
        content = SaveToFilePopup(save=self.save, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora mentése", content=content, size_hint=(None, None), size=(400, 430))
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def save(self, path, filename):
        fullpath = join(path, filename)
        savebutton = self.popup.ids.container.children[0].ids.save_button
        if isfile(fullpath) and savebutton.text != "Felülírjam?":
            savebutton.text = "Felülírjam?"
            return
        with open(fullpath, 'w') as stream:
            stream.write(dumps(Root().ids.agora.speakers, indent=1, default=lambda x: x.to_json()))
        self.dismiss_popup()

class LoadFromFileButton(Button):
    """Opens a popup window for loading an Agora configuration from file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.show_load_popup)

    def show_load_popup(self, *_):
        content = LoadFromFilePopup(load=self.load, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora betöltése", content=content, size_hint=(None, None), size=(400, 430))
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def load(self, _path, fileselection):
        if not fileselection:
            return
        fullpath = fileselection[0]
        with open(fullpath, 'r') as stream:
            speaker_list = load(stream)
        speakers = [Speaker.from_json(s) for s in speaker_list]
        Root().ids.agora.clear_speakers()
        Root().ids.agora.load_speakers(speakers)
        Root().ids.agora.save_starting_state()
        self.dismiss_popup()

class StartStopSimButton(Button):
    """Runs or halts the simulation process."""

    sim = None
    start_text = 'Csapassad neki!'
    stop_text = 'Várj egy kicsit,\nlégy oly kedves!'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.start_text
        self.bind(on_release=self.start_stop)

    def start_stop(self, *_):
        Root().ids.agora.start_stop_sim()
        self.update_text()

    def update_text(self):
        self.text = self.stop_text if Root().ids.agora.sim else self.start_text

class RewindButton(Button):
    """Restores the initial state of the Agora when loaded."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.rewind)

    def rewind(self, *_):
        Root().ids.agora.stop_sim()
        Root().ids.agora.reset()

class FastForwardButton(Button):
    """Keeps running the simulation until a stable state is reached."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.fastforward)

    def fastforward(self, *_):
        Root().ids.agora.stop_sim()
        content = FastForwardPopup(cancel=self.cancel_fast_forward)
        self.popup = Popup(title="Folyamatban...", content=content, size_hint=(None, None), size=(500, 250))
        self.popup.open()
        Root().ids.agora.clear_talk_arrow()
        Root().ids.agora.start_stop_sim(fastforward=True)

    def cancel_fast_forward(self, *_):
        if Root().ids.agora.sim:
            Root().ids.agora.sim_cancelled = True

class SpeakerDot(Speaker, DragBehavior, Widget):
    """The visual representation of a single speaker on the GUI."""

    color = ColorProperty()

    def __init__(self, n, pos, para=None, experience=1.0, **kwargs):
        if type(para) is float: # poor man's polymorphism
            weight_a = para
            Speaker.__init__(self, n, pos, None, False, experience)
            Speaker.init_from_weight(self, weight_a)
        else:
            Speaker.__init__(self, n, pos, para, False, experience)
        DragBehavior.__init__(self, **kwargs)
        Widget.__init__(self, **kwargs)
        self.size = 20, 20
        self.update_color()
        self.nametag = NameTag(text=str(n) + ': ' + self.name_tag())
        self.nametag_on = False
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.bind(pos=self.on_pos_changed)

    @classmethod
    def fromspeaker(cls, speaker):
        # bit of an ugly hack but okay
        if speaker.is_broadcaster:
            return BroadcasterSpeakerDot(speaker.n, speaker.pos, deepcopy(speaker.para), speaker.experience)
        else:
            return SpeakerDot(speaker.n, speaker.pos, deepcopy(speaker.para), speaker.experience)

    def on_mouse_pos(self, _window, pos):
        if not self.parent:
            # why do SpeakerDots stay alive after AgoraWidget.clear_widgets(), this is stupid
            return
        if not self.parent.graphics_on:
            return
        pos = tuple(p - dp for (p, dp) in zip(pos, self.parent.parent.pos))
        if (self.collide_point(*pos)):
            if not self.nametag_on:
                debug("Turning on nametag for", self.n)
                self.nametag.text = str(self.n) + ': ' + self.name_tag()
                self.parent.add_widget(self.nametag)
                self.nametag_on = True
        elif self.nametag_on:
            debug("Turning off nametag for", self.n)
            self.parent.remove_widget(self.nametag)
            self.nametag_on = False

    def on_pos_changed(self, *_):
        Root().ids.agora.clear_dist_cache()

    def update_color(self):
        yellow = (1.0, 1.0, 0.0)
        purple = (1.0, 0.0, 1.0)
        w = self.principal_weight()
        self.color = [sum(x) for x in zip([w * y for y in yellow], [(1-w) * p for p in purple])]

    def talk_to(self, hearer):
        Speaker.talk_to(self, hearer)
        if self.parent.graphics_on:
            hearer.update_color()

class BroadcasterSpeakerDot(SpeakerDot):
    """The GUI representation of a broadcasting speaker who never listens to anyone."""

    def __init__(self, n, pos, para=None, experience=1.0, **kwargs):
        super().__init__(n, pos, para, experience, **kwargs)
        self.is_broadcaster = True
        self.update_color()

    def update_color(self):
        self.color = (0.2, 0.9, 0.1)

class NameTag(Label):
    """A kind of tooltip that shows how biased a speaker is at the moment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _window, pos):
        self.pos[0] = pos[0] - Root().ids.rel_layout.pos[0]
        self.pos[1] = pos[1] - Root().ids.rel_layout.pos[1]

class AgoraWidget(Widget, Agora):
    """An agora of speakers visualized on the screen."""

    def __init__(self, speakers=[], **kwargs):
        Widget.__init__(self, **kwargs)
        Agora.__init__(self)
        self.speakers = speakers
        self.sim = None
        self.pick = []
        self.talk_arrow = None
        self.graphics_on = True

    def add_speakerdot(self, speakerdot):
        """Add a virtual speaker to the simulated community."""
        self.speakers.append(speakerdot)
        self.add_widget(speakerdot)

    def clear_talk_arrow(self):
        """Remove blue arrow from screen."""
        if self.talk_arrow:
            self.canvas.remove(self.talk_arrow)
            self.talk_arrow = None

    def clear_speakers(self):
        """Remove all simulated speakers."""
        super().clear_speakers()
        self.clear_widgets()
        self.clear_talk_arrow()

    def load_speakers(self, speakers):
        """Add an array of pre-built Speakers."""
        for s in speakers:
            self.add_speakerdot(SpeakerDot.fromspeaker(s))

    def start_stop_sim(self, fastforward=False):
        """Schedule simulation to repeat in Kivy event loop."""
        if not self.sim:
            debug("Starting simulation...")
            if fastforward:
                self.sim = Clock.schedule_interval(partial(self.simulate_till_stable, 100), 0.0)
            else:
                slowdown = Root().ids.button_layout.ids.speed_slider.value
                self.sim = Clock.schedule_interval(self.simulate, 1.0 - 0.01 * slowdown)
        else:
            self.stop_sim()

    def stop_sim(self, fastforward=False):
        """Unschedule previously scheduled simulation callback."""
        if self.sim:
            self.sim.cancel()
            self.sim = None
            start_stop_button = Root().ids.button_layout.ids.start_stop_button
            start_stop_button.update_text()

    def simulate(self, *_):
        """Perform a single step of simulation: let one speaker talk to another."""
        super().simulate(*_)
        self.update_talk_arrow()

    def simulate_till_stable(self, batch_size=100, *_):
        """Keep running the simulation until the stability condition is reached."""
        graphics_on_before = self.graphics_on
        self.graphics_on = False
        done = super().simulate_till_stable(batch_size)
        self.graphics_on = graphics_on_before
        if done:
            self.stop_sim()
            ff_button = Root().ids.button_layout.ids.fast_forward_button
            ff_button.popup.dismiss()
            self.pick = None
            self.update_speakerdot_colors()
        else:
            self.update_progressbar(self.sim_iteration)

    def update_talk_arrow(self):
        """Redraw the blue arrow between the current speaker and the current hearer."""
        if not self.graphics_on:
            return
        self.clear_talk_arrow()
        if self.pick:
            speaker_x = self.pick[0].pos[0]+10
            speaker_y = self.pick[0].pos[1]+10
            hearer_x  = self.pick[1].pos[0]+10
            hearer_y  = self.pick[1].pos[1]+10
            length = sqrt((hearer_x - speaker_x)**2 + (hearer_y - speaker_y)**2)
            sin_a = (hearer_y - speaker_y) / length
            cos_a = (hearer_x - speaker_x) / length
            self.talk_arrow = Line(points=[speaker_x, speaker_y,
                                           hearer_x, hearer_y,
                                           hearer_x - 12.0*cos_a - 8.0*sin_a, hearer_y - 12.0*sin_a + 8.0*cos_a,
                                           hearer_x, hearer_y,
                                           hearer_x - 12.0*cos_a + 8.0*sin_a, hearer_y - 12.0*sin_a - 8.0*cos_a],
                                           width=2)
            self.canvas.add(Color(0.2, 0.0, 0.8))
            self.canvas.add(self.talk_arrow)

    def update_speakerdot_colors(self):
        """Set the colors of all speakers according to their current state."""
        if not self.graphics_on:
            return
        for s in self.speakers:
            s.update_color()

    def update_progressbar(self, sim_iteration):
        """Display number of simulation cycles performed in the progress bar popup."""
        ff_button = Root().ids.button_layout.ids.fast_forward_button
        progressbar = ff_button.popup.ids.container.children[0].ids.progressbar
        progressbar.value = sim_iteration

class DemoAgoraWidget1(AgoraWidget):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for row in range(10):
            for col in range(10):
                weight_b = 1 / 18 * (row + col)
                pos = self.width * 0.1 + self.width * 0.09 * col - 10, self.height * 0.9 - self.height * 0.09 * row - 10
                self.add_speakerdot(SpeakerDot(row*10 + col, pos, 1 - weight_b))
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget2(AgoraWidget):
    """A 10x10 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for row in range(10):
            for col in range(10):
                pos = self.width * 0.1 + self.width * 0.09 * col - 10, self.height * 0.9 - self.height * 0.09 * row - 10
                if (3 <= row and row <= 6 and 3 <= col and col <= 6):
                    self.add_speakerdot(SpeakerDot(row*10 + col, pos, 0.0))
                else:
                    self.add_speakerdot(SpeakerDot(row*10 + col, pos, 0.5))
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget3(AgoraWidget):
    """A circle of neutral speakers around a biased broadcaster."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 150
            y = cos(2 * pi * float(n) / 16) * 150
            pos = (300 + x, 300 + y)
            self.add_speakerdot(SpeakerDot(n, pos, 0.5))
        broadcaster = BroadcasterSpeakerDot(16, (300, 300), 1.0)
        self.add_speakerdot(broadcaster)
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget4(AgoraWidget):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 100
            y = cos(2 * pi * float(n) / 16) * 100
            pos = (300 + x, 300 + y)
            self.add_speakerdot(SpeakerDot(n, pos, 0.0))
        for n in range(24):
            x = sin(2 * pi * float(n) / 24) * 200
            y = cos(2 * pi * float(n) / 24) * 200
            pos = (300 + x, 300 + y)
            self.add_speakerdot(SpeakerDot(n, pos, 1.0))
        self.unbind(size=self.populate)
        self.save_starting_state()

def Root():
    return App.get_running_app().root

class MurmurApp(App):
    def build(self):
        self.icon = "assets/logo.png"
        KeyeventHandler()
        return TopBoxLayout()

if __name__ == '__main__':
    MurmurApp().run()
