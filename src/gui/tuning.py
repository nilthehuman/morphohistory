"""The contents of the Tuning tab, where you can do brute force exhaustive simulation
on a variety of model parameters."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from .access_widgets import get_root, get_agora

from ..demos import DEMO_FACTORIES
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

    def on_gui_ready(self):
        """Finish initializing: tell the Agora to load the first demo in the dropdown."""
        self.on_text()

    def on_text(self, *_):
        """Tell the Agora on the main tab to load the selected demo."""
        if not get_root():
            # Widget tree has not been built yet, leave job to on_size
            return
        selected = self.values.index(self.text) + 1
        demo_factory = DEMO_FACTORIES[selected]
        get_agora().load_demo_agora(demo_factory)
