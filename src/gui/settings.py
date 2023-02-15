"""The contents of the Settings tab: a list of user options to control the simulation parameters."""

from json import dumps
from math import inf

from kivy.app import App
from kivy.config import ConfigParser
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.settings import InterfaceWithNoMenu, Settings, SettingItem
from kivy.utils import get_color_from_hex, get_hex_from_color

from ..settings import SETTINGS

Settings.interface_cls = InterfaceWithNoMenu

_SETTINGS_UI = [
    {
        "type": "title",
        "title": "Megjelenés"
    },
    {
        "type": "color",
        "title": "A szín",
        "desc": "Az első alternánst jelölő szín",
        "section": "Appearance",
        "key": "color_a"
    },
    {
        "type": "color",
        "title": "B szín",
        "desc": "A második alternánst jelölő szín",
        "section": "Appearance",
        "key": "color_b"
    },
    {
        "type": "color",
        "title": "Broadcaster színe",
        "desc": "A mindenkihez szóló beszélők színe",
        "section": "Appearance",
        "key": "color_broadcaster"
    },
    {
        "type": "bool",
        "title": "Közlés mutatása",
        "desc": "Jelezze-e nyíl az egyes interakciókat",
        "section": "Appearance",
        "key": "draw_arrow"
    },
    {
        "type": "title",
        "title": "Szimuláció"
    },
    {
        "type": "options",
        "title": "Távolságmérték",
        "desc": "Hogyan számítson a geometria",
        "section": "Simulation",
        "key": "sim_distance_metric",
        "options": ["konstans", "Manhattan", "euklideszi"]
    },
    {
        "type": "bool",
        "title": "Önbefolyásolás",
        "desc": "Hasson-e magára a beszélő",
        "section": "Simulation",
        "key": "sim_influence_self"
    },
    {
        "type": "bool",
        "title": "Kölcsönös befolyásolás",
        "desc": "Hasson-e egymásra mindkét fél",
        "section": "Simulation",
        "key": "sim_influence_mutual"
    },
    {
        "type": "bool",
        "title": "Fordított hatás",
        "desc": "A hallott alak ellenkezőjét preferáljuk-e",
        "section": "Simulation",
        "key": "sim_prefer_opposite"
    },
    {
        "type": "numeric",
        "title": "Kezdeti tapasztalat",
        "desc": "Hány előzetes interakciót tételezzünk fel a beszélőkről",
        "section": "Simulation",
        "key": "starting_experience"
    },
    {
        "type": "title",
        "title": "Holtpont"
    },
    {
        "type": "numeric",
        "title": "Elfogultsági küszöb",
        "desc": "Mekkora biast várunk el minden beszélőtől, mielőtt leáll a szimuláció",
        "section": "Termination",
        "key": "bias_threshold"
    },
    {
        "type": "numeric",
        "title": "Tapasztalati küszöb",
        "desc": "Hány hallott alakot várunk el minden beszélőtől, mielőtt leáll a szimuláció",
        "section": "Termination",
        "key": "experience_threshold"
    },
    {
        "type": "numeric",
        "title": "Iterációs limit",
        "desc": "Hány interakciót engedünk meg legfeljebb",
        "section": "Termination",
        "key": "sim_max_iteration"
    }
]

class SettingsLayout(BoxLayout):
    """The vertical BoxLayout for the CustomSettingsPanel and the Buttons at the bottom."""
    pass

class CustomSettings(Settings):
    """A list of user preferences to control the appearance and operation of the application."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = ConfigParser()
        self.config.setdefaults('Appearance',
                                {
                                    'color_a': '#ffff00',
                                    'color_b': '#ff00ff',
                                    'color_broadcaster': '#00ff00',
                                    'draw_arrow': 1
                                })
        self.config.setdefaults('Simulation',
                                {
                                    'sim_distance_metric': 'konstans',
                                    'sim_influence_self': 0,
                                    'sim_influence_mutual': 0,
                                    'sim_prefer_opposite': 0,
                                    'starting_experience': 1
                                })
        self.config.setdefaults('Termination',
                                {
                                    'bias_threshold': 0.8,
                                    'experience_threshold': 10,
                                    'sim_max_iteration': 10000
                                })
        self.add_json_panel('Beállítások', self.config, data=dumps(_SETTINGS_UI))

    def on_config_change(self, config, section, key, value):
        # enforce upper and lower bounds on user-supplied values
        bounds = {
            ('Simulation', 'starting_experience') : (0, inf),
            ('Termination', 'bias_threshold') : (0, 1),
            ('Termination', 'experience_threshold') : (0, inf),
            ('Termination', 'sim_max_iteration') : (100, inf)
        }
        if (section, key) in bounds:
            clamped_value = float(value)
            clamped_value = max(clamped_value, bounds[(section, key)][0])
            clamped_value = min(clamped_value, bounds[(section, key)][1])
            self.config.set(section, key, clamped_value)
            # TODO: refresh the SettingsPanel as well
        super().on_config_change(config, section, key, value)

    def reload_config_values(self):
        """Refresh all values displayed in the SettingsPanel."""
        settingspanel = self.interface.children[0].children[0]
        subtree = settingspanel.children
        for child in subtree:
            if isinstance(child, SettingItem):
                child.value = self.config.get(child.section, child.key)

def _get_agora():
    return App.get_running_app().root.ids.sim_layout.ids.agora

def _get_settings():
    return App.get_running_app().root.ids.settings_layout.ids.settings

def _get_config():
    return _get_settings().config

class ApplySettingsButton(Button):
    """Button to destructively set the user's choices in the global settings object."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.apply_settings)

    def apply_settings(self, *_):
        """Overwrite current application settings with those in the SettingsPanel."""
        update_colors = False
        update_grid = False
        for section in _get_config().sections():
            for (key, new_value) in _get_config().items(section):
                # parse new_value from its raw string state
                value_type = [item['type'] for item in _SETTINGS_UI if 'key' in item and key == item['key']][0]
                if 'bool' == value_type:
                    new_value = '0' != new_value
                elif 'color' == value_type:
                    new_value = Color(*get_color_from_hex(new_value))
                    if new_value.rgb != getattr(SETTINGS, key).rgb:
                        update_colors = True
                elif 'numeric' == value_type:
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        new_value = float(new_value)
                elif 'options' == value_type:
                    string_to_enum = {
                        'konstans'   : SETTINGS.DistanceMetric.CONSTANT,
                        'Manhattan'  : SETTINGS.DistanceMetric.MANHATTAN,
                        'euklideszi' : SETTINGS.DistanceMetric.EUCLIDEAN
                    }
                    new_value = string_to_enum[new_value]
                    update_grid = True
                elif 'string' == value_type:
                    pass
                else:
                    assert False
                setattr(SETTINGS, key, new_value)
        if update_colors:
            _get_agora().update_speakerdot_colors()
        if update_grid:
            _get_agora().update_grid()

class DiscardSettingsButton(Button):
    """Button to throw away all changes and restore previous settings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.discard_settings)

    def discard_settings(self, *_):
        """Reset all items in SettingsPanel to the previous application settings."""
        for section in _get_config().sections():
            for (key, _) in _get_config().items(section):
                old_value = getattr(SETTINGS, key)
                if isinstance(old_value, Color):
                    old_value = get_hex_from_color(old_value.rgb)
                elif isinstance(old_value, SETTINGS.DistanceMetric):
                    enum_to_string = {
                        SETTINGS.DistanceMetric.CONSTANT  : 'konstans',
                        SETTINGS.DistanceMetric.MANHATTAN : 'Manhattan',
                        SETTINGS.DistanceMetric.EUCLIDEAN : 'euklideszi',
                    }
                    old_value = enum_to_string[old_value]
                _get_config().set(section, key, old_value)
        # force the update of displayed values on GUI as well
        _get_settings().reload_config_values()
