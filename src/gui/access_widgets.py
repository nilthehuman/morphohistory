"""Convenience functions to make it easier for GUI code to navigate the Kivy Widget tree:
aliases for tediously long Widget and Layout lookups starting from the root Widget."""

from kivy.app import App
from kivy.uix.widget import Widget

from typing import Callable
from weakref import ReferenceType

def get_root() -> Widget:
    """Returns the root Widget."""
    return App.get_running_app().root

def get_agora_layout() -> ReferenceType[Widget]:
    """Returns the AgoraLayout on the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.agora_layout

def get_agora() -> ReferenceType[Widget]:
    """Returns the AgoraWidget on the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.agora

def get_button_layout() -> ReferenceType[Widget]:
    """Returns the Button panel on the right side of the main tab."""
    return App.get_running_app().root.ids.sim_layout.ids.button_layout

def get_settings() -> ReferenceType[Widget]:
    """Returns the scrollable Settings widget that takes up most of the Settings tab."""
    return App.get_running_app().root.ids.settings_layout.ids.settings

def get_single_cell_checkbox() -> ReferenceType[Widget]:
    """Returns the CheckBox at the top of the Paradigm tab."""
    return App.get_running_app().root.ids.para_layout.ids.single_cell_checkbox

def get_paradigm_table() -> ReferenceType[Widget]:
    """Returns the GridLayout that takes up most of the Paradigm tab."""
    return App.get_running_app().root.ids.para_layout.ids.para_table

def get_tuning_menu() -> ReferenceType[Widget]:
    """Returns the BoxLayout that takes up most of the Tuning tab."""
    return App.get_running_app().root.ids.tuning_layout.ids.tuning_menu

def forall_widgets(callback: Callable[[Widget], None], root: Widget) -> None:
    """Walk the entire subtree below and including the 'root' Widget
    and apply the callback to every Widget, tolerating failure."""
    # N.B.: Widget.walk() seems to be unreliable, and naive recursion results in
    # multiple calls to the same Widget due to id's being visible from higher up
    all_children = set()
    def collect_children(widget):
        children = set(list(widget.ids.values()) + widget.children)
        if hasattr(widget, 'tab_list'):
            children.update(widget.tab_list)
        all_children.update(children)
        for child in children:
            collect_children(child)
    # collect all widgets in the entire (sub)tree
    collect_children(root)
    # visit all widgets
    for child in all_children:
        try:
            callback(child)
        except AttributeError:
            pass  # that's fine
