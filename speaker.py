"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from paradigm import NounParadigm, VerbParadigm

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, para=NounParadigm()):
        self.para = para
        self.experience = 1.0

    @classmethod
    def fromweight(cls, weight_a):
        me = cls(NounParadigm(weight_a))
        return me

    def name_tag():
        return str(self.para[0][0][0])

    def hear_noun(self, i, j, k, form_a):
        self.para.nudge((-1 if form_a else 1) / self.experience, i, j, k)
        self.para.propagate(self.experience)

    def say_noun(self, hearer, i, j, k, form_a):
        pass
