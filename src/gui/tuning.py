"""The contents of the Tuning tab, where you can do brute force exhaustive simulation
on a variety of model parameters."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from .access_widgets import *

from ..demos import DEMO_FACTORIES, DEFAULT_DEMO_ARGUMENTS
from ..settings import SETTINGS


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
    pass
