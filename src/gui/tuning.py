"""The contents of the Tuning tab, where you can do brute force exhaustive simulation
on a variety of model parameters."""

from copy import copy
from logging import info
from os.path import isfile
from time import gmtime, strftime, perf_counter

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from .access_widgets import *

from ..agora import Agora
from ..demos import DEMO_FACTORIES, DEFAULT_DEMO_ARGUMENTS
from ..settings import SETTINGS


def _float_range(start, stop, step):
    """Interpolate between two values, like the standard range function.
    Attention: equality if allowed, so 'stop' is included in the range."""
    if start is None or stop is None:
        yield None
        return
    if step == 0:
        yield start
        return
    up = start <= stop
    next_val = start
    while (next_val <= stop if up else next_val >= stop):
        yield next_val
        if up:
            next_val += step
        else:
            next_val -= step

def _normalize_hungarian(string):
    accentless = {
                   'Á':'AA', 'á':'aa',
                   'É':'EE', 'é':'ee',
                   'Í':'II', 'í':'ii',
                   'Ó':'OO', 'ó':'oo',
                   'Ö':'OE', 'ö':'oe',
                   'Ő':'OE', 'ő':'oe',
                   'Ú':'UU', 'ú':'uu',
                   'Ü':'UE', 'ü':'ue',
                   'Ű':'UE', 'ű':'ue'
                 }
    def convert(char):
        try:
            return accentless[char]
        except KeyError:
            return char
    return ''.join(map(convert, string))


class TuningTabLayout(BoxLayout):
    """The vertical BoxLayout holding the demo selector Spinner, a few TextInputs to define
    parameter intervals and step, and a Button to launch the parametrized simulation."""
    pass


class DemoSpinner(Spinner):
    """The Spinner Widget used to select the parametrizable demo agora the user wants to use."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = [str(factory_name) for factory_name in DEMO_FACTORIES.keys()]
        self.values = [factory_name[factory_name.index('.')+1:] for factory_name in self.values]
        # FIXME: revert or clean this up after NYTUD talk
        self.values = ['Szivárvány 9x9',
                       'Szivárvány 10x10',
                       'Egyensúly',
                       'Egyensúly (óriás)',
                       'Sakktábla',
                       'Egyedül',
                       'Kisebbség vs nagyobbság 9x9',
                       'Kisebbség vs nagyobbság 10x10',
                       'Mizantróp filmcsillag',
                       'Gyűrűk 16+16',
                       'Gyűrűk 16+24',
                       'Falvak']

    def on_gui_ready(self):
        """Finish initializing: tell the Agora to load the first demo in the dropdown."""
        self.on_text()

    def on_text(self, *_):
        """Tell the Agora on the main tab to load the selected demo."""
        if not get_root():
            # Widget tree has not been built yet, leave job to on_gui_ready
            return
        selected = self.values.index(self.text) + 1
        SETTINGS.current_demo = selected
        demo_factory = DEMO_FACTORIES[selected]
        get_agora().load_demo_agora(demo_factory, starting_experience=SETTINGS.starting_experience)
        # update suggested default parametrization values
        tuning_menu = get_tuning_menu()
        if DEFAULT_DEMO_ARGUMENTS[selected].our_bias is not None:
            tuning_menu.ids.our_bias_start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].our_bias)
            tuning_menu.ids.our_bias_stop_input.text = str(abs(1 - DEFAULT_DEMO_ARGUMENTS[selected].our_bias))
            tuning_menu.ids.our_bias_step_input.text = '0.1'
        else:
            tuning_menu.ids.our_bias_start_input.text = 'N/A'
            tuning_menu.ids.our_bias_stop_input.text = 'N/A'
            tuning_menu.ids.our_bias_step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].their_bias is not None:
            tuning_menu.ids.their_bias_start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].their_bias)
            tuning_menu.ids.their_bias_stop_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].their_bias)
            tuning_menu.ids.their_bias_step_input.text = '0.1'
        else:
            tuning_menu.ids.their_bias_start_input.text = 'N/A'
            tuning_menu.ids.their_bias_stop_input.text = 'N/A'
            tuning_menu.ids.their_bias_step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].starting_experience is not None:
            tuning_menu.ids.starting_experience_start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].starting_experience)
            tuning_menu.ids.starting_experience_stop_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].starting_experience)
            tuning_menu.ids.starting_experience_step_input.text = '10'
        else:
            tuning_menu.ids.starting_experience_start_input.text = 'N/A'
            tuning_menu.ids.starting_experience_stop_input.text = 'N/A'
            tuning_menu.ids.starting_experience_step_input.text = 'N/A'
        if DEFAULT_DEMO_ARGUMENTS[selected].inner_radius is not None:
            tuning_menu.ids.inner_radius_start_input.text = str(DEFAULT_DEMO_ARGUMENTS[selected].inner_radius)
            tuning_menu.ids.inner_radius_stop_input.text = '0.9'
            tuning_menu.ids.inner_radius_step_input.text = '0.125'
        else:
            tuning_menu.ids.inner_radius_start_input.text = 'N/A'
            tuning_menu.ids.inner_radius_stop_input.text = 'N/A'
            tuning_menu.ids.inner_radius_step_input.text = 'N/A'


class TuningProgressPopup(BoxLayout):
    """A popup window to show the progress of the tuning."""
    cancel = ObjectProperty(None)


class LaunchTuningButton(Button):
    """The Button to start the repeated exhaustive simulation of the model parameters
    as defined by the TextInputs above."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tuner = None
        self.popup = None
        self.bind(on_release=self.start_tuning)

    def start_tuning(self, *_):
        """Start the exhaustive simulation."""
        content = TuningProgressPopup(cancel=self.cancel_tuning)
        self.popup = Popup(title="Kis türelmet, ez eltarthat ám egy darabig...", content=content,
                           size_hint=(None, None), size=SETTINGS.popup_size_progress)
        self.popup.open()
        self.tuner = Tuner()
        self.tuner.run()

    def cancel_tuning(self, *_):
        """Stop the simulation midway through."""
        self.tuner.tuning_cancelled = True
        self.popup.dismiss()


# TODO: yeah I mean this class could use a bit of a cleanup...
class Tuner:
    """The class that's actually responsible for performing the parametrized simulations
    and writing the results to file."""

    result_item = {
        'egyik_bias' : None,
        'masik_bias' : None,
        'kezdo_tapasztalat' : None,
        'belso_gyuru_sugara' : None,
        SETTINGS.paradigm.para[0][0].form_a : 0,
        SETTINGS.paradigm.para[0][0].form_b : 0,
        'egyik_sem' : 0
    }

    # why doesn't Python have macros?
    def loop_our_bias(self):
        return _float_range(self.our_bias_start, self.our_bias_stop, self.our_bias_step)

    def loop_their_bias(self):
        return _float_range(self.their_bias_start, self.their_bias_stop, self.their_bias_step)

    def loop_starting_experience(self):
        return _float_range(self.starting_experience_start, self.starting_experience_stop, self.starting_experience_step)

    def loop_inner_radius(self):
        return _float_range(self.inner_radius_start, self.inner_radius_stop, self.inner_radius_step)

    def __init__(self):
        """Fetch the parameter ranges defined by user in the Tuning menu
        and prepare for actually performing the simulations."""
        tuning_menu = get_tuning_menu()
        # macros?... :(
        try:
            self.our_bias_start = float(tuning_menu.ids.our_bias_start_input.text)
            self.our_bias_stop = float(tuning_menu.ids.our_bias_stop_input.text)
            self.our_bias_step = float(tuning_menu.ids.our_bias_step_input.text)
        except ValueError:
            # parameter not available
            self.our_bias_start = None
            self.our_bias_stop = None
            self.our_bias_step = None
        try:
            self.their_bias_start = float(tuning_menu.ids.their_bias_start_input.text)
            self.their_bias_stop = float(tuning_menu.ids.their_bias_stop_input.text)
            self.their_bias_step = float(tuning_menu.ids.their_bias_step_input.text)
        except ValueError:
            # parameter not available
            self.their_bias_start = None
            self.their_bias_stop = None
            self.their_bias_step = None
        try:
            self.starting_experience_start = int(tuning_menu.ids.starting_experience_start_input.text)
            self.starting_experience_stop = int(tuning_menu.ids.starting_experience_stop_input.text)
            self.starting_experience_step = int(tuning_menu.ids.starting_experience_step_input.text)
        except ValueError:
            # parameter not available
            self.starting_experience_start = None
            self.starting_experience_stop = None
            self.starting_experience_step = None
        try:
            self.inner_radius_start = float(tuning_menu.ids.inner_radius_start_input.text)
            self.inner_radius_stop = float(tuning_menu.ids.inner_radius_stop_input.text)
            self.inner_radius_step = float(tuning_menu.ids.inner_radius_step_input.text)
        except ValueError:
            # parameter not available
            self.inner_radius_start = None
            self.inner_radius_stop = None
            self.inner_radius_step = None
        self.repetitions = int(tuning_menu.ids.repetition_input.text)

        # man, that's a lot of setups
        self.num_total_setups = len(list(self.loop_our_bias())) * \
                                len(list(self.loop_their_bias())) * \
                                len(list(self.loop_starting_experience())) * \
                                len(list(self.loop_inner_radius()))
        popup = get_tuning_menu().ids.launch_tuning_button.popup
        popup.ids.container.children[0].ids.progressbar.max = self.num_total_setups * self.repetitions

        # state to keep track of simulation parameters and results
        self.agora = Agora()
        self.results = []
        self.current_setup = 0
        self.current_rep = 0
        self.num_total_reps = 0
        self.tuning_cancelled = False
        self.our_bias_range = self.loop_our_bias()
        self.their_bias_range = self.loop_their_bias()
        self.starting_experience_range = self.loop_starting_experience()
        self.inner_radius_range = self.loop_inner_radius()
        self.our_bias = next(self.our_bias_range)
        self.their_bias = next(self.their_bias_range)
        self.starting_experience = next(self.starting_experience_range)
        self.inner_radius = next(self.inner_radius_range)
        self.prepare_next_setup()

        # create the CSV file, write the header line, and we're good to go
        self.output_filename = 'results.csv'
        self.initialize_csv_file()

    def run(self):
        """Schedule our own method driving the tuning in the Kivy event loop."""
        info("Tuning: Exhaustive simulation started at %s" % strftime("%H:%M:%S", gmtime()))
        self.start_time = perf_counter()
        self.tuning_event = Clock.schedule_interval(self.iterate_tuning, 0.0)

    def iterate_tuning(self, *_):
        """Repeat the simulation several times for each parameter setup in the set of
        parameter combinations chosen by the user, then dump the results in a CSV file."""
        if self.tuning_cancelled:
            # unschedule ourselves from Kivy event loop
            self.tuning_event.cancel()
            get_tuning_menu().ids.launch_tuning_button.popup.dismiss()
            return

        # poor man's nested for loop, continued from previous call...
        # this is pretty horrifying actually, maybe we could try continuation-passing style?
        if self.current_rep == self.repetitions:
            self.current_rep = 0
            # export results to file incrementally
            self.write_new_row_to_csv_file()
            try:
                self.inner_radius = next(self.inner_radius_range)
            except StopIteration:
                self.inner_radius_range = self.loop_inner_radius()
                self.inner_radius = next(self.inner_radius_range)
                try:
                    self.starting_experience = next(self.starting_experience_range)
                except StopIteration:
                    self.starting_experience_range = self.loop_starting_experience()
                    self.starting_experience = next(self.starting_experience_range)
                    try:
                        self.their_bias = next(self.their_bias_range)
                    except StopIteration:
                        self.their_bias_range = self.loop_their_bias()
                        self.their_bias = next(self.their_bias_range)
                        try:
                            self.our_bias = next(self.our_bias_range)
                        except StopIteration:
                            # we're done, stop iterating
                            self.tuning_event.cancel()
                            get_tuning_menu().ids.launch_tuning_button.popup.dismiss()
                            end_time = perf_counter()
                            info("Tuning: Exhaustive simulation finished at %s, took %s" % \
                                (strftime("%H:%M:%S", gmtime()),
                                 strftime("%H:%M:%S", gmtime(end_time - self.start_time))))
                            return
            self.prepare_next_setup()
        self.perform_next_rep()
        # update progress bar
        popup = get_tuning_menu().ids.launch_tuning_button.popup
        popup.ids.container.children[0].ids.progressbar.value = self.num_total_reps

    def prepare_next_setup(self):
        """Initialize Agora according to next parameter setup."""
        self.agora.load_demo_agora(DEMO_FACTORIES[SETTINGS.current_demo],
                                   self.our_bias,
                                   self.their_bias,
                                   self.starting_experience,
                                   self.inner_radius)
        self.new_result = copy(self.result_item)
        self.new_result['egyik_bias'] = self.our_bias
        self.new_result['masik_bias'] = self.their_bias
        self.new_result['kezdo_tapasztalat'] = self.starting_experience
        self.new_result['belso_gyuru_sugara'] = self.inner_radius
        self.current_setup += 1
        info("Tuning: Running setup %d out of %d..." % (self.current_setup, self.num_total_setups))
        popup = get_tuning_menu().ids.launch_tuning_button.popup
        popup.ids.container.children[0].ids.progress_label.text = "Ez a(z) %d. beállítás %d közül..." % \
            (self.current_setup, self.num_total_setups)

    def perform_next_rep(self):
        """Perform a single simulation run for the current parameter setup."""
        self.agora.simulate_till_stable()
        dominant_form = self.agora.dominant_form()
        if dominant_form is None:
            self.new_result['egyik_sem'] += 1
        else:
            self.new_result[dominant_form] += 1
        self.agora.quick_reset()
        self.current_rep += 1
        self.num_total_reps += 1

    def initialize_csv_file(self):
        """Create output CSV file and write the first row with the column names."""
        append_num = 0
        try:
            filename_until_dot = self.output_filename[:self.output_filename.index('.csv')]
        except ValueError:
            filename_until_dot = self.output_filename
        while isfile(self.output_filename):
            self.output_filename = filename_until_dot + str(append_num) + '.csv'
            append_num += 1
        with open(self.output_filename, 'w', encoding='utf-8') as filehandle:
            keys_normalized = [_normalize_hungarian(key) for key in self.result_item.keys()]
            csv_header = ','.join(keys_normalized)
            filehandle.write(csv_header)

    def write_new_row_to_csv_file(self):
        """Output next row of simulation results to target CSV file."""
        with open(self.output_filename, 'a', encoding='utf-8') as stream:
            # create CSV manually for now
            stream.write("\n")
            csv_row = ','.join([str(value) for value in self.new_result.values()])
            stream.write(csv_row)
