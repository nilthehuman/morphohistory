"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from itertools import product
from logging import debug
from random import choices, randrange
import time  # TODO remove

from paradigm import NounCell, VerbCell, NounParadigm, VerbParadigm

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, para=NounParadigm(), is_broadcaster=False):
        self.para = para
        self.experience = 1.0
        self.is_broadcaster = is_broadcaster
        # TODO: temporary hack, for demo purposes
        self.para[0][0][0] = NounCell(number=0, possessor=0, case=0,
            weight_a=self.para.para[0][0][0].weight_a, form_a='Harkivból', form_b='Harkivből', importance=0.2)

    @classmethod
    def fromweight(cls, weight_a, is_broadcaster=False):
        me = cls(NounParadigm(weight_a), is_broadcaster)
        return me

    def principal_weight(self):
        """Which way the speaker is leaning, summed up in a single float."""
        sum_w = 0
        sum_imp = 0
        for i in range(2):
            for j in range(7):
                for k in range(18):
                    if len(self.para.para[i][j][k].form_a):
                        sum_w = sum_w + self.para.para[i][j][k].weight_a * self.para.para[i][j][k].importance
                        sum_imp = sum_imp + self.para.para[i][j][k].importance
        return sum_w / sum_imp

    def name_tag(self):
        return self.para[0][0][0].to_str_short()

    def talk_to(self, hearer):
        i, j, k = -1, -1, -1
        # pick a non-empty cell to share with the hearer
        while True:
            i = randrange(2)
            j = randrange(7)
            k = randrange(18)
            if len(self.para.para[i][j][k].form_a):
                break
        weights = [self.para.para[i][j][k].weight_a, 1 - self.para.para[i][j][k].weight_a]
        is_form_a = choices([True, False], weights=weights)
        hearer.hear_noun(i, j, k, is_form_a[0])

    def hear_noun(self, i, j, k, is_form_a):
        form = self.para.para[i][j][k].form_a if is_form_a else self.para.para[i][j][k].form_b
        debug("I just heard", form)
        # we might want to use exponential decay instead
        delta = (-1 if is_form_a else 1) / (self.experience + 1)
        self.para.nudge(delta, i, j, k)
        self.para.propagate(delta, i, j, k)
        self.experience = self.experience + 1

class Agora:
    """A collection of simulated speakers talking to each other."""

    def __init__(self):
        self.pick_queue = None
        self.speaker_pairs = None
        self.inv_dist_squared = None

    # TODO: stop referring to self.children
    def simulate(self, dt, graphics=True): # TODO: do dt number of iterations?
        """Perform one iteration: pick two individuals to talk to each other
        and update the hearer's state based on the speaker's."""
        debug("Iterating simulation")
        if self.pick_queue:
            # a broadcaster is speaking
            self.pick = self.pick_queue.pop()
        else:
            if not self.speaker_pairs:
                self.speaker_pairs = list([(s, t) for (s, t) in product(self.children, self.children) if s != t])
            inv_dist_sq = lambda p, q: 1 / ((p[0] - q[0])**2 + (p[1] - q[1])**2)
            if not self.inv_dist_squared:
                self.inv_dist_squared = list([ inv_dist_sq(s.pos, t.pos) for (s, t) in self.speaker_pairs ])
            while True:
                self.pick = choices(self.speaker_pairs, weights=self.inv_dist_squared, k=1)[0]
                if (not self.pick[1].speaker.is_broadcaster):
                    break
            if self.pick[0].speaker.is_broadcaster:
                speaker = self.pick[0]
                self.pick_queue = [ (speaker, c) for c in self.children if c != speaker ]
                self.pick = self.pick_queue.pop()
        debug(self.pick[0].n, "picked to talk to", self.pick[1].n)
        self.pick[0].talk_to(self.pick[1])
        return True # keep going

    def is_stable(self):
        """When to stop the simulation"""
        return all(abs(c.speaker.principal_weight()) < 0.1 for c in self.children)

    def simulate_till_stable(self):
        """Keep running the simulation until the stability condition is reached."""
        # Make sure we stop eventually no matter what
        debug("Simulation until stable started:", time.time())
        for i in range(0, 10000):
            if self.is_stable():
                break
            self.simulate(0, graphics=False)
        debug("Simulation until stable finished:", time.time())
