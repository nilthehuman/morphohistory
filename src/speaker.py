"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from copy import deepcopy
from logging import debug

from .paradigm import NounParadigm
from .rng import RAND
from .settings import SETTINGS

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, n, pos, para=None, experience=SETTINGS.starting_experience, is_broadcaster=False):
        self.n = n
        self.pos = pos
        self.para = para
        self.experience = experience
        self.is_broadcaster = is_broadcaster
        self.principal_bias_cached = None

    @classmethod
    def fromspeaker(cls, speaker):
        """Copy an existing Speaker."""
        new_speaker = cls(speaker.n, speaker.pos, deepcopy(speaker.para),
                          speaker.experience, speaker.is_broadcaster)
        return new_speaker

    @classmethod
    def frombias(cls, n, pos, bias_a, experience=SETTINGS.starting_experience, is_broadcaster=False):
        """Construct a Speaker from a single bias value."""
        para = NounParadigm(bias_a=bias_a, form_a=SETTINGS.paradigm.para[0][0].form_a,
                                           form_b=SETTINGS.paradigm.para[0][0].form_b)
        new_speaker = cls(n, pos, para, experience, is_broadcaster)
        return new_speaker

    def to_dict(self):
        """Export object contents for JSON serialization."""
        speaker_only = Speaker.fromspeaker(self)
        speaker_dict = speaker_only.__dict__
        del speaker_dict['principal_bias_cached']
        return speaker_dict

    @staticmethod
    def from_dict(speaker_dict):
        """Reconstruct Speaker object from an imported JSON dictionary."""
        para = NounParadigm.from_dict(speaker_dict['para'])
        return Speaker(speaker_dict['n'],
                       speaker_dict['pos'],
                       para,
                       speaker_dict['experience'],
                       speaker_dict['is_broadcaster'])

    def principal_bias(self):
        """Which way the speaker is leaning, summed up in a single float."""
        return self.para.para[0][0].bias_a
        # TODO: figure out why this function is slow
        if self.principal_bias_cached:
            return self.principal_bias_cached
        sum_bias = 0
        sum_prominence = 0
        for cases in self.para.para:
            for cell in cases:
                if cell.form_a:
                    sum_bias += cell.bias_a * cell.prominence
                    sum_prominence += cell.prominence
        self.principal_bias_cached = sum_bias / sum_prominence
        return self.principal_bias_cached

    def name_tag(self):
        """Text to display next to SpeakerDot label on mouse hover."""
        return self.para[0][0].to_str_short() + "; xp:%d" % self.experience

    def talk(self, pick):
        """Interact with and influence another Speaker in the Agora."""
        assert pick['speaker'] == self
        hearer = pick['hearer']
        assert not hearer.is_broadcaster # broadcasters are deaf
        i, j = 0, 0
        if not SETTINGS.sim_single_cell:
            # pick a non-empty cell to share with the hearer
            while True:
                i = RAND.next() % 2
                j = RAND.next() % 18
                if self.para.para[i][j].form_a:
                    break
        cum_weights = [self.para.para[i][j].bias_a, 1]
        form_a_used = RAND.choices([True, False], cum_weights=cum_weights)[0]
        if SETTINGS.sim_prefer_opposite:
            form_a_used = not form_a_used
        hearer.hear_noun(i, j, form_a_used)
        if SETTINGS.sim_influence_self:
            self.hear_noun(i, j, form_a_used)
        return (i, j), form_a_used  # let the Agora know which form of which cell we used

    def hear_noun(self, i, j, is_form_a):
        """Accept a given form from another Speaker and adjust own bias based on it."""
        form = self.para.para[i][j].form_a if is_form_a else self.para.para[i][j].form_b
        debug("Speaker: I just heard '%s'" % form)
        delta = (1 if is_form_a else -1) / (self.experience + 1)
        self.para.nudge(delta, i, j)
        self.para.propagate(delta, i, j)
        self.experience = self.experience + 1
        self.principal_bias_cached = None

    def passive_decay(self):
        """Tilt all biases slightly in favor of the preferred form, fading the opposite form."""
        self.para.passive_decay()
