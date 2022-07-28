"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from logging import debug
from random import choices, randrange

from paradigm import NounCell, VerbCell, NounParadigm, VerbParadigm

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, para=NounParadigm()):
        self.para = para
        self.experience = 10.0 # experiment!! reset to 1
        self.para.fill_cell(NounCell(number=0, possessor=0, case=0, weight_a=self.para.para[0][0][0].weight_a, form_a='Harkivból', form_b='Harkivből', importance=0.2), 0, 0, 0)
        print(str(self.para.para[0][0][0]))

    @classmethod
    def fromweight(cls, weight_a):
        me = cls(NounParadigm(weight_a))
        return me

    def principal_weight(self):
        """Which way the speaker is leaning, summed up in a single float."""
        sum_w = 0
        sum_imp = 0.000001 # avoid div by zero
        for i in range(2):
            for j in range(7):
                for k in range(18):
                    if len(self.para.para[i][j][k].form_a):
                        sum_w = sum_w + self.para.para[i][j][k].weight_a * self.para.para[i][j][k].importance
                        sum_imp = sum_imp + self.para.para[i][j][k].importance
        return sum_w / sum_imp

    def name_tag():
        return str(self.para[0][0][0])

    def talk_to(self, hearer):
        i = randrange(2)
        j = randrange(7)
        k = randrange(18)
        weights = [self.para.para[i][j][k].weight_a, 1 - self.para.para[i][j][k].weight_a]
        is_form_a = choices([True, False], weights=weights)
        hearer.hear_noun(i, j, k, is_form_a[0])

    def hear_noun(self, i, j, k, is_form_a):
        form = self.para.para[i][j][k].form_a if is_form_a else self.para.para[i][j][k].form_b
        if len(form):
            print("I just heard", form)
        # we might want to use exponential decay instead
        delta = (-1 if is_form_a else 1) / (self.experience + 1)
        self.para.nudge(delta, i, j, k)
        self.para.propagate(delta, i, j, k)
        self.experience = self.experience + 1
