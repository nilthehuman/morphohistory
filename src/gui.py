"""The app's GUI built with the Kivy toolkit"""

import kivy
kivy.require('2.1.0')

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import ColorProperty, ObjectProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.widget import Widget

from copy import deepcopy
from functools import partial
from json import JSONDecodeError
from logging import debug
from math import sqrt
from os.path import isfile, join

from .settings import SETTINGS
from .agora import Agora
from .demos import DEFAULT_DEMO
from .speaker import Speaker

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

class TopTabbedPanel(TabbedPanel):
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

class LoadFailedPopup(BoxLayout):
    """A popup window to let the user know their file could not be loaded."""
    okay = ObjectProperty(None)

class FastForwardPopup(BoxLayout):
    """A popup window to show the progress of a fast forward."""
    cancel = ObjectProperty(None)

class SaveToFileButton(Button):
    """Opens a popup window for writing the current configuration of the Agora to file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.show_save_popup)

    def show_save_popup(self, *_):
        Root().ids.agora.stop_sim()
        content = SaveToFilePopup(save=self.save, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora mentése", content=content, size_hint=(None, None), size=SETTINGS.popup_size_load)
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def save(self, path, filename):
        fullpath = join(path, filename)
        savebutton = self.popup.ids.container.children[0].ids.save_button
        if isfile(fullpath) and savebutton.text != "Felülírjam?":
            savebutton.text = "Felülírjam?"
            return
        Root().ids.agora.save_to_file(fullpath)
        self.dismiss_popup()

class LoadFromFileButton(Button):
    """Opens a popup window for loading an Agora configuration from file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.show_load_popup)

    def show_load_popup(self, *_):
        Root().ids.agora.stop_sim()
        content = LoadFromFilePopup(load=self.load, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora betöltése", content=content, size_hint=(None, None), size=SETTINGS.popup_size_load)
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def dismiss_fail_popup(self):
        self.fail_popup.dismiss()

    def load(self, _path, fileselection):
        if not fileselection:
            return
        fullpath = fileselection[0]
        try:
            Root().ids.agora.load_from_file(fullpath)
            self.dismiss_popup()
        except (JSONDecodeError, TypeError):
            content = LoadFailedPopup(okay=self.dismiss_fail_popup)
            self.fail_popup = Popup(title="Sikertelen betöltés", content=content, size_hint=(None, None), size=SETTINGS.popup_size_fail)
            self.fail_popup.open()

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
        self.popup = Popup(title="Folyamatban...", content=content, size_hint=(None, None), size=SETTINGS.popup_size_progress)
        self.popup.open()
        Root().ids.agora.clear_talk_arrow()
        Root().ids.agora.start_stop_sim(fastforward=True)

    def cancel_fast_forward(self, *_):
        if Root().ids.agora.sim:
            Root().ids.agora.sim_cancelled = True

class SpeedSlider(Slider):
    """Used to set the idle time between simulation steps."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_move=self.adjust_sim_speed)
        self.bind(on_touch_up=self.adjust_sim_speed)

    def adjust_sim_speed(self, *_):
        if Root().ids.agora.sim:
            Root().ids.agora.restart_sim()

class SpeakerDot(Speaker, DragBehavior, Widget):
    """The visual representation of a single speaker on the GUI."""

    color = ColorProperty()

    def __init__(self, n, pos, para=None, experience=SETTINGS.experience_start, **kwargs):
        Speaker.__init__(self, n, pos, para, False, experience)
        DragBehavior.__init__(self, **kwargs)
        Widget.__init__(self, **kwargs)
        self.size = SETTINGS.speakerdot_size
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
        if self.collide_point(*pos):
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
        color_A = SETTINGS.color_A
        color_B = SETTINGS.color_B
        w = self.principal_weight()
        self.color = [sum(x) for x in zip([w * c for c in color_A], [(1-w) * c for c in color_B])]

    def talk(self, pick):
        Speaker.talk(self, pick)
        if self.parent.graphics_on:
            pick['hearer'].update_color()

class BroadcasterSpeakerDot(SpeakerDot):
    """The GUI representation of a broadcasting speaker who never listens to anyone."""

    def __init__(self, n, pos, para=None, experience=SETTINGS.experience_start, **kwargs):
        super().__init__(n, pos, para, experience, **kwargs)
        self.is_broadcaster = True
        self.update_color()

    def update_color(self):
        self.color = SETTINGS.color_broadcaster

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
        self.slowdown_prev = None
        self.pick = []
        self.talk_arrow_shaft = None
        self.talk_arrow_tip = None
        self.graphics_on = True
        self.bind(size=self.on_size)

    def add_speakerdot(self, speakerdot):
        """Add a virtual speaker to the simulated community."""
        self.speakers.append(speakerdot)
        self.add_widget(speakerdot)

    def clear_talk_arrow(self):
        """Remove blue arrow from screen."""
        if self.talk_arrow_shaft:
            self.canvas.remove(self.talk_arrow_shaft)
            self.talk_arrow_shaft = None
        if self.talk_arrow_tip:
            self.canvas.remove(self.talk_arrow_tip)
            self.talk_arrow_tip = None

    def clear_speakers(self):
        """Remove all simulated speakers."""
        super().clear_speakers()
        self.clear_widgets()
        self.clear_talk_arrow()

    def load_speakers(self, speakers):
        """Add an array of pre-built Speakers."""
        for s in speakers:
            self.add_speakerdot(SpeakerDot.fromspeaker(s))

    def on_size(self, *_):
        """Finish initializing: draw the grid and load the default speaker population."""
        self.update_grid() # TODO: update when setting is changed
        speakers = DEFAULT_DEMO.get_speakers()
        self.load_speakers(speakers)
        self.save_starting_state()
        self.unbind(size=self.on_size)

    def start_sim(self):
        """Schedule regular simulation in Kivy event loop at intervals specified by the slider."""
        assert not self.sim
        slowdown = Root().ids.button_layout.ids.speed_slider.value
        self.sim = Clock.schedule_interval(self.simulate, 1.0 - 0.01 * slowdown)
        self.slowdown_prev = slowdown

    def start_stop_sim(self, fastforward=False):
        """Schedule or unschedule simulation based on current state."""
        if not self.sim:
            debug("Starting simulation...")
            if fastforward:
                batch_size = SETTINGS.sim_batch_size
                self.sim = Clock.schedule_interval(partial(self.simulate_till_stable, batch_size), 0.0)
            else:
                self.start_sim()
        else:
            self.stop_sim()

    def restart_sim(self):
        """Reschedule simulation with different sleep timing."""
        if self.sim:
            slowdown = Root().ids.button_layout.ids.speed_slider.value
            if self.slowdown_prev != slowdown:
                self.sim.cancel()
                self.sim = None
                self.start_sim()

    def stop_sim(self):
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

    def simulate_till_stable(self, batch_size=None, *_):
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

    def toggle_euclidean_grid(self, force_show=False):
        """Show/hide a grid with circles behind the Agora to suggest the use of Euclidean distance."""
        if not self.graphics_on:
            return
        if self.canvas.has_before and self.canvas.before.length():
            if not force_show:
                self.canvas.before.clear()
        else:
            self.toggle_manhattan_grid(force_show=True)
            half_sqrt_2 = 1 / sqrt(2)
            bottom = (0.5 - half_sqrt_2) * self.height
            top    = (0.5 + half_sqrt_2) * self.height
            left   = (0.5 - half_sqrt_2) * self.width
            right  = (0.5 + half_sqrt_2) * self.width
            self.canvas.before.add(Color(*SETTINGS.grid_color))
            self.canvas.before.add(Line(points=[left, bottom, right, top], width=1))
            self.canvas.before.add(Line(points=[left, top, right, bottom], width=1))
            step = int(self.width / SETTINGS.grid_resolution)
            for r in range(step, int(sqrt(2) * self.width/2), step):
                self.canvas.before.add(Line(circle=(self.width/2, self.height/2, r), width=1))

    def toggle_manhattan_grid(self, force_show=False):
        """Show/hide a grey Cartesian grid behind the Agora to suggest the use of Manhattan distance."""
        if not self.graphics_on:
            return
        if self.canvas.has_before and self.canvas.before.length():
            if not force_show:
                self.canvas.before.clear()
        else:
            half_sqrt_2 = 1 / sqrt(2)
            bottom = (0.5 - half_sqrt_2) * self.height
            top    = (0.5 + half_sqrt_2) * self.height
            left   = (0.5 - half_sqrt_2) * self.width
            right  = (0.5 + half_sqrt_2) * self.width
            step_x = int(self.width  / SETTINGS.grid_resolution)
            step_y = int(self.height / SETTINGS.grid_resolution)
            self.canvas.before.add(Color(*SETTINGS.grid_color))
            for x in range(0, int(half_sqrt_2 * self.width), step_x):
                self.canvas.before.add(Line(points=[self.width/2 + x, bottom, self.width/2 + x, top], width=1))
                self.canvas.before.add(Line(points=[self.width/2 - x, bottom, self.width/2 - x, top], width=1))
            for y in range(0, int(half_sqrt_2 * self.height), step_y):
                self.canvas.before.add(Line(points=[left, self.height/2 + y, right, self.height/2 + y], width=1))
                self.canvas.before.add(Line(points=[left, self.height/2 - y, right, self.height/2 - y], width=1))

    def update_grid(self, *_):
        """Show/hide the grid behind the Agora."""
        if not self.graphics_on:
            return
        if SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.CONSTANT:
            if self.canvas.has_before and self.canvas.before.length():
                self.canvas.before.clear()
        elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.MANHATTAN:
            self.toggle_manhattan_grid(force_show=True)
        elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.EUCLIDEAN:
            self.toggle_euclidean_grid(force_show=True)
        else:
            assert False

    def update_talk_arrow(self):
        """Redraw the blue arrow between the current speaker and the current hearer."""
        if not self.graphics_on or not SETTINGS.draw_arrow:
            return
        self.clear_talk_arrow()
        if self.pick:
            dot_size = SETTINGS.speakerdot_size
            speaker_x = self.pick['speaker'].pos[0] + 0.5 * dot_size[0]
            speaker_y = self.pick['speaker'].pos[1] + 0.5 * dot_size[1]
            hearer_x = self.pick['hearer'].pos[0] + 0.5 * dot_size[0]
            hearer_y = self.pick['hearer'].pos[1] + 0.5 * dot_size[1]
            length = sqrt((hearer_x - speaker_x)**2 + (hearer_y - speaker_y)**2)
            sin_a = (hearer_y - speaker_y) / length
            cos_a = (hearer_x - speaker_x) / length
            width = SETTINGS.arrow_width
            self.talk_arrow_shaft = Line(points=[speaker_x, speaker_y, hearer_x, hearer_y], width=width)
            self.talk_arrow_tip = Line(points=[hearer_x - 12.0*cos_a - 8.0*sin_a, hearer_y - 12.0*sin_a + 8.0*cos_a,
                                               hearer_x, hearer_y,
                                               hearer_x - 12.0*cos_a + 8.0*sin_a, hearer_y - 12.0*sin_a - 8.0*cos_a],
                                               width=width)
            color_arrow_shaft = None
            if self.pick['is_form_a']:
                color_arrow_shaft = SETTINGS.color_A
            else:
                color_arrow_shaft = SETTINGS.color_B
            color_arrow_shaft = (0.85 * color_arrow_shaft[0], 0.85 * color_arrow_shaft[1], 0.85 * color_arrow_shaft[2])
            self.canvas.add(Color(*color_arrow_shaft))
            self.canvas.add(self.talk_arrow_shaft)
            self.canvas.add(Color(*SETTINGS.color_arrow_tip))
            self.canvas.add(self.talk_arrow_tip)

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

def Root():
    return App.get_running_app().root

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
