"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from bisect import bisect
from copy import deepcopy
from itertools import product
from json import loads
from logging import debug
from time import time
try:
    from simplerandom.iterators import MWC1
    class RNG:
        def __init__(self):
            self.mwc = MWC1() # unseeded is fine
        def next(self):
            return next(self.mwc)
        def choices(self, population, cum_weights):
            assert len(population) == len(cum_weights)
            scale = cum_weights[-1] + 0.0
            r = next(self.mwc) / 2**32
            # copied this trick from the original Lib/random.py
            return [population[bisect(cum_weights, r * scale, 0, len(population) - 1)]]
except ImportError:
    from random import choices, randrange
    class RNG:
        def next(self):
            return randrange(0, 2**32)
        def choices(self, population, cum_weights):
            return choices(population, cum_weights=cum_weights)

from .paradigm import NounCell, VerbCell, Paradigm, NounParadigm, VerbParadigm

RAND = RNG()

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
    def from_json(speaker_dict):
        para = Paradigm.from_json(speaker_dict['para'])
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

class Agora:
    """A collection of simulated speakers influencing each other."""

    def __init__(self):
        self.speakers = []
        self.clear_caches()
        self.sim_iteration = None
        self.sim_cancelled = False
        self.graphics_on = False

    def save_starting_state(self):
        """Stash a snapshot of the current list of speakers."""
        # N.B. paradigms are deep copied by Speaker.fromspeaker
        self.starting_speakers = [Speaker.fromspeaker(s) for s in self.speakers]

    def reset(self):
        """Restore earlier speaker snapshot."""
        self.clear_speakers()
        self.load_speakers(self.starting_speakers)

    def clear_caches(self):
        """Invalidate cache variables."""
        # variables for expensive calculations
        self.speaker_pairs = None
        self.cum_weights = None
        self.pick_queue = None

    def clear_dist_cache(self):
        self.cum_weights = None

    def clear_speakers(self):
        self.speakers = []
        self.clear_caches()

    def load_speakers(self, speakers):
        self.speakers = [Speaker.fromspeaker(s) for s in speakers]
        self.clear_caches()

    def add_speaker(self, speaker):
        self.speakers.append(Speaker.fromspeaker(speaker))
        self.clear_caches()

    def simulate(self, *_): # TODO: use threading to perform independent picks in parallel
        """Perform one iteration: pick two individuals to talk to each other
        and update the hearer's state based on the speaker's."""
        debug("Iterating simulation")
        if self.pick_queue:
            # a broadcaster is speaking
            self.pick = self.pick_queue.pop(0)
        else:
            if not self.speaker_pairs:
                self.speaker_pairs = list([{'speaker': s, 'hearer': h} for (s, h) in product(self.speakers, self.speakers) if s != h])
            inv_dist_sq = lambda p: 1 / ((p['speaker'].pos[0] - p['hearer'].pos[0])**2 + (p['speaker'].pos[1] - p['hearer'].pos[1])**2)
            if not self.cum_weights:
                self.cum_weights = [0]
                for p in self.speaker_pairs:
                     self.cum_weights.append(inv_dist_sq(p) + self.cum_weights[-1])
                self.cum_weights.pop(0)
            while True:
                self.pick = RAND.choices(self.speaker_pairs, cum_weights=self.cum_weights)[0]
                if (not self.pick['hearer'].is_broadcaster):
                    break
            if self.pick['speaker'].is_broadcaster:
                s = self.pick['speaker']
                self.pick_queue = [ {'speaker': s, 'hearer': h} for h in self.speakers if h != s ]
                self.pick = self.pick_queue.pop(0)
        debug(self.pick['speaker'].n, "picked to talk to", self.pick['hearer'].n)
        self.pick['speaker'].talk(self.pick)
        #return True # keep going

    def all_biased(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased."""
        stable = lambda x: x.is_broadcaster or abs(s.principal_weight() - 0.5) > 0.4
        return all(stable(s) for s in self.speakers)

    def all_biased_and_experienced(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased and experienced."""
        stable = lambda x: x.is_broadcaster or abs(x.principal_weight() - 0.5) > 0.4 and x.experience > 10
        return all(stable(s) for s in self.speakers)

    def simulate_till_stable(self, batch_size=None, is_stable=all_biased_and_experienced):
        """Keep running the simulation until the stability condition is reached."""
        debug("Simulation until stable started:", time())
        max_iteration = 10000
        if not self.sim_iteration:
            self.sim_iteration = 0
        until = self.sim_iteration + batch_size + 1 if batch_size else max_iteration + 1
        for self.sim_iteration in range(self.sim_iteration + 1, until):
            if self.sim_cancelled:
                self.sim_cancelled = False
                self.sim_iteration = None
                return True
            if is_stable and is_stable(self):
                self.sim_iteration = None
                return True
            self.simulate()
            # Make sure we stop eventually no matter what
            if max_iteration < self.sim_iteration:
                self.sim_iteration = None
                return True
        debug("Simulation until stable finished:", time())
        return False
