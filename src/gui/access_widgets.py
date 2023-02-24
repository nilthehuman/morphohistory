"""Convenience functions to make it easier for GUI code to navigate the Kivy Widget tree:
aliases for tediously long Widget and Layout lookups starting from the root Widget."""

from kivy.app import App

def get_root():
    """Returns the root Widget."""
    return App.get_running_app().root

def get_agora_layout():
    """Returns the AgoraLayout on the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.agora_layout

def get_agora():
    """Returns the AgoraWidget on the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.agora

def get_button_layout():
    """Returns the Button panel on the right side of the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.button_layout

def get_settings():
    """Returns the scrollable Settings widget that takes up most of the Settings tab."""
    return App.get_running_app().root.ids.settings_layout.ids.settings

def get_single_cell_checkbox():
    """Returns the CheckBox at the top of the Paradigm tab."""
    return App.get_running_app().root.ids.para_layout.ids.single_cell_checkbox

def get_paradigm_table():
    """Returns the GridLayout that takes up most of the Paradigm tab."""
    return App.get_running_app().root.ids.para_layout.ids.para_table

def get_tuning_menu():
    """Returns the BoxLayout that takes up most of the Tuning tab."""
    return App.get_running_app().root.ids.tuning_layout.ids.tuning_menu
