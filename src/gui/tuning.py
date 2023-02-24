"""The contents of the Tuning tab, where you can do brute force exhaustive simulation
on a variety of model parameters."""

from copy import copy
from logging import debug

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from .access_widgets import *

from ..agora import Agora
from ..demos import DEMO_FACTORIES, DEFAULT_DEMO_ARGUMENTS
from ..settings import SETTINGS


def _float_range(start, stop, step):
    """Interpolate between two values, like the standard range function.
    Attention: equality if allowed, so 'stop' is included in the range."""
    if start is None or stop is None or step == 0:
        yield None
        return
    up = start <= stop
    next_val = start
    while (next_val <= stop if up else next_val >= stop):
        yield next_val
        if up:
            next_val += step
        else:
            next_val -= step


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
        get_agora().load_demo_agora(demo_factory)
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


class LaunchTuningButton(Button):
    """The Button to start the repeated exhaustive simulation of the model parameters
    as defined by the TextInputs above."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
        self.bind(on_release=self.start_tuning)

    def start_tuning(self, *_):
        """Perform the exhaustive simulation and dump the results into a CSV file."""
        result_item = {
                        'egyik_bias' : None,
                        'masik_bias' : None,
                        'kezdo_tapasztalat' : None,
                        'belso_gyuru_sugara' : None,
                        SETTINGS.paradigm.para[0][0].form_a : 0,
                        SETTINGS.paradigm.para[0][0].form_b : 0,
                        'egyik_sem'                         : 0
                      }
        results = []

        # fetch the parameter ranges set by user in the Tuning menu
        tuning_menu = get_tuning_menu()
        try:
            our_bias_start = float(tuning_menu.ids.our_bias_start_input.text)
            our_bias_stop = float(tuning_menu.ids.our_bias_stop_input.text)
            our_bias_step = float(tuning_menu.ids.our_bias_step_input.text)
        except ValueError:
            # parameter not available
            our_bias_start = None
            our_bias_stop = None
            our_bias_step = None
        try:
            their_bias_start = float(tuning_menu.ids.their_bias_start_input.text)
            their_bias_stop = float(tuning_menu.ids.their_bias_stop_input.text)
            their_bias_step = float(tuning_menu.ids.their_bias_step_input.text)
        except ValueError:
            # parameter not available
            their_bias_start = None
            their_bias_stop = None
            their_bias_step = None
        try:
            starting_experience_start = int(tuning_menu.ids.starting_experience_start_input.text)
            starting_experience_stop = int(tuning_menu.ids.starting_experience_stop_input.text)
            starting_experience_step = int(tuning_menu.ids.starting_experience_step_input.text)
        except ValueError:
            # parameter not available
            starting_experience_start = None
            starting_experience_stop = None
            starting_experience_step = None
        try:
            inner_radius_start = float(tuning_menu.ids.inner_radius_start_input.text)
            inner_radius_stop = float(tuning_menu.ids.inner_radius_stop_input.text)
            inner_radius_step = float(tuning_menu.ids.inner_radius_step_input.text)
        except ValueError:
            # parameter not available
            inner_radius_start = None
            inner_radius_stop = None
            inner_radius_step = None
        repetitions = int(tuning_menu.ids.repetition_input.text)

        # man, that's a lot of setups
        num_total_setups = len(list(_float_range(our_bias_start, our_bias_stop, our_bias_step))) * \
                           len(list(_float_range(their_bias_start, their_bias_start, their_bias_start))) * \
                           len(list(_float_range(starting_experience_start, starting_experience_stop, starting_experience_step))) * \
                           len(list(_float_range(inner_radius_start, inner_radius_stop, inner_radius_step)))

        # now let's get to work
        agora = Agora()
        setup = 0
        for our_bias in _float_range(our_bias_start, our_bias_stop, our_bias_step):
            for their_bias in _float_range(their_bias_start, their_bias_stop, their_bias_step):
                for starting_experience in _float_range(starting_experience_start, starting_experience_stop, starting_experience_step):
                    print({our_bias, their_bias, starting_experience})
                    for inner_radius in _float_range(inner_radius_start, inner_radius_stop, inner_radius_step):
                        # initialize Agora according to current parameter setup
                        agora.load_demo_agora(DEMO_FACTORIES[SETTINGS.current_demo],
                                              our_bias,
                                              their_bias,
                                              starting_experience,
                                              inner_radius)
                        new_result = copy(result_item)
                        new_result['egyik_bias'] = our_bias
                        new_result['masik_bias'] = their_bias
                        new_result['kezdo_tapasztalat'] = starting_experience
                        new_result['belso_gyuru_sugara'] = inner_radius
                        print("new_result:",new_result)
                        setup += 1
                        print("Tuning: Running setup %d out of %d" % (setup, num_total_setups))
                        # perform 'repetition' number of simulations from the same starting state
                        for rep in range(0, repetitions):
                            agora.simulate_till_stable()
                            dominant_form = agora.dominant_form()
                            if dominant_form is None:
                                new_result['egyik_sem'] += 1
                            else:
                                new_result[dominant_form] += 1
                            agora.reset()
                        results.append(new_result)

        return
        # write the aggregated results to file
        with open('results.csv', 'w') as stream:
            for result in results:
                # create CSV manually for now
                stream.write(
                    str(r['r']) + ',' + str(r['exp']) + ',' + str(r['fotelnak']) + ',' + str(r['fotelnek']) + ',' + str(
                        r[None]) + "\n")
