"""The contents of the Paradigm tab: a complete noun paradigm with two different forms in each cell."""

from logging import error

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from .access_widgets import get_agora, get_single_cell_checkbox, get_paradigm_table
from .confirm import ApplyConfirmedLabel, DiscardConfirmedLabel
from .l10n import localize

from ..settings import SETTINGS

class ParadigmTabLayout(BoxLayout):
    """The vertical BoxLayout holding the "single cell" CheckBox, the paradigm table
    and the two Buttons at the bottom."""
    pass

class CaseLabel(Label):
    """A simple label to help the user identify which row corresponds to which noun case."""

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._text = text

    def on_gui_ready(self) -> None:
        """Finish initializing once the root widget is ready."""
        self.toggle_text()
        get_single_cell_checkbox().bind(active=self.toggle_text)

    def toggle_text(self, *_) -> None:
        """Show or hide our own text depending on the state of the CheckBox above."""
        self.text = '' if get_single_cell_checkbox().active else self._text

class CellTextInput(TextInput):
    """A text input box for one form of a cell in the paradigm table."""

    def __init__(self, always_enabled: bool=False, text: str='', **kwargs) -> None:
        super().__init__(**kwargs)
        self.always_enabled = always_enabled
        self.text = text
        self.font_size = 14
        self.multiline = False
        self.cursor_color = (0, 0, 0, 1)

    def on_gui_ready(self) -> None:
        """Finish initializing once the root widget is ready."""
        if not self.always_enabled:
            self.toggle_disabled()
            get_single_cell_checkbox().bind(active=self.toggle_disabled)

    def toggle_disabled(self, *_) -> None:
        """Show or hide our own text depending on the state of the CheckBox above."""
        self.disabled = get_single_cell_checkbox().active

class ParadigmTable(GridLayout):
    """A 15 row (header + 14 cases) by 7 column (label col + 2 x (form A, form B, prominence)) table
    for the noun paradigm to be used in the simulation."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        case_names = ["", "NOM", "ACC", "DAT", "INS", "TRANS", "INE", "SUPE", "ADE",
                      "ILL", "SUBL", "ALL", "ELA", "DEL", "ABL"]
        for row in range(0, 15):
            case_label = CaseLabel(text=case_names[row], size_hint_x=0.1)
            self.add_widget(case_label)

        header_label = Label(text="SING (form A)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 15):
            if row == 1:
                text_input = CellTextInput(always_enabled=True, size_hint_x=0.175)
            else:
                text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="SING (form B)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 15):
            if row == 1:
                text_input = CellTextInput(always_enabled=True, size_hint_x=0.175)
            else:
                text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="prominence", size_hint_x=0.1)
        self.add_widget(header_label)
        for row in range(1, 15):
            text_input = CellTextInput(size_hint_x=0.1, text='1')
            self.add_widget(text_input)

        header_label = Label(text="PLUR (form A)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 15):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="PLUR (form B)", size_hint_x=0.175)
        self.add_widget(header_label)
        for row in range(1, 15):
            text_input = CellTextInput(size_hint_x=0.175)
            self.add_widget(text_input)

        header_label = Label(text="prominence", size_hint_x=0.1)
        self.add_widget(header_label)
        for row in range(1, 15):
            text_input = CellTextInput(size_hint_x=0.1, text='1')
            self.add_widget(text_input)

    def on_gui_ready(self) -> None:
        """Finish initializing once the root widget is ready."""
        self.save_or_load_cells()
        get_single_cell_checkbox().bind(active=self.toggle_single_cell_setting)

    def toggle_single_cell_setting(self, *_) -> None:
        """Update the single cell vs whole paradigm switch in the global SETTINGS object."""
        SETTINGS.sim_single_cell = get_single_cell_checkbox().active

    def save_or_load_cells(self, save: bool=False) -> None:
        """Write the contents of all cells to speaker's paradigms, or reload cells from them."""
        def get_text_input_index(num, case, subcell):
            return 15 * 7 - ((1 + 3*num + subcell) * 15 + 2 + case) # why do I need to add 2 here instead of 1??
        if save:
            sum_prominence = 0
            for num in range(0, 2):
                for case in range(0, 14):
                    form_a_index = get_text_input_index(num, case, 0)
                    form_a_text_input = self.children[form_a_index]
                    form_b_index = get_text_input_index(num, case, 1)
                    form_b_text_input = self.children[form_b_index]
                    if not form_a_text_input.disabled and form_a_text_input.text != form_b_text_input.text:
                        prominence_index = get_text_input_index(num, case, 2)
                        prominence_text_input = self.children[prominence_index]
                        sum_prominence += float(prominence_text_input.text)
            if 0 == sum_prominence:
                raise ZeroDivisionError
        def _process_subcell(num, case, subcell):
            # N.B. children are stored in reverse order
            child_index = get_text_input_index(num, case, subcell)
            text_input = self.children[child_index]
            if not save:
                was_disabled = text_input.disabled
                text_input.disabled = False
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
            if not save:
                text_input.disabled = was_disabled
        for num in range(0, 2):
            for case in range(0, 14):
                for subcell in range(0, 3):
                    _process_subcell(num, case, subcell)
        get_agora().set_paradigm(SETTINGS.paradigm)

class ApplyParadigmButton(Button):
    """Button to replace all word forms in the current simulation with the ones set on this tab."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bind(on_release=self.apply_paradigm)

    def apply_paradigm(self, *_) -> None:
        """Update all word forms in the simulated paradigm to the user's new inputs."""
        try:
            get_paradigm_table().save_or_load_cells(save=True)
            label = ApplyConfirmedLabel()
            self.parent.add_widget(label)
        except ZeroDivisionError:
            error("Cells with non-identical forms have zero total prominence.")
            label = DiscardConfirmedLabel()
            label.text = localize("Zero total prominence.")
            self.parent.add_widget(label)

class DiscardParadigmButton(Button):
    """Button to reset all word forms in this tab to the ones in the current simulation."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bind(on_release=self.discard_paradigm)

    def discard_paradigm(self, *_) -> None:
        """Reset all word forms in the paradigm table to their previous values."""
        get_paradigm_table().save_or_load_cells(save=False)
        label = DiscardConfirmedLabel()
        self.parent.add_widget(label)
