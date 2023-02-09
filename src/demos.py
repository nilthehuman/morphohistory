"""An assortment of sample agoras for experimentation and demonstration purposes."""

from math import sin, cos, pi

from .gui import SpeakerDot, BroadcasterSpeakerDot, AgoraWidget

class DemoAgoraWidget1(AgoraWidget):
    """A 10x10 grid of speakers, pure A in the top left corner, pure B at bottom right and everything else in between."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for row in range(10):
            for col in range(10):
                weight_b = 1 / 18 * (row + col)
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                self.add_speakerdot(SpeakerDot(row * 10 + col, pos, 1 - weight_b))
        self.unbind(size=self.populate)
        self.save_starting_state()

    #def populate_9x9(self, *_):
    #    for row in range(9):
    #        for col in range(9):
    #            weight_b = 1 / 16 * (row + col)
    #            pos = self.width * 0.1 + self.width * 0.1 * col - 10, self.height * 0.9 - self.height * 0.1 * row - 10
    #            self.add_speakerdot(SpeakerDot(row * 10 + col, pos, 1 - weight_b))
    #    self.unbind(size=self.populate)
    #    self.save_starting_state()

class DemoAgoraWidget2(AgoraWidget):
    """A 10x10 grid of speakers, neutral majority on the outside, biased minority on the inside."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for row in range(10):
            for col in range(10):
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                if (3 <= row and row <= 6 and 3 <= col and col <= 6):
                    self.add_speakerdot(SpeakerDot(row * 10 + col, pos, 0.0))
                else:
                    self.add_speakerdot(SpeakerDot(row * 10 + col, pos, 0.5))
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget3(AgoraWidget):
    """A circle of neutral speakers around a biased broadcaster."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 180
            y = cos(2 * pi * float(n) / 16) * 180
            pos = (300 + x - 10, 300 + y - 10)
            self.add_speakerdot(SpeakerDot(n, pos, 0.5))
        broadcaster = BroadcasterSpeakerDot(16, (300 - 10, 300 - 10), 1.0)
        self.add_speakerdot(broadcaster)
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget4(AgoraWidget):
    """A smaller ring of A speakers inside a wider ring of B speakers."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for n in range(16):
            x = sin(2 * pi * float(n) / 16) * 120
            y = cos(2 * pi * float(n) / 16) * 120
            pos = (300 + x - 10, 300 + y - 10)
            self.add_speakerdot(SpeakerDot(n, pos, 0.0))
        for n in range(24):
            x = sin(2 * pi * float(n) / 24) * 240
            y = cos(2 * pi * float(n) / 24) * 240
            pos = (300 + x - 10, 300 + y - 10)
            self.add_speakerdot(SpeakerDot(16 + n, pos, 1.0))
        self.unbind(size=self.populate)
        self.save_starting_state()

class DemoAgoraWidget5(AgoraWidget):
    """A 10x10 grid of speakers, all undecided: a case of perfect synonymy."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ugh, this is pretty ughly, but the widget still has default size at this point...
        self.bind(size=self.populate)

    def populate(self, *_):
        for row in range(10):
            for col in range(10):
                pos = self.width * 0.05 + self.width * 0.1 * col - 10, self.height * 0.95 - self.height * 0.1 * row - 10
                self.add_speakerdot(SpeakerDot(row * 10 + col, pos, 0.5))
        self.unbind(size=self.populate)
        self.save_starting_state()
