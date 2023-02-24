"""An assortment of sample agoras for experimentation and demonstration purposes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import sin, cos, pi

from .settings import SETTINGS
from .speaker import Speaker

_WIDTH, _HEIGHT = SETTINGS.agora_size
_DOT_WIDTH, _DOT_HEIGHT = SETTINGS.speakerdot_size

@dataclass
class _DefaultArguments:
    our_bias: float = 1
    their_bias: float = 0
    starting_experience: int = 1
    inner_radius: float = None

# TODO: use these in the class method definitions below as well
DEFAULT_DEMO_ARGUMENTS = {
    SETTINGS.DemoAgora.RAINBOW_9X9   : _DefaultArguments(),
    SETTINGS.DemoAgora.RAINBOW_10X10 : _DefaultArguments(),
    SETTINGS.DemoAgora.BALANCE       : _DefaultArguments(our_bias=None, their_bias=None),
    SETTINGS.DemoAgora.BALANCE_LARGE : _DefaultArguments(our_bias=None, their_bias=None),
    SETTINGS.DemoAgora.CHECKERS      : _DefaultArguments(),
    SETTINGS.DemoAgora.ALONE         : _DefaultArguments(),
    SETTINGS.DemoAgora.CORE_9x9      : _DefaultArguments(our_bias=0.5),
    SETTINGS.DemoAgora.CORE_10x10    : _DefaultArguments(our_bias=0.5),
    SETTINGS.DemoAgora.NEWS_ANCHOR   : _DefaultArguments(our_bias=1, their_bias=0.5, inner_radius=1),
    SETTINGS.DemoAgora.RINGS_16_16   : _DefaultArguments(our_bias=1, their_bias=0, inner_radius=0.25),
    SETTINGS.DemoAgora.RINGS_16_24   : _DefaultArguments(our_bias=1, their_bias=0, inner_radius=0.25),
    SETTINGS.DemoAgora.VILLAGES      : _DefaultArguments()
}

class _DemoFactory(ABC):
    """Interface for demo generating factory classes."""

    @staticmethod
    @abstractmethod
    def get_speakers(our_bias, their_bias, starting_experience, inner_radius):
        """Return the starting state of the speaker population."""

class Rainbow9x9(_DemoFactory):
    """A 9x9 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        for row in range(9):
            for col in range(9):
                pos = (_WIDTH * 0.1 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.9 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = our_bias + (their_bias - our_bias) * 1 / 16 * (row + col)
                speakers.append(Speaker.frombias(row * 9 + col, pos, bias_a))
        return speakers

class Rainbow10x10(_DemoFactory):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                pos = (_WIDTH * 0.05 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.95 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = our_bias + (their_bias - our_bias) * 1 / 18 * (row + col)
                speakers.append(Speaker.frombias(row * 10 + col, pos, bias_a, starting_experience))
        return speakers

class Balance(_DemoFactory):
    """A 10x10 grid of speakers, all undecided: a case of balanced alternatives."""

    @staticmethod
    def get_speakers(our_bias=None, their_bias=None, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                pos = (_WIDTH * 0.05 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.95 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                speakers.append(Speaker.frombias(row * 10 + col, pos, 0.5, starting_experience))
        return speakers

class BalanceLarge(_DemoFactory):
    """A 30x30 grid of speakers, all undecided: a case of balanced alternatives."""

    @staticmethod
    def get_speakers(our_bias=None, their_bias=None, starting_experience=1, _inner_radius=None):
        SETTINGS.speakerdot_size = (12, 12) # TODO: integrate settings into Agora, I think
        _DOT_WIDTH, _DOT_HEIGHT = SETTINGS.speakerdot_size
        speakers = []
        pos = [None, None]
        for row in range(30):
            for col in range(30):
                pos = (_WIDTH * 0.05 + _WIDTH * 0.03103 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.95 - _HEIGHT * 0.03103 * row - _DOT_HEIGHT * 0.5)
                speakers.append(Speaker.frombias(row * 30 + col, pos, 0.5, starting_experience))
        return speakers

class Checkers(_DemoFactory):
    """An 8x8 grid of biased speakers arranged in an alternating pattern."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(8):
            for col in range(8):
                pos = (_WIDTH * 0.15 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.85 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = our_bias if (row + col) % 2 else their_bias
                speakers.append(Speaker.frombias(row * 8 + col, pos, bias_a, starting_experience))
        return speakers

class AloneAgainstTheWorld(_DemoFactory):
    """A 9x9 grid of speakers, all but one speaker biased towards A, the loner is biased towards B."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(9):
            for col in range(9):
                pos = (_WIDTH * 0.1 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.9 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = our_bias if row == col == 4 else their_bias
                speakers.append(Speaker.frombias(row * 9 + col, pos, bias_a, starting_experience))
        return speakers

class CoreVsPeriphery9x9(_DemoFactory):
    """A 9x9 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    @staticmethod
    def get_speakers(our_bias=0.5, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(9):
            for col in range(9):
                pos = (_WIDTH * 0.1 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.9 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = their_bias if (3 <= row <= 5 and 3 <= col <= 5) else our_bias
                speakers.append(Speaker.frombias(row * 9 + col, pos, bias_a, starting_experience))
        return speakers

class CoreVsPeriphery10x10(_DemoFactory):
    """A 10x10 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    @staticmethod
    def get_speakers(our_bias=0.5, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                pos = (_WIDTH * 0.05 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                       _HEIGHT * 0.95 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                bias_a = their_bias if (3 <= row <= 6 and 3 <= col <= 6) else our_bias
                speakers.append(Speaker.frombias(row * 10 + col, pos, bias_a, starting_experience))
        return speakers

class NewsAnchor(_DemoFactory):
    """A circle of neutral speakers around a biased broadcaster."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0.5, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * _WIDTH * 0.3
            y = cos(2 * pi * float(n) / 16) * _HEIGHT * 0.3
            pos = (_WIDTH * 0.5 + x - _DOT_WIDTH * 0.5,
                   _HEIGHT * 0.5 + y - _DOT_HEIGHT * 0.5)
            speakers.append(Speaker.frombias(n, pos, their_bias, starting_experience))
        pos = (_WIDTH * 0.5 - _DOT_WIDTH * 0.5,
               _HEIGHT * 0.5 - _DOT_HEIGHT * 0.5)
        speakers.append(Speaker.frombias(16, pos, our_bias, starting_experience, is_broadcaster=True))
        return speakers

class Rings16_16(_DemoFactory):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, inner_radius=0.5):
        speakers = []
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * _WIDTH * 0.4 * inner_radius
            y = cos(2 * pi * float(n) / 16) * _HEIGHT * 0.4 * inner_radius
            pos = (_WIDTH * 0.5 + x - _DOT_WIDTH * 0.5,
                   _HEIGHT * 0.5 + y - _DOT_HEIGHT * 0.5)
            speakers.append(Speaker.frombias(n, pos, their_bias))
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * _WIDTH * 0.4
            y = cos(2 * pi * float(n) / 16) * _HEIGHT * 0.4
            pos = (_WIDTH * 0.5 + x - _DOT_WIDTH * 0.5,
                   _HEIGHT * 0.5 + y - _DOT_HEIGHT * 0.5)
            speakers.append(Speaker.frombias(16 + n, pos, our_bias))
        return speakers

class Rings16_24(_DemoFactory):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, inner_radius=0.5):
        speakers = []
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * _WIDTH * 0.4 * inner_radius
            y = cos(2 * pi * float(n) / 16) * _HEIGHT * 0.4 * inner_radius
            pos = (_WIDTH * 0.5 + x - _DOT_WIDTH * 0.5,
                   _HEIGHT * 0.5 + y - _DOT_HEIGHT * 0.5)
            speakers.append(Speaker.frombias(n, pos, their_bias))
        for n in range(24):
            x = sin(2 * pi * float(n) / 24) * _WIDTH * 0.4
            y = cos(2 * pi * float(n) / 24) * _HEIGHT * 0.4
            pos = (_WIDTH * 0.5 + x - _DOT_WIDTH * 0.5,
                   _HEIGHT * 0.5 + y - _DOT_HEIGHT * 0.5)
            speakers.append(Speaker.frombias(16 + n, pos, our_bias))
        return speakers

class Villages(_DemoFactory):
    """Four different compact communities a bit further apart from each other."""

    @staticmethod
    def get_speakers(our_bias=1, their_bias=0, starting_experience=1, _inner_radius=None):
        speakers = []
        pos = [None, None]
        for row in range(9):
            for col in range(9):
                if (row < 3 or 5 < row) and (col < 3 or 5 < col):
                    pos = (_WIDTH * 0.1 + _WIDTH * 0.1 * col - _DOT_WIDTH * 0.5,
                           _HEIGHT * 0.9 - _HEIGHT * 0.1 * row - _DOT_HEIGHT * 0.5)
                    bias_a = their_bias if (row < 3) == (col < 3) else our_bias
                    speakers.append(Speaker.frombias(row * 9 + col, pos, bias_a))
        return speakers

DEMO_FACTORIES = {
    SETTINGS.DemoAgora.RAINBOW_9X9   : Rainbow9x9,
    SETTINGS.DemoAgora.RAINBOW_10X10 : Rainbow10x10,
    SETTINGS.DemoAgora.BALANCE       : Balance,
    SETTINGS.DemoAgora.BALANCE_LARGE : BalanceLarge,
    SETTINGS.DemoAgora.CHECKERS      : Checkers,
    SETTINGS.DemoAgora.ALONE         : AloneAgainstTheWorld,
    SETTINGS.DemoAgora.CORE_9x9      : CoreVsPeriphery9x9,
    SETTINGS.DemoAgora.CORE_10x10    : CoreVsPeriphery10x10,
    SETTINGS.DemoAgora.NEWS_ANCHOR   : NewsAnchor,
    SETTINGS.DemoAgora.RINGS_16_16   : Rings16_16,
    SETTINGS.DemoAgora.RINGS_16_24   : Rings16_24,
    SETTINGS.DemoAgora.VILLAGES      : Villages
}
