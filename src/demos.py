"""An assortment of sample agoras for experimentation and demonstration purposes."""

from abc import ABC
from math import sin, cos, pi

from .speaker import Speaker

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
                pos = self.width * 0.1 + self.width * 0.1 * col - 10, self.height * 0.9 - self.height * 0.1 * row - 10
                speakers.append(Speaker.fromweight(row * 10 + col, pos, weight_a))
        return speakers

class Rainbow10x10(DemoFactory):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def get_speakers():
        speakers = []
        for row in range(10):
            for col in range(10):
                weight_a = 1 - 1 / 18 * (row + col)
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                speakers.append(Speaker.fromweight(row * 10 + col, pos, weight_a))
        return speakers

class Synonymy(DemoFactory):
    """A 10x10 grid of speakers, all undecided: a case of perfect synonymy."""

    def get_speakers():
        speakers = []
        for row in range(10):
            for col in range(10):
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.5))
        return speakers

class CoreVsPeriphery10x10(DemoFactory):
    """A 10x10 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    def get_speakers():
        speakers = []
        for row in range(10):
            for col in range(10):
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                if (3 <= row and row <= 6 and 3 <= col and col <= 6):
                    speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.0))
                else:
                    speakers.append(Speaker.fromweight(row * 10 + col, pos, 0.5))
        return speakers

class NewsAnchor(DemoFactory):
    """A circle of neutral speakers around a biased broadcaster."""

    def get_speakers():
        speakers = []
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 180
            y = cos(2 * pi * float(n) / 16) * 180
            pos = (300 + x - 10, 300 + y - 10)
            speakers.append(Speaker.fromweight(n, pos, 0.5))
        broadcaster = speakers.append(Speaker.fromweight(16, (300 - 10, 300 - 10), 1.0, is_broadcaster=True))
        return speakers

class Rings16_24(DemoFactory):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    def get_speakers():
        speakers = []
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 120
            y = cos(2 * pi * float(n) / 16) * 120
            pos = (300 + x - 10, 300 + y - 10)
            speakers.append(Speaker.fromweight(n, pos, 0.0))
        for n in range(24):
            x = sin(2 * pi * float(n) / 24) * 240
            y = cos(2 * pi * float(n) / 24) * 240
            pos = (300 + x - 10, 300 + y - 10)
            speakers.append(Speaker.fromweight(16 + n, pos, 0.0))
        return speakers
