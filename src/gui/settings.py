"""The contents of the Settings tab: a list of user options to control the simulation parameters."""

from math import inf

from kivy.config import ConfigParser
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import Settings, InterfaceWithNoMenu

from ..settings import SETTINGS

Settings.interface_cls = InterfaceWithNoMenu

_SETTINGS_JSON = '''
[
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
        "key": "sim_influence_mutual"
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
'''

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
        self.add_json_panel('Beállítások', self.config, data=_SETTINGS_JSON)

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
