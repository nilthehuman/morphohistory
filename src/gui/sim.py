"""The contents of the main Simulate tab: the Agora and the control buttons to the right."""

from copy import deepcopy
from functools import partial
from json import JSONDecodeError
from logging import debug, info
from math import sqrt
from os.path import isfile, join

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.properties import ColorProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.slider import Slider
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget

from ..settings import SETTINGS
from ..agora import Agora
from ..demos import DEFAULT_DEMO
from ..speaker import Speaker

# aliases for tediously long Widget and Layout lookups
def _get_root():
    return App.get_running_app().root

def _get_agora():
    return App.get_running_app().root.ids.sim_layout.ids.agora

def _get_agora_layout():
    return App.get_running_app().root.ids.sim_layout.ids.agora_layout

def _get_button_layout():
    return App.get_running_app().root.ids.sim_layout.ids.button_layout

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
            _get_agora().start_stop_sim()
            return True
        if keycode[1] == 'f':
            _get_agora().start_stop_sim(fastforward=True)
            return True
        if keycode[1] == 'r':
            _get_agora().stop_sim()
            _get_agora().reset()
            return True
        if keycode[1] == 'q':
            info("KeyeventHandler: Exiting app...")
            App.get_running_app().stop()
            return True
        return False

class SimLayout(BoxLayout):
    """The horizontal BoxLayout holding all the contents of the Simulation tab."""
    pass

class CenterLayout(AnchorLayout, StencilView):
    """The main rectangular area on the simulation tab, puts the AgoraLayout in the center."""
    pass

class AgoraLayout(ScatterLayout):
    """The scalable layout that holds the AgoraWidget."""
    def on_touch_up(self, touch):
        """Handle zooming in or out by mouse wheel."""
        if touch.is_mouse_scrolling:
            if touch.button == 'scrolldown':
                factor = 1.02
            if touch.button == 'scrollup':
                factor = 1 / 1.02
            self.apply_transform(Matrix().scale(factor, factor, 1), anchor=self.center)
        super().on_touch_up(touch)

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

class OverwritePopup(BoxLayout):
    """A popup window to ask the user for confirmation cobbling an existing file."""
    proceed = ObjectProperty(None)
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
        self.popup = None
        self.overwrite_popup = None
        self.bind(on_release=self.show_save_popup)

    def show_save_popup(self, *_):
        """Open the main file saving dialogue popup."""
        _get_agora().stop_sim()
        content = SaveToFilePopup(save=self.save, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora mentése", content=content,
                           size_hint=(None, None), size=SETTINGS.popup_size_load)
        self.popup.open()

    def dismiss_popup(self):
        """Close the main file saving dialogue popup."""
        self.popup.dismiss()

    def save(self, path, filename):
        """Write current Agora state to file unless given filename exists."""
        fullpath = join(path, filename)
        if isfile(fullpath):
            self.show_overwrite_popup()
        else:
            _get_agora().save_to_file(fullpath)
            self.dismiss_popup()

    def show_overwrite_popup(self, *_):
        """Open another popup to ask for permission to overwrite existing file."""
        content = OverwritePopup(proceed=self.proceed, cancel=self.dismiss_overwrite_popup)
        self.overwrite_popup = Popup(title="Meglévő fájl!", content=content,
                                     size_hint=(None, None), size=SETTINGS.popup_size_fail)
        self.overwrite_popup.open()

    def proceed(self):
        """Overwrite existing file anyway per user's request."""
        filechooser = self.popup.ids.container.children[0].ids.filechooser
        text_input = self.popup.ids.container.children[0].ids.text_input
        fullpath = join(filechooser.path, text_input.text)
        _get_agora().save_to_file(fullpath)
        self.dismiss_overwrite_popup()
        self.dismiss_popup()

    def dismiss_overwrite_popup(self):
        """Close nested dialogue popup about overwriting existing file."""
        self.overwrite_popup.dismiss()

class LoadFromFileButton(Button):
    """Opens a popup window for loading an Agora configuration from file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
        self.fail_popup = None
        self.bind(on_release=self.show_load_popup)

    def show_load_popup(self, *_):
        """Open the main file loading dialogue popup."""
        _get_agora().stop_sim()
        content = LoadFromFilePopup(load=self.load, cancel=self.dismiss_popup)
        self.popup = Popup(title="Agora betöltése", content=content,
                           size_hint=(None, None), size=SETTINGS.popup_size_load)
        self.popup.open()

    def load(self, _path, fileselection):
        """Read and set new Agora state from file."""
        if not fileselection:
            return
        fullpath = fileselection[0]
        try:
            _get_agora().load_from_file(fullpath)
            self.dismiss_popup()
        except (JSONDecodeError, UnicodeDecodeError, TypeError):
            self.show_fail_popup()

    def dismiss_popup(self):
        """Close the main file loading dialogue popup."""
        self.popup.dismiss()

    def show_fail_popup(self):
        """Open another popup to let the user know the file could not be loaded."""
        content = LoadFailedPopup(okay=self.dismiss_fail_popup)
        self.fail_popup = Popup(title="Sikertelen betöltés", content=content,
                                size_hint=(None, None), size=SETTINGS.popup_size_fail)
        self.fail_popup.open()

    def dismiss_fail_popup(self):
        """Close nested dialogue popup about unsuccessful loading."""
        self.fail_popup.dismiss()

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
        """Start or resume the simulation if not running, stop if already running."""
        _get_agora().start_stop_sim()
        self.update_text()

    def update_text(self):
        """Toggle button text to show what the button will do next."""
        self.text = self.stop_text if _get_agora().sim else self.start_text

class RewindButton(Button):
    """Restores the initial state of the Agora when loaded."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.rewind)

    def rewind(self, *_):
        """Reset the state of the simulation to the the original state."""
        _get_agora().stop_sim()
        _get_agora().reset()

class FastForwardButton(Button):
    """Keeps running the simulation until a stable state is reached."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
        self.bind(on_release=self.fastforward)

    def fastforward(self, *_):
        """Perform many iterations of the simulation at once ignoring graphics."""
        _get_agora().stop_sim()
        content = FastForwardPopup(cancel=self.cancel_fast_forward)
        self.popup = Popup(title="Folyamatban...", content=content,
                           size_hint=(None, None), size=SETTINGS.popup_size_progress)
        self.popup.open()
        _get_agora().start_stop_sim(fastforward=True)

    def cancel_fast_forward(self, *_):
        """Stop the running simulation early."""
        if _get_agora().sim:
            _get_agora().sim_cancelled = True

class SpeedSlider(Slider):
    """Used to set the idle time between simulation steps."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_move=self.adjust_sim_speed)
        self.bind(on_touch_up=self.adjust_sim_speed)

    def adjust_sim_speed(self, *_):
        """Speed up or slow down the running graphical (non-fast-forward) simulation."""
        if _get_agora().sim:
            _get_agora().restart_sim()

class IterationCounter(Label):
    """Displays the number of iterations simulated so far."""
    pass

class SpeakerDot(Speaker, DragBehavior, Widget):
    """The visual representation of a single speaker on the GUI."""

    color = ColorProperty()

    def __init__(self, n, pos, para, experience, **kwargs):
        Speaker.__init__(self, n, pos, para, False, experience)
        DragBehavior.__init__(self, **kwargs)
        Widget.__init__(self, **kwargs)
        self.size = SETTINGS.speakerdot_size
        self.update_color()
        self.nametag = NameTag(text=str(n) + ': ' + self.name_tag())
        self.nametag_on = False
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.bind(pos=self.on_pos_changed)
        self.bind(on_touch_up=self.on_right_click)

    @classmethod
    def fromspeaker(cls, speaker):
        """Copy an existing Speaker."""
        if speaker.is_broadcaster:
            return BroadcasterSpeakerDot(speaker.n, speaker.pos, deepcopy(speaker.para), speaker.experience)
        return SpeakerDot(speaker.n, speaker.pos, deepcopy(speaker.para), speaker.experience)

    def on_mouse_pos(self, _window, pos):
        """Show/hide NameTag on hover."""
        if not self.parent:
            # why do SpeakerDots stay alive after AgoraWidget.clear_widgets(), this is stupid
            return
        if not self.parent.graphics_on:
            return
        if _get_root().current_tab != _get_root().tab_list[-1]:
            # user's looking at a different tab right now
            return
        pos = _get_agora_layout().transform_inv.transform_point(*pos, 0)
        if self.collide_point(pos[0], pos[1]):
            if not self.nametag_on:
                debug("SpeakerDot: Turning on nametag for %d" % self.n)
                self.nametag.text = str(self.n) + ': ' + self.name_tag()
                self.parent.add_widget(self.nametag)
                self.nametag_on = True
        elif self.nametag_on:
            debug("SpeakerDot: Turning off nametag for %d" % self.n)
            self.parent.remove_widget(self.nametag)
            self.nametag_on = False

    def on_pos_changed(self, *_):
        """Invalidate the whole distance calculation cache when any speaker is moved."""
        _get_agora().clear_dist_cache()

    def on_right_click(self, _instance, touch):
        """Remove this speaker when right clicked."""
        if touch.button == 'right' and self.collide_point(*touch.pos):
            self.parent.remove_widget(self.nametag)
            self.nametag_on = False
            _get_agora().remove_speakerdot(self)
        else:
            pass # no need to propagate upwards to DragBehavior

    def update_color(self):
        """Refresh own color based on current paradigm bias."""
        color_a = SETTINGS.color_a
        color_b = SETTINGS.color_b
        bias = self.principal_bias()
        self.color = [sum(x) for x in zip([bias * c for c in color_a.rgb],
                                          [(1-bias) * c for c in color_b.rgb])]

    def talk(self, pick):
        """Interact with and influence another Speaker in the Agora."""
        Speaker.talk(self, pick)
        if self.parent.graphics_on:
            pick['hearer'].update_color()
            if SETTINGS.sim_influence_self:
                pick['speaker'].update_color()

class BroadcasterSpeakerDot(SpeakerDot):
    """The GUI representation of a broadcasting speaker who never listens to anyone."""

    def __init__(self, n, pos, para, experience, **kwargs):
        super().__init__(n, pos, para, experience, **kwargs)
        self.is_broadcaster = True
        self.update_color()

    def update_color(self):
        """Set own color to special color to stand apart from the rest of the speakers."""
        self.color = SETTINGS.color_broadcaster.rgb

# TODO: use a single global NameTag for all SpeakerDots
class NameTag(Label):
    """A kind of tooltip that shows how biased a speaker is at the moment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _window, pos):
        """Follow hovering mouse cursor."""
        transformed_pos = _get_agora_layout().transform_inv.transform_point(*pos, 0)
        self.pos = transformed_pos[0:2]

class AgoraWidget(Widget, Agora):
    """An agora of speakers visualized on the screen."""

    def __init__(self, speakers=None, **kwargs):
        Widget.__init__(self, **kwargs)
        Agora.__init__(self)
        self.state.speakers = speakers if speakers else []
        self.sim = None
        self.pick = []
        self.slowdown_prev = None
        self.distance_metric_prev = SETTINGS.sim_distance_metric
        self.talk_arrow_shaft = None
        self.talk_arrow_tip = None
        self.graphics_on = True
        self.bind(size=self.on_size)
        self.bind(on_touch_up=self.change_tab_manually)

    def on_size(self, *_):
        """Finish initializing: draw the grid and load the default speaker population."""
        self.update_grid()
        self.update_iteration_counter()
        speakers = DEFAULT_DEMO.get_speakers()
        self.load_speakers(speakers)
        self.save_starting_state()
        self.unbind(size=self.on_size)

    def change_tab_manually(self, instance, touch):
        """Workaround to enable tab switching if AgoraWidget overlaps with tab strip.
        (The Scatter widget above the AgoraWidget stops and claims the touch)"""
        for tab in _get_root().tab_list:
            if tab.collide_point(*tab.to_widget(*touch.pos)):
                _get_root().switch_to(tab)
                return True
        return False

    def reset(self):
        """Reset state to earlier speaker snapshot."""
        super().reset()
        self.update_iteration_counter()

    def load_from_file(self, filepath):
        """Restore an Agora state previously written to file."""
        super().load_from_file(filepath)
        self.update_iteration_counter()

    def add_speakerdot(self, speakerdot):
        """Add a virtual speaker to the simulated community."""
        self.state.speakers.append(speakerdot)
        self.add_widget(speakerdot)
        self.clear_caches()

    def remove_speakerdot(self, speakerdot):
        """Remove a virtual speaker from the simulated community."""
        self.remove_widget(speakerdot)
        self.state.speakers.remove(speakerdot)
        self.clear_caches()

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
        for speaker in speakers:
            self.add_speakerdot(SpeakerDot.fromspeaker(speaker))

    def start_sim(self):
        """Schedule regular simulation in Kivy event loop at intervals specified by the slider."""
        assert not self.sim
        slowdown = _get_button_layout().ids.speed_slider.value
        self.sim = Clock.schedule_interval(self.simulate, 1.0 - 0.01 * slowdown)
        self.slowdown_prev = slowdown

    def start_stop_sim(self, fastforward=False):
        """Schedule or unschedule simulation based on current state."""
        if not self.sim:
            if fastforward:
                if self.graphics_on:
                    self.clear_talk_arrow()
                debug("AgoraWidget: Scheduling fast forward simulation...")
                batch_size = SETTINGS.sim_batch_size
                sim_callback = partial(self.simulate_till_stable, batch_size=batch_size)
                self.sim = Clock.schedule_interval(sim_callback, 0.0)
            else:
                debug("AgoraWidget: Scheduling graphical simulation...")
                self.start_sim()
        else:
            debug("AgoraWidget: Unscheduling simulation...")
            self.stop_sim()

    def restart_sim(self):
        """Reschedule simulation with different sleep timing."""
        if self.sim:
            slowdown = _get_button_layout().ids.speed_slider.value
            if self.slowdown_prev != slowdown:
                self.sim.cancel()
                self.sim = None
                self.start_sim()

    def stop_sim(self):
        """Unschedule previously scheduled simulation callback."""
        if self.sim:
            self.sim.cancel()
            self.sim = None
            start_stop_button = _get_button_layout().ids.start_stop_button
            start_stop_button.update_text()

    def simulate(self, *_):
        """Perform a single step of simulation: let one speaker talk to another."""
        super().simulate(*_)
        self.update_talk_arrow()
        self.update_iteration_counter()

    def simulate_till_stable(self, *_, batch_size=None):
        """Keep running the simulation until the stability condition is reached."""
        graphics_on_before = self.graphics_on
        self.graphics_on = False
        done = super().simulate_till_stable(batch_size=batch_size)
        self.graphics_on = graphics_on_before
        if done:
            self.stop_sim()
            ff_button = _get_button_layout().ids.fast_forward_button
            if ff_button.popup:
                ff_button.popup.dismiss()
            self.pick = None
            self.update_speakerdot_colors()
        else:
            self.update_progressbar(self.sim_iteration)

    def show_euclidean_grid(self):
        """Draw a grid with circles behind the Agora to suggest the use of Euclidean distance."""
        if not self.graphics_on:
            return
        self.show_manhattan_grid()
        half_sqrt_2 = 1 / sqrt(2)
        bottom = (0.5 - half_sqrt_2) * self.height
        top    = (0.5 + half_sqrt_2) * self.height
        left   = (0.5 - half_sqrt_2) * self.width
        right  = (0.5 + half_sqrt_2) * self.width
        self.canvas.before.add(Line(points=[left, bottom, right, top], width=1))
        self.canvas.before.add(Line(points=[left, top, right, bottom], width=1))
        step = int(self.width / SETTINGS.grid_resolution)
        for radius in range(step, int(sqrt(2) * self.width/2), step):
            self.canvas.before.add(Line(circle=(self.width/2, self.height/2, radius), width=1))

    def show_manhattan_grid(self):
        """Draw a grey Cartesian grid behind the Agora to suggest the use of Manhattan distance."""
        if not self.graphics_on:
            return
        half_sqrt_2 = 1 / sqrt(2)
        bottom = (0.5 - half_sqrt_2) * self.height
        top    = (0.5 + half_sqrt_2) * self.height
        left   = (0.5 - half_sqrt_2) * self.width
        right  = (0.5 + half_sqrt_2) * self.width
        step_x = int(self.width  / SETTINGS.grid_resolution)
        step_y = int(self.height / SETTINGS.grid_resolution)
        self.canvas.before.add(SETTINGS.grid_color)
        for delta_x in range(0, int(half_sqrt_2 * self.width), step_x):
            self.canvas.before.add(Line(points=[self.width/2 + delta_x,
                                                bottom,
                                                self.width/2 + delta_x,
                                                top],
                                                width=1))
            self.canvas.before.add(Line(points=[self.width/2 - delta_x,
                                                bottom,
                                                self.width/2 - delta_x,
                                                top],
                                                width=1))
        for delta_y in range(0, int(half_sqrt_2 * self.height), step_y):
            self.canvas.before.add(Line(points=[left,
                                                self.height/2 + delta_y,
                                                right,
                                                self.height/2 + delta_y],
                                                width=1))
            self.canvas.before.add(Line(points=[left,
                                                self.height/2 - delta_y,
                                                right,
                                                self.height/2 - delta_y],
                                                width=1))

    def update_grid(self, *_):
        """Show/hide the grid behind the Agora."""
        if not self.graphics_on:
            return
        if self.canvas.has_before and self.distance_metric_prev == SETTINGS.sim_distance_metric:
            # leave grid as it is
            pass
        else:
            if self.canvas.has_before and self.canvas.before.length():
                self.canvas.before.clear()
            if SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.CONSTANT:
                pass
            elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.MANHATTAN:
                self.show_manhattan_grid()
            elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.EUCLIDEAN:
                self.show_euclidean_grid()
            else:
                assert False
        self.distance_metric_prev = SETTINGS.sim_distance_metric

    def update_iteration_counter(self):
        """Set the text on the button panel that shows how deep into the simulation we are."""
        iter_counter = _get_button_layout().ids.iteration_counter
        iter_counter.text = '%d iteráció' % self.state.sim_iteration_total

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
            self.talk_arrow_shaft = Line(points=[speaker_x, speaker_y,
                                                 hearer_x, hearer_y],
                                                 width=width)
            self.talk_arrow_tip = Line(points=[hearer_x - 12.0 * cos_a - 8.0 * sin_a,
                                               hearer_y - 12.0 * sin_a + 8.0 * cos_a,
                                               hearer_x, hearer_y,
                                               hearer_x - 12.0 * cos_a + 8.0 * sin_a,
                                               hearer_y - 12.0 * sin_a - 8.0 * cos_a],
                                               width=width)
            color_arrow_shaft = None
            if self.pick['is_form_a']:
                color_arrow_shaft = SETTINGS.color_a.rgb
            else:
                color_arrow_shaft = SETTINGS.color_b.rgb
            color_arrow_shaft = (0.85 * color_arrow_shaft[0],
                                 0.85 * color_arrow_shaft[1],
                                 0.85 * color_arrow_shaft[2])
            self.canvas.add(Color(*color_arrow_shaft))
            self.canvas.add(self.talk_arrow_shaft)
            self.canvas.add(SETTINGS.color_arrow_tip)
            self.canvas.add(self.talk_arrow_tip)

    def update_speakerdot_colors(self):
        """Set the colors of all speakers according to their current state."""
        if not self.graphics_on:
            return
        for speaker in self.state.speakers:
            speaker.update_color()

    def update_progressbar(self, sim_iteration):
        """Display number of simulation cycles performed in the progress bar popup."""
        ff_button = _get_button_layout().ids.fast_forward_button
        if ff_button.popup:
            progressbar = ff_button.popup.ids.container.children[0].ids.progressbar
            progressbar.value = sim_iteration
