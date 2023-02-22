"""The contents of the Settings tab: a list of user options to control the simulation parameters."""

from copy import copy
from math import inf

from kivy.app import App
from kivy.config import ConfigParser
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.settings import InterfaceWithNoMenu, Settings, SettingItem, SettingsPanel
from kivy.utils import get_color_from_hex, get_hex_from_color

from .confirm import ApplyConfirmedLabel, DiscardConfirmedLabel

from ..settings import SETTINGS

Settings.interface_cls = InterfaceWithNoMenu

_SETTINGS_FILE_PATH = 'user_settings.ini'

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
        "type": "string",
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

def _get_agora():
    return App.get_running_app().root.ids.sim_layout.ids.agora

def _get_settings():
    return App.get_running_app().root.ids.settings_layout.ids.settings

class SettingsTabLayout(BoxLayout):
    """The vertical BoxLayout for the CustomSettingsPanel and the Buttons at the bottom."""
    pass

class CustomSettingsPanel(SettingsPanel):
    """Base class overridden to keep it from saving to file every time a setting is changed."""
    def set_value(self, section, key, value):
        """Override base class method to keep it from saving to file
        every time a setting is changed."""
        current = self.get_value(section, key)
        if current == value:
            return
        self.config.set(section, key, value)
        #self.config.write() # don't write to file just yet

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
                                    'sim_influence_self': 1,
                                    'sim_influence_mutual': 0,
                                    'sim_prefer_opposite': 0,
                                    'starting_experience': 1
                                })
        self.config.setdefaults('Termination',
                                {
                                    'bias_threshold': '80%',
                                    'experience_threshold': 10,
                                    'sim_max_iteration': 10000
                                })
        self.add_json_panel('Beállítások', self.config, data=_SETTINGS_UI)
        self.config.read(_SETTINGS_FILE_PATH)
        self.reload_config_values()

    # Initiasize anti-pattern
    def on_size(self, *_):
        self.commit_settings(write_to_file=False)
        self.unbind(size=self.on_size)

    def on_config_change(self, config, section, key, value):
        """Keep sensible value constraints and formatting in order when a new value is entered."""
        # enforce upper and lower bounds on user-supplied values
        bounds = {
            ('Simulation', 'starting_experience') : (0, inf),
            ('Termination', 'bias_threshold') : (50, 100),
            ('Termination', 'experience_threshold') : (0, inf),
            ('Termination', 'sim_max_iteration') : (100, inf)
        }
        if (section, key) in bounds:
            clamped_value = value
            if key == 'bias_threshold':
                clamped_value = clamped_value[:-1]
            clamped_value = float(clamped_value)
            clamped_value = max(clamped_value, bounds[(section, key)][0])
            clamped_value = min(clamped_value, bounds[(section, key)][1])
            if key != 'bias_threshold':
                # keep numeric values in integer format
                clamped_value = int(clamped_value)
            clamped_value = str(clamped_value)
            if key == 'bias_threshold':
                clamped_value += '%'
            self.config.set(section, key, clamped_value)
            self.reload_config_values(section, key)
        super().on_config_change(config, section, key, value)

    def commit_settings(self, write_to_file=True):
        """Destructively set all values in the global SETTINGS to the current values
        in our ConfigParser instance, and also save them to file."""
        update_colors = False
        update_arrow = False
        update_grid = False
        for section in self.config.sections():
            for (key, new_value) in self.config.items(section):
                # parse new_value from its raw string state
                value_type = [item['type'] for item in _SETTINGS_UI if 'key' in item and key == item['key']][0]
                if 'bool' == value_type:
                    new_value = '0' != new_value
                    if 'draw_arrow' == key:
                        update_arrow = True
                elif 'color' == value_type:
                    new_value = Color(*get_color_from_hex(new_value))
                    if new_value.rgb != getattr(SETTINGS, key).rgb:
                        update_colors = True
                elif 'numeric' == value_type:
                    new_value = int(new_value)
                elif 'options' == value_type:
                    string_to_enum = {
                        'konstans'   : SETTINGS.DistanceMetric.CONSTANT,
                        'Manhattan'  : SETTINGS.DistanceMetric.MANHATTAN,
                        'euklideszi' : SETTINGS.DistanceMetric.EUCLIDEAN
                    }
                    new_value = string_to_enum[new_value]
                    update_grid = True
                elif 'string' == value_type:
                    if '%' == new_value[-1]:
                        # percentage to plain float
                        new_value = float(new_value[:-1]) / 100
                else:
                    assert False
                setattr(SETTINGS, key, new_value)
        if write_to_file:
            # save all settings to disk
            self.config.write()
        # update graphics on main tab
        if update_colors:
            _get_agora().update_speakerdot_colors()
        if update_arrow:
            _get_agora().update_talk_arrow()
        if update_grid:
            _get_agora().clear_dist_cache()
            _get_agora().update_grid()

    def load_settings_values(self):
        """Destructively (re)set all values in our ConfigParser instance to the current global SETTINGS."""
        for section in self.config.sections():
            for (key, _) in self.config.items(section):
                old_value = getattr(SETTINGS, key)
                if isinstance(old_value, bool):
                    old_value = '1' if old_value else '0'
                elif isinstance(old_value, Color):
                    old_value = get_hex_from_color(old_value.rgb)
                elif isinstance(old_value, SETTINGS.DistanceMetric):
                    enum_to_string = {
                        SETTINGS.DistanceMetric.CONSTANT  : 'konstans',
                        SETTINGS.DistanceMetric.MANHATTAN : 'Manhattan',
                        SETTINGS.DistanceMetric.EUCLIDEAN : 'euklideszi'
                    }
                    old_value = enum_to_string[old_value]
                elif isinstance(old_value, float):
                    # plain float to percentage
                    old_value = str(100 * old_value) + '%'
                #print("Setting", section, key, str(old_value))
                self.config.set(section, key, str(old_value))
        # force the update of displayed values on GUI as well
        self.reload_config_values()

    def create_json_panel(self, title, config, filename=None, data=None):
        """Override base class method to keep it from saving to file
        every time a setting is changed."""
        assert not filename and data
        assert isinstance(data, list)
        panel = CustomSettingsPanel(title=title, settings=self, config=config)
        for setting in data:
            # determine the type and the class to use
            if 'type' not in setting:
                raise ValueError('A setting is missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError('No class registered to handle the <%s> type' % setting['type'])
            str_settings = copy(setting)
            del str_settings['type']
            instance = cls(panel=panel, **str_settings)
            # instance created, add to the panel
            panel.add_widget(instance)
        return panel

    def reload_config_values(self, section=None, key=None):
        """Refresh all values displayed in the SettingsPanel from our ConfigParser instance."""
        assert bool(section) == bool(key)
        settingspanel = self.interface.children[0].children[0]
        subtree = settingspanel.children
        for child in subtree:
            if isinstance(child, SettingItem):
                if not key or section == child.section and key == child.key:
                    child.value = self.config.get(child.section, child.key)

class ApplySettingsButton(Button):
    """Button to destructively set the user's choices in the global settings object."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.apply_settings)

    def apply_settings(self, *_):
        """Overwrite current application settings with those in the SettingsPanel."""
        _get_settings().commit_settings()
        label = ApplyConfirmedLabel()
        self.parent.add_widget(label)

class DiscardSettingsButton(Button):
    """Button to throw away all changes and restore previous settings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.discard_settings)

    def discard_settings(self, *_):
        """Reset all items in SettingsPanel to the previous application settings."""
        _get_settings().load_settings_values()
        label = DiscardConfirmedLabel()
        self.parent.add_widget(label)
