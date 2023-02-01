"""An evolving virtual community of speakers influencing each other stochastically."""

from itertools import product
from logging import debug
from time import time

from src.rng import RAND
from src.speaker import Speaker

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
            def inv_dist_sq(p):
                dist_sq = ((p['speaker'].pos[0] - p['hearer'].pos[0])**2 + (p['speaker'].pos[1] - p['hearer'].pos[1])**2)
                return 1 / dist_sq
            if not self.cum_weights:
                self.cum_weights = [0]
                for p in self.speaker_pairs:
                    self.cum_weights.append(inv_dist_sq(p) + self.cum_weights[-1])
                self.cum_weights.pop(0)
            while True:
                self.pick = RAND.choices(self.speaker_pairs, cum_weights=self.cum_weights)[0]
                if not self.pick['hearer'].is_broadcaster:
                    break
            if self.pick['speaker'].is_broadcaster:
                s = self.pick['speaker']
                self.pick_queue = [ {'speaker': s, 'hearer': h} for h in self.speakers if h != s ]
                self.pick = self.pick_queue.pop(0)
        debug(self.pick['speaker'].n, "picked to talk to", self.pick['hearer'].n)
        self.pick['speaker'].talk(self.pick)

    def all_biased(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased."""
        def stable(x):
            return x.is_broadcaster or abs(s.principal_weight() - 0.5) > 0.4
        return all(stable(s) for s in self.speakers)

    def all_biased_and_experienced(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased and experienced."""
        def stable(x):
            return x.is_broadcaster or abs(x.principal_weight() - 0.5) > 0.4 and x.experience > 10
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
