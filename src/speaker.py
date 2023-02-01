"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from copy import deepcopy
from logging import debug

from src.paradigm import NounCell, Paradigm, NounParadigm
from src.rng import RAND

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, n, pos, para=NounParadigm(), is_broadcaster=False, experience=1.0):
        self.n = n
        self.pos = pos
        self.para = para
        self.experience = experience
        self.is_broadcaster = is_broadcaster
        self.principal_weight_cached = None

    def init_from_weight(self, weight_a):
        self.para = NounParadigm(weight_a)
        # TODO: temporary hack, for demo purposes
        self.para[0][0] = NounCell(number=0, case=0, weight_a=self.para.para[0][0].weight_a,
            form_a='havernak', form_b='havernek', importance=0.2)

    @classmethod
    def fromspeaker(cls, other):
        me = cls(other.n, other.pos, deepcopy(other.para), other.is_broadcaster)
        me.experience = other.experience
        return me

    @classmethod
    def fromweight(cls, n, pos, weight_a, is_broadcaster=False):
        me = cls(n, pos, NounParadigm(weight_a), is_broadcaster)
        return me

    def to_json(self):
        speaker_only = Speaker.fromspeaker(self)
        return speaker_only.__dict__

    @staticmethod
    def from_dict(speaker_dict):
        para = Paradigm.from_dict(speaker_dict['para'])
        return Speaker(speaker_dict['n'],
                       speaker_dict['pos'],
                       para,
                       speaker_dict['is_broadcaster'],
                       speaker_dict['experience'])

    def principal_weight(self):
        """Which way the speaker is leaning, summed up in a single float."""
        return self.para.para[0][0].weight_a
        # TODO: figure out why this function is slow
        if self.principal_weight_cached:
            return self.principal_weight_cached
        sum_w = 0
        sum_imp = 0
        for cases in self.para.para:
            for cell in cases:
                if cell.form_a:
                    sum_w = sum_w + cell.weight_a * cell.importance
                    sum_imp = sum_imp + cell.importance
        self.principal_weight_cached = sum_w / sum_imp
        return self.principal_weight_cached

    def name_tag(self):
        return self.para[0][0].to_str_short()

    def talk(self, pick):
        assert pick['speaker'] == self
        hearer = pick['hearer']
        assert not hearer.is_broadcaster # broadcasters are deaf
        i, j = -1, -1
        # pick a non-empty cell to share with the hearer
        while True:
            i = RAND.next() % 2
            j = RAND.next() % 18
            if self.para.para[i][j].form_a:
                break
        cum_weights = [self.para.para[i][j].weight_a, 1]
        is_form_a = RAND.choices([True, False], cum_weights=cum_weights)
        pick['is_form_a'] = is_form_a[0] # let the Agora know what we're saying
        hearer.hear_noun(i, j, is_form_a[0])

    def hear_noun(self, i, j, is_form_a):
        form = self.para.para[i][j].form_a if is_form_a else self.para.para[i][j].form_b
        debug("I just heard", form)
        # we might want to use exponential decay instead
        delta = (1 if is_form_a else -1) / (self.experience + 1)
        self.para.nudge(delta, i, j)
        self.para.propagate(delta, i, j)
        self.experience = self.experience + 1
        self.principal_weight_cached = None
