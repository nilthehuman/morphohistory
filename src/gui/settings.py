"""The contents of the Settings tab: a list of user options to control the simulation parameters."""

from copy import copy
from logging import error
from math import inf
from os.path import join
from sys import path
from typing import Dict, Optional, Self, Union

from kivy.config import ConfigParser
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.settings import InterfaceWithNoMenu, Settings, SettingItem, SettingOptions, SettingsPanel
from kivy.utils import get_color_from_hex, get_hex_from_color

from .access_widgets import get_root, get_agora, get_settings
from .confirm import ApplyConfirmedLabel, DiscardConfirmedLabel
from .l10n import LocalizedString, localize, unlocalize, localize_all_texts, unlocalize_all_texts

from ..settings import SETTINGS

Settings.interface_cls = InterfaceWithNoMenu

_SETTINGS_FILE_PATH = join(path[0], 'user_settings.ini')

ConfigItem = Dict[str, Union[str, list[str]]]

class ConfigList(list[ConfigItem]):
    def __getitem__(self, key: str) -> ConfigItem:
        return [item for item in _SETTINGS_UI if 'key' in item and key == item['key']][0]

_SETTINGS_UI = ConfigList([
    {
        "type": "title",
        "title": "Appearance"
    },
    {
        "type": "options",
        "title": "App language",
        "desc": "The language of the application's user interface",
        "section": "Appearance",
        "key": "gui_language",
        "options": ["English", "Hungarian"]
    },
    {
        "type": "color",
        "title": "Color A",
        "desc": "The color designating the first alternant",
        "section": "Appearance",
        "key": "color_a"
    },
    {
        "type": "color",
        "title": "Color B",
        "desc": "The color designating the second alternant",
        "section": "Appearance",
        "key": "color_b"
    },
    {
        "type": "color",
        "title": "Broadcaster color",
        "desc": "The color of a speaker talking to everyone",
        "section": "Appearance",
        "key": "color_broadcaster"
    },
    {
        "type": "bool",
        "title": "Show interaction",
        "desc": "Draw an arrow to make the current interaction visible",
        "section": "Appearance",
        "key": "draw_arrow"
    },
    {
        "type": "title",
        "title": "Simulation"
    },
    {
        "type": "options",
        "title": "Distance metric",
        "desc": "What kind of geometry to use",
        "section": "Simulation",
        "key": "sim_distance_metric",
        "options": ["constant", "Manhattan", "Euclidean"]
    },
    {
        "type": "options",
        "title": "Learning model",
        "desc": "Control how speakers update their biases after an interaction",
        "section": "Simulation",
        "key": "sim_learning_model",
        "options": ["harmonic", "Rescorla-Wagner (vanilla)", "Rescorla-Wagner (weighted)"]
    },
    {
        "type": "bool",
        "title": "Self influence",
        "desc": "Should a speaker affect itself",
        "section": "Simulation",
        "key": "sim_influence_self"
    },
    {
        "type": "bool",
        "title": "Mutual influence",
        "desc": "Should both parties affect each other",
        "section": "Simulation",
        "key": "sim_influence_mutual"
    },
    {
        "type": "bool",
        "title": "Passive decay",
        "desc": "Should underrepresented forms be forgotten with time",
        "section": "Simulation",
        "key": "sim_passive_decay"
    },
    {
        "type": "bool",
        "title": "Reverse preference",
        "desc": "Should speakers prefer the opposite of the forms we encounter",
        "section": "Simulation",
        "key": "sim_prefer_opposite"
    },
    {
        "type": "numeric",
        "title": "Starting experience",
        "desc": "Number of interactions speakers are assumed to have initially",
        "section": "Simulation",
        "key": "starting_experience"
    },
    {
        "type": "title",
        "title": "Termination"
    },
    {
        "type": "string",
        "title": "Bias threshold",
        "desc": "Degree of bias expected of every speaker before the simulation halts",
        "section": "Termination",
        "key": "bias_threshold"
    },
    {
        "type": "numeric",
        "title": "Experience threshold",
        "desc": "Number of forms encountered expected of every speaker before the simulation halts",
        "section": "Termination",
        "key": "experience_threshold"
    },
    {
        "type": "numeric",
        "title": "Max iterations",
        "desc": "Maximum number of iterations allowed in fast forward",
        "section": "Termination",
        "key": "sim_max_iteration"
    }
])

class SettingsTabLayout(BoxLayout):
    """The vertical BoxLayout for the CustomSettingsPanel and the Buttons at the bottom."""
    pass

class CustomSettingsPanel(SettingsPanel):
    """Override base class to keep it from saving to file every time a setting is changed."""
    def set_value(self, section: str, key: str, value: str) -> None:
        """Override base class method to keep it from saving to file
        every time a setting is changed."""
        current = self.get_value(section, key)
        if current == value:
            return
        self.config.set(section, key, value)
        #self.config.write() # don't write to file just yet
        self.settings.dispatch('on_config_change', self.config, section, key, value)

class CustomSettingOptions(SettingOptions):
    """Override base class to allow localization inside dynamically created options Popup."""
    def _create_popup(self, instance: Self) -> None:
        super()._create_popup(instance)
        localize_all_texts(self.popup)

class CustomSettings(Settings):
    """A list of user preferences to control the appearance and operation of the application."""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.register_type('options', CustomSettingOptions)
        self.config = ConfigParser()
        self.config.setdefaults('Appearance',
                                {
                                    'gui_language': 'English',
                                    'color_a': '#ffff00',
                                    'color_b': '#ff00ff',
                                    'color_broadcaster': '#00ff00',
                                    'draw_arrow': 1
                                })
        self.config.setdefaults('Simulation',
                                {
                                    'sim_distance_metric': 'constant',
                                    'sim_learning_model': 'harmonic',
                                    'sim_influence_self': 1,
                                    'sim_influence_mutual': 0,
                                    'sim_passive_decay': 0,
                                    'sim_prefer_opposite': 0,
                                    'starting_experience': 1
                                })
        self.config.setdefaults('Termination',
                                {
                                    'bias_threshold': '80%',
                                    'experience_threshold': 10,
                                    'sim_max_iteration': 10000
                                })
        self.add_json_panel('Settings', self.config, data=_SETTINGS_UI)
        self.config.read(_SETTINGS_FILE_PATH)
        self.reload_config_values()

    def on_gui_ready(self) -> None:
        """Pump the settings values read from file into the global SETTINGS object
        and refresh the AgoraWidget's graphics on the main tab."""
        self.commit_settings(write_to_file=False, force_update=True)

    def on_config_change(self, config: ConfigParser, section: str, key: str, value: str) -> None:
        """Keep sensible value constraints and formatting in order when a new value is entered."""
        # enforce upper and lower bounds on user-supplied values
        bounds = {
            ('Simulation' , 'starting_experience')  : (  0, inf),
            ('Termination', 'bias_threshold')       : ( 50, 100),
            ('Termination', 'experience_threshold') : (  0, inf),
            ('Termination', 'sim_max_iteration')    : (100, 1e20)
        }
        if (section, key) in bounds:
            clamped_value = value
            if clamped_value[-1] == '%':
                clamped_value = clamped_value[:-1]
            try:
                clamped_value = float(clamped_value)
            except ValueError:
                get_settings().load_settings_values(section, key)
                return
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
        elif isinstance(value, LocalizedString):
            # prevent localized string values from seeping into the ConfigParser
            unloc_value = unlocalize(value)
            if 'gui_language' == key:
                unloc_value = SETTINGS.GuiLanguage(unloc_value)
            elif 'sim_distance_metric' == key:
                unloc_value = SETTINGS.DistanceMetric(unloc_value)
            elif 'sim_learning_model' == key:
                unloc_value = SETTINGS.LearningModel(unloc_value)
            else:
                assert False
            self.config.set(section, key, unloc_value)
            # no reload on purpose: preserve localized strings on user interface
        super().on_config_change(config, section, key, value)

    def commit_settings(self, write_to_file: bool=True, force_update: bool=False) -> None:
        """Destructively set all values in the global SETTINGS to the current values
        in our ConfigParser instance, and also save them to file."""
        update_lang = force_update
        update_colors = force_update
        update_grid = force_update
        update_arrow = False
        update_starting_experience = False
        for section in self.config.sections():
            for (key, new_value) in self.config.items(section):
                assert not isinstance(new_value, LocalizedString)
                # parse new_value from its raw string state
                value_type = _SETTINGS_UI[key]['type']
                if 'bool' == value_type:
                    new_value = '0' != new_value
                    if 'draw_arrow' == key and new_value == ('0' if getattr(SETTINGS, key) else '1'):
                        update_arrow = True
                elif 'color' == value_type:
                    new_value = Color(*get_color_from_hex(new_value))
                    if new_value.rgb != getattr(SETTINGS, key).rgb:
                        update_colors = True
                elif 'numeric' == value_type:
                    new_value = int(new_value)
                    if 'starting_experience' == key and new_value != getattr(SETTINGS, key):
                        update_starting_experience = True
                elif 'options' == value_type:
                    if new_value != getattr(SETTINGS, key):
                        if 'gui_language' == key:
                            update_lang = True
                        elif 'sim_distance_metric' == key:
                            update_grid = True
                        elif 'sim_learning_model' == key:
                            pass
                        else:
                            assert False
                elif 'string' == value_type:
                    if '%' == new_value[-1]:
                        # percentage to plain float
                        new_value = float(new_value[:-1]) / 100
                else:
                    assert False
                if not 'gui_language' == key:
                    setattr(SETTINGS, key, new_value)
        # update application language
        if update_lang:
            unlocalize_all_texts(get_root())
            SETTINGS.gui_language = SETTINGS.GuiLanguage(self.config['Appearance']['gui_language'])
            localize_all_texts(get_root())
            # strings like "%d+ iterations" are currently not handled by the l10n system
            get_agora().update_iteration_counter()
        # update graphics on main tab
        if update_colors:
            get_agora().update_speakerdot_colors()
        if update_arrow:
            get_agora().update_talk_arrow()
        if update_grid:
            get_agora().clear_dist_cache()
            get_agora().update_grid()
        if update_starting_experience:
            get_agora().set_starting_experience()
        # save all settings to disk
        if write_to_file:
            self.config.write()

    def load_settings_values(self, section: Optional[str]=None, key: Optional[str]=None) -> None:
        """Destructively (re)set all values in our ConfigParser instance to the current global SETTINGS."""
        for config_section in self.config.sections():
            for (config_key, _) in self.config.items(config_section):
                if not key or section == config_section and key == config_key:
                    old_value = getattr(SETTINGS, config_key)
                    if isinstance(old_value, bool):
                        old_value = '1' if old_value else '0'
                    elif isinstance(old_value, Color):
                        old_value = get_hex_from_color(old_value.rgb)
                    elif isinstance(old_value, float):
                        # plain float to percentage
                        old_value = str(100 * old_value) + '%'
                    self.config.set(config_section, config_key, str(old_value))
        # force the update of displayed values on GUI as well
        self.reload_config_values()

    def create_json_panel(self, title: str, config: ConfigParser,
                          filename: Optional[str]=None, data: Optional[ConfigList]=None) -> CustomSettingsPanel:
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

    def reload_config_values(self, section: Optional[str]=None, key: Optional[str]=None) -> None:
        """Refresh values displayed in the SettingsPanel from our ConfigParser instance."""
        assert bool(section) == bool(key)
        settingspanel = self.interface.children[0].children[0]
        subtree = settingspanel.children
        for child in subtree:
            if isinstance(child, SettingItem):
                if not key or section == child.section and key == child.key:
                    value = self.config.get(child.section, child.key)
                    # make sure we've got a legal value for this key
                    value_type = _SETTINGS_UI[child.key]['type']
                    if 'options' == value_type:
                        options = _SETTINGS_UI[child.key]['options']
                        if value not in options:
                            error("Settings: Invalid option value '%s' given for %s, using '%s' instead." %
                                  (value, child.key, options[0]))
                            value = options[0]
                            self.config.set(child.section, child.key, value)
                    child.value = localize(value)

class ApplySettingsButton(Button):
    """Button to destructively set the user's choices in the global settings object."""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bind(on_release=self.apply_settings)

    def apply_settings(self, *_) -> None:
        """Overwrite current application settings with those in the SettingsPanel."""
        get_settings().commit_settings()
        label = ApplyConfirmedLabel()
        self.parent.add_widget(label)

class DiscardSettingsButton(Button):
    """Button to throw away all changes and restore previous settings."""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bind(on_release=self.discard_settings)

    def discard_settings(self, *_) -> None:
        """Reset all items in SettingsPanel to the previous application settings."""
        get_settings().load_settings_values()
        label = DiscardConfirmedLabel()
        self.parent.add_widget(label)
