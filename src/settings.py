"""Global settings controlling GUI appearance and simulation behavior."""

#TODO: use observer pattern to spread changes

try:
    from enum import Enum, StrEnum
except ImportError:
    from strenum import StrEnum

from kivy.graphics import Color

from .paradigm import NounParadigm

class _Settings:
    """A plain struct holding all relevant constants and parameters."""

    class GuiLanguage(StrEnum):
        ENG = "English"
        HUN = "Hungarian"

    class DemoAgora(StrEnum):
        RAINBOW_9X9   = "Rainbow 9x9"
        RAINBOW_10X10 = "Rainbow 10x10"
        BALANCE       = "Balance"
        BALANCE_LARGE = "Balance Large"
        CHECKERS      = "Checkers"
        ALONE         = "Alone"
        CORE_9x9      = "Core 9x9"
        CORE_10x10    = "Core 10x10"
        NEWS_ANCHOR   = "News Anchor"
        RINGS_16_16   = "Rings 16+16"
        RINGS_16_24   = "Rings 16+24"
        VILLAGES      = "Villages"

    class DistanceMetric(StrEnum):
        CONSTANT  = "constant"
        MANHATTAN = "Manhattan"
        EUCLIDEAN = "Euclidean"

    class LearningModel(Enum):
        HARMONIC = 1
        RW       = 2

    def __init__(self):
        self.gui_language = self.GuiLanguage.ENG

        self.agora_size = (600, 600)
        self.color_a = Color(1.0, 1.0, 0.0)
        self.color_b = Color(1.0, 0.0, 1.0)
        self.color_broadcaster = Color(0.2, 0.9, 0.1)
        self.color_arrow_tip = Color(0.2, 0.0, 0.8)
        self.arrow_width = 2
        self.draw_arrow = True
        self.grid_color = Color(0.15, 0.15, 0.15)
        self.grid_resolution = 10

        self.speakerdot_size = (20, 20)
        self.popup_size_load = (400, 430)
        self.popup_size_fail = (250, 200)
        self.popup_size_progress = (500, 250)

        self.current_demo = self.DemoAgora.RAINBOW_9X9

        self.bias_threshold = 0.8
        self.starting_experience = 1
        self.experience_threshold = 10

        self.paradigm = NounParadigm(bias_a=0.5, form_a='rozéból', form_b='rozéből')

        self.sim_single_cell = True
        self.sim_distance_metric = self.DistanceMetric.CONSTANT
        #self.sim_learning_model = HARMONIC # TODO use this option
        self.sim_influence_self = True
        self.sim_influence_mutual = False
        self.sim_passive_decay = False
        self.sim_prefer_opposite = False
        self.sim_batch_size = 100
        self.sim_max_iteration = 10000

SETTINGS = _Settings()
