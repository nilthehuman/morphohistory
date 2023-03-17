"""The contents of the Tuning tab, where you can do brute force exhaustive simulation
on a variety of model parameters."""

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner

from .access_widgets import get_root, get_agora, get_tuning_menu
from .l10n import localize, unlocalize, LocalizedPopup

from ..agora import Agora
from ..demos import DEMO_FACTORIES, DEFAULT_DEMO_ARGUMENTS
from ..settings import SETTINGS
from ..tuning import Tuner


class TuningTabLayout(BoxLayout):
    """The vertical BoxLayout holding the demo selector Spinner, a few TextInputs to define
    parameter intervals and step, and a Button to launch the parametrized simulation."""
    pass


class ParamBoxLayout(BoxLayout):
    """The horizontal BoxLayout holding three TextInputs for the range of one parameter."""
    label = StringProperty()


class DemoSpinner(Spinner):
    """The Spinner Widget used to select the parametrizable demo agora the user wants to use."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = [localize(factory_name) for factory_name in DEMO_FACTORIES.keys()]

    def on_gui_ready(self):
        """Finish initializing: tell the Agora to load the first demo in the dropdown."""
        self.on_text()

    def on_text(self, *_):
        """Tell the Agora on the main tab to load the selected demo."""
        if not get_root():
            # Widget tree has not been built yet, leave job to on_gui_ready
            return
        selected = unlocalize(self.text)
        SETTINGS.current_demo = selected
        demo_factory = DEMO_FACTORIES[selected]
        get_agora().load_demo_agora(demo_factory, starting_experience=SETTINGS.starting_experience)
        # update suggested default parametrization values
        tuning_menu = get_tuning_menu()
        if DEFAULT_DEMO_ARGUMENTS[selected].our_bias is not None:
            tuning_menu.ids.our_bias_box.disabled = False
            tuning_menu.ids.our_bias_box.ids.start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].our_bias)
            tuning_menu.ids.our_bias_box.ids.stop_input.text = str(abs(1 - DEFAULT_DEMO_ARGUMENTS[selected].our_bias))
            tuning_menu.ids.our_bias_box.ids.step_input.text = '0.1'
        else:
            tuning_menu.ids.our_bias_box.disabled = True
            tuning_menu.ids.our_bias_box.ids.start_input.text = 'N/A'
            tuning_menu.ids.our_bias_box.ids.stop_input.text = 'N/A'
            tuning_menu.ids.our_bias_box.ids.step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].their_bias is not None:
            tuning_menu.ids.their_bias_box.disabled = False
            tuning_menu.ids.their_bias_box.ids.start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].their_bias)
            tuning_menu.ids.their_bias_box.ids.stop_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].their_bias)
            tuning_menu.ids.their_bias_box.ids.step_input.text = '0.1'
        else:
            tuning_menu.ids.their_bias_box.disabled = True
            tuning_menu.ids.their_bias_box.ids.start_input.text = 'N/A'
            tuning_menu.ids.their_bias_box.ids.stop_input.text = 'N/A'
            tuning_menu.ids.their_bias_box.ids.step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].starting_experience is not None:
            tuning_menu.ids.starting_experience_box.disabled = False
            tuning_menu.ids.starting_experience_box.ids.start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].starting_experience)
            tuning_menu.ids.starting_experience_box.ids.stop_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].starting_experience)
            tuning_menu.ids.starting_experience_box.ids.step_input.text = '10'
        else:
            tuning_menu.ids.starting_experience_box.disabled = True
            tuning_menu.ids.starting_experience_box.ids.start_input.text = 'N/A'
            tuning_menu.ids.starting_experience_box.ids.stop_input.text = 'N/A'
            tuning_menu.ids.starting_experience_box.ids.step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].inner_radius is not None:
            tuning_menu.ids.inner_radius_box.disabled = False
            tuning_menu.ids.inner_radius_box.ids.start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].inner_radius)
            tuning_menu.ids.inner_radius_box.ids.stop_input.text = '0.9'
            tuning_menu.ids.inner_radius_box.ids.step_input.text = '0.125'
        else:
            tuning_menu.ids.inner_radius_box.disabled = True
            tuning_menu.ids.inner_radius_box.ids.start_input.text = 'N/A'
            tuning_menu.ids.inner_radius_box.ids.stop_input.text = 'N/A'
            tuning_menu.ids.inner_radius_box.ids.step_input.text = 'N/A'


class TuningProgressPopup(BoxLayout):
    """A popup window to show the progress of the tuning."""
    cancel = ObjectProperty(None)


class LaunchTuningButton(Button):
    """The Button to start the repeated exhaustive simulation of the model parameters
    as defined by the TextInputs above."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tuner = None
        self.bind(on_release=self.start_tuning)

    def start_tuning(self, *_):
        """Start the exhaustive simulation."""
        tuning_menu = get_tuning_menu()
        # fetch the parameter ranges defined by user in the Tuning menu
        # why doesn't Python have macros?
        try:
            our_bias_params = (float(tuning_menu.ids.our_bias_box.ids.start_input.text),
                               float(tuning_menu.ids.our_bias_box.ids.stop_input.text),
                               float(tuning_menu.ids.our_bias_box.ids.step_input.text))
        except ValueError:
            # parameter not available
            our_bias_params = (None, None, None)
        try:
            their_bias_params = (float(tuning_menu.ids.their_bias_box.ids.start_input.text),
                                 float(tuning_menu.ids.their_bias_box.ids.stop_input.text),
                                 float(tuning_menu.ids.their_bias_box.ids.step_input.text))
        except ValueError:
            # parameter not available
            their_bias_params = (None, None, None)
        try:
            starting_experience_params = (int(tuning_menu.ids.starting_experience_box.ids.start_input.text),
                                          int(tuning_menu.ids.starting_experience_box.ids.stop_input.text),
                                          int(tuning_menu.ids.starting_experience_box.ids.step_input.text))
        except ValueError:
            # parameter not available
            starting_experience_params = (None, None, None)
        try:
            inner_radius_params = (float(tuning_menu.ids.inner_radius_box.ids.start_input.text),
                                   float(tuning_menu.ids.inner_radius_box.ids.stop_input.text),
                                   float(tuning_menu.ids.inner_radius_box.ids.step_input.text))
        except ValueError:
            # parameter not available
            inner_radius_params = (None, None, None)
        repetitions = int(tuning_menu.ids.repetition_input.text)

        content = TuningProgressPopup(cancel=self.cancel_tuning)
        self.tuner = TunerPopup(our_bias_params,
                                their_bias_params,
                                starting_experience_params,
                                inner_radius_params,
                                repetitions,
                                title="Crunching numbers, hang tight...",
                                content=content,
                                size_hint=(None, None),
                                size=SETTINGS.popup_size_progress)
        self.tuner.open()
        self.tuner.run()

    def cancel_tuning(self, *_):
        """Stop the simulation midway through."""
        self.tuner.tuning_cancelled = True


class TunerPopup(Tuner, LocalizedPopup):
    """A simple graphical frontend to a Tuner to show its progress live."""

    def __init__(self, *args, **kwargs):
        Tuner.__init__(self, *args)
        LocalizedPopup.__init__(self, **kwargs)
        self.ids.container.children[0].ids.progressbar.max = self.num_total_setups * self.repetitions

    def run(self):
        """Schedule our own method driving the tuning in the Kivy event loop."""
        # attention: this method does *not* call its base class equivalent on purpose!
        self.on_start()
        self.tuning_event = Clock.schedule_interval(self.iterate_tuning, 0.0)

    def iterate_tuning(self, *_):
        """Repeat the simulation several times for each parameter setup in the set of
        parameter combinations chosen by the user, then dump the results in a CSV file."""
        try:
            super().iterate_tuning()
            # update progress bar
            self.ids.container.children[0].ids.progressbar.value = self.num_total_reps
        except (Tuner.Cancelled, Tuner.Finished) as stop_except:
            # unschedule ourselves from Kivy event loop
            self.tuning_event.cancel()
            self.dismiss()
            if isinstance(stop_except, Tuner.Cancelled):
                self.on_cancelled()
            else:
                self.on_finished()

    def prepare_next_setup(self):
        """Initialize Agora according to next parameter setup."""
        super().prepare_next_setup()
        self.ids.container.children[0].ids.progress_label.text = \
            localize("Running parameter setup %d out of %d...") % \
            (self.current_setup, self.num_total_setups)
