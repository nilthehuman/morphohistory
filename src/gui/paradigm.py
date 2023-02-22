"""The contents of the Paradigm tab: a complete noun paradigm with two different forms in each cell."""


from platform import system
if system() == "Windows":
    from kivy.config import Config
    Config.set('kivy', 'keyboard_mode', 'systemandmulti')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from .confirm import ApplyConfirmedLabel, DiscardConfirmedLabel

from ..settings import SETTINGS

def _get_agora():
    return App.get_running_app().root.ids.sim_layout.ids.agora

def _get_single_cell_checkbox():
    return App.get_running_app().root.ids.para_layout.ids.single_cell_checkbox

def _get_paradigm_table():
    return App.get_running_app().root.ids.para_layout.ids.para_table

class ParadigmTabLayout(BoxLayout):
    """The vertical BoxLayout holding the "single cell" CheckBox, the paradigm table
    and the two Buttons at the bottom."""
    pass

class CaseLabel(Label):
    """A simple label to help the user identify which row corresponds to which noun case."""

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self._text = text

    # Initiasize anti-pattern
    def on_size(self, *_):
        """Finish initializing once the root widget is ready."""
        self.toggle_text()
        _get_single_cell_checkbox().bind(active=self.toggle_text)
        self.unbind(size=self.on_size)

    def toggle_text(self, *_):
        """Show or hide our own text depending on the state of the CheckBox above."""
        self.text = '' if _get_single_cell_checkbox().active else self._text

class CellTextInput(TextInput):
    """A text input box for one form of a cell in the paradigm table."""

    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.multiline = False # FIXME: this does not work :/
        self.cursor_color = (0, 0, 0, 1)

    # Initiasize anti-pattern
    def on_size(self, *_):
        """Finish initializing once the root widget is ready."""
        self.toggle_disabled()
        _get_single_cell_checkbox().bind(active=self.toggle_disabled)
        self.unbind(size=self.on_size)

    def toggle_disabled(self, *_):
        """Show or hide our own text depending on the state of the CheckBox above."""
        self.disabled = _get_single_cell_checkbox().active

class ParadigmTable(GridLayout):
    """A 14 row (header + 13 cases) by 7 column (label col + 2 x (form A, form B, prominence)) table
    for the noun paradigm to be used in the simulation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        case_names = ["", "ACC", "DAT", "INS", "TRANS", "INE", "SUPE", "ADE",
                      "ILL", "SUBL", "ALL", "ELA", "DEL", "ABL"]
        for row in range(0, 14):
            case_label = CaseLabel(text=case_names[row], size_hint_x=0.1)
            self.add_widget(case_label)

        header_label = Label(text="SING (A alak)", size_hint_x=0.175)
        self.add_widget(header_label)
        first_textinput = TextInput(size_hint_x=0.175, cursor_color=(0, 0, 0, 1))
        self.add_widget(first_textinput)
        for row in range(2, 14):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="SING (B alak)", size_hint_x=0.175)
        self.add_widget(header_label)
        first_textinput = TextInput(size_hint_x=0.175, cursor_color=(0, 0, 0, 1))
        self.add_widget(first_textinput)
        for row in range(2, 14):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="prominencia", size_hint_x=0.1)
        self.add_widget(header_label)
        first_textinput = TextInput(size_hint_x=0.1, text='1', cursor_color=(0, 0, 0, 1))
        self.add_widget(first_textinput)
        for row in range(2, 14):
            text_input = CellTextInput(size_hint_x=0.1, text='1')
            self.add_widget(text_input)

        header_label = Label(text="PLUR (A alak)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 14):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="PLUR (B alak)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 14):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="prominencia", size_hint_x=0.1)
        self.add_widget(header_label)
        for row in range(1, 14):
            text_input = CellTextInput(size_hint_x=0.1, text='1')
            self.add_widget(text_input)

    # Initiasize anti-pattern
    def on_size(self, *_):
        """Finish initializing once the root widget is ready."""
        self.save_or_load_cells()
        self.unbind(size=self.on_size)

    def save_or_load_cells(self, save=False):
        """Write the contents of all cells to speaker's paradigms, or reload cells from them."""
        def _process_subcell(num, case, subcell):
            # N.B. children are stored in reverse order
            child_number = 14 * 7 - ((1 + 3*num + subcell) * 14 + 2 + case) # why do I need to add 2 here instead of 1??
            text_input = self.children[child_number]
            if 0 == subcell:
                if save:
                    SETTINGS.paradigm.para[num][case].form_a = text_input.text
                else:
                    text_input.text = SETTINGS.paradigm.para[num][case].form_a
            elif 1 == subcell:
                if save:
                    SETTINGS.paradigm.para[num][case].form_b = text_input.text
                else:
                    text_input.text = SETTINGS.paradigm.para[num][case].form_b
            elif 2 == subcell:
                try:
                    if save:
                        SETTINGS.paradigm.para[num][case].prominence = float(text_input.text)
                    else:
                        text_input.text = str(SETTINGS.paradigm.para[num][case].prominence)
                except ValueError:
                    pass
        if _get_single_cell_checkbox().active:
            for subcell in range(0, 3):
                _process_subcell(0, 0, subcell)
        else:
            for num in range(0, 2):
                for case in range(0, 13):
                    for subcell in range(0, 3):
                        _process_subcell(num, case, subcell)
        _get_agora().set_paradigm(SETTINGS.paradigm)

class ApplyParadigmButton(Button):
    """Button to replace all word forms in the current simulation with the ones set on this tab."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.apply_paradigm)

    def apply_paradigm(self, *_):
        """Update all word forms in the simulated paradigm to the user's new inputs."""
        _get_paradigm_table().save_or_load_cells(save=True)
        label = ApplyConfirmedLabel()
        self.parent.add_widget(label)

class DiscardParadigmButton(Button):
    """Button to reset all word forms in this tab to the ones in the current simulation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.discard_paradigm)

    def discard_paradigm(self, *_):
        """Reset all word forms in the paradigm table to their previous values."""
        _get_paradigm_table().save_or_load_cells(save=False)
        label = DiscardConfirmedLabel()
        self.parent.add_widget(label)
