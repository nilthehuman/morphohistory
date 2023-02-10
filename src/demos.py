"""An assortment of sample agoras for experimentation and demonstration purposes."""

from abc import ABC
from math import sin, cos, pi

from .settings import SETTINGS
from .speaker import Speaker

WIDTH, HEIGHT = SETTINGS.agora_size
DOT_WIDTH, DOT_HEIGHT = SETTINGS.speakerdot_size

class DemoFactory(ABC):
    """Interface for demo generating factory classes."""

    def get_speakers():
        """Return the starting state of the speaker population."""

class Rainbow9x9(DemoFactory):
    """A 9x9 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def get_speakers():
        speakers = []
        for row in range(9):
            for col in range(9):
                weight_a = 1 - 1 / 16 * (row + col)
                pos = (WIDTH * 0.1 + WIDTH * 0.1 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.9 - HEIGHT * 0.1 * row - DOT_HEIGHT * 0.5)
                speakers.append(Speaker.fromweight(row * 9 + col, pos, weight_a))
        return speakers

class Rainbow10x10(DemoFactory):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def get_speakers():
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                weight_a = 1 - 1 / 18 * (row + col)
                pos = (WIDTH * 0.05 + WIDTH * 0.1 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.95 - HEIGHT * 0.1 * row - DOT_HEIGHT * 0.5)
                speakers.append(Speaker.fromweight(row * 10 + col, pos, weight_a))
        return speakers

class Synonymy(DemoFactory):
    """A 10x10 grid of speakers, all undecided: a case of perfect synonymy."""

    def get_speakers():
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                pos = (WIDTH * 0.05 + WIDTH * 0.1 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.95 - HEIGHT * 0.1 * row - DOT_HEIGHT * 0.5)
                speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.5))
        return speakers

class SynonymyLarge(DemoFactory):
    """A 100x100 grid of speakers, all undecided: a case of perfect synonymy."""

    def get_speakers():
        SETTINGS.speakerdot_size = (12, 12) # TODO: integrate settings into Agora, I think
        DOT_WIDTH, DOT_HEIGHT = SETTINGS.speakerdot_size
        speakers = []
        pos = [None, None]
        for row in range(30):
            for col in range(30):
                pos = (WIDTH * 0.05 + WIDTH * 0.03103 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.95 - HEIGHT * 0.03103 * row - DOT_HEIGHT * 0.5)
                speakers.append(Speaker.fromweight(row * 30 + col, pos, 0.5))
        return speakers

class CoreVsPeriphery9x9(DemoFactory):
    """A 9x9 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    def get_speakers():
        speakers = []
        pos = [None, None]
        for row in range(9):
            for col in range(9):
                pos = (WIDTH * 0.1 + WIDTH * 0.1 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.9 - HEIGHT * 0.1 * row - DOT_HEIGHT * 0.5)
                if (3 <= row <= 5 and 3 <= col <= 5):
                    speakers.append(Speaker.fromweight(row * 9 + col, pos, 0.0))
                else:
                    speakers.append(Speaker.fromweight(row * 9 + col, pos, 0.5))
        return speakers

class CoreVsPeriphery10x10(DemoFactory):
    """A 10x10 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    def get_speakers():
        speakers = []
        pos = [None, None]
        for row in range(10):
            for col in range(10):
                pos = (WIDTH * 0.05 + WIDTH * 0.1 * col - DOT_WIDTH * 0.5,
                       HEIGHT * 0.95 - HEIGHT * 0.1 * row - DOT_HEIGHT * 0.5)
                if (3 <= row <= 6 and 3 <= col <= 6):
                    speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.0))
                else:
                    speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.5))
        return speakers

class NewsAnchor(DemoFactory):
    """A circle of neutral speakers around a biased broadcaster."""

    def get_speakers():
        speakers = []
        pos = [None, None]
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * WIDTH * 0.3
            y = cos(2 * pi * float(n) / 16) * HEIGHT * 0.3
            pos = (WIDTH * 0.5 + x - DOT_WIDTH * 0.5,
                   HEIGHT * 0.5 + y - DOT_HEIGHT * 0.5)
            speakers.append(Speaker.fromweight(n, pos, 0.5))
        pos = (WIDTH * 0.5 - DOT_WIDTH * 0.5,
               HEIGHT * 0.5 - DOT_HEIGHT * 0.5)
        speakers.append(Speaker.fromweight(16, pos, 1.0, is_broadcaster=True))
        return speakers

class Rings16_24(DemoFactory):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    def get_speakers():
        speakers = []
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * WIDTH * 0.2
            y = cos(2 * pi * float(n) / 16) * HEIGHT * 0.2
            pos = (WIDTH * 0.5 + x - DOT_WIDTH * 0.5,
                   HEIGHT * 0.5 + y - DOT_HEIGHT * 0.5)
            speakers.append(Speaker.fromweight(n, pos, 0.0))
        for n in range(24):
            x = sin(2 * pi * float(n) / 24) * WIDTH * 0.4
            y = cos(2 * pi * float(n) / 24) * HEIGHT * 0.4
            pos = (WIDTH * 0.5 + x - DOT_WIDTH * 0.5,
                   HEIGHT * 0.5 + y - DOT_HEIGHT * 0.5)
            speakers.append(Speaker.fromweight(16 + n, pos, 1.0))
        return speakers

DEFAULT_DEMO = Rainbow9x9
