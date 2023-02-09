"""An evolving virtual community of speakers influencing each other stochastically."""

from itertools import product
from json import dumps, load
from logging import debug
from time import time

from .rng import RAND
from .settings import SETTINGS
from .speaker import Speaker

def inv_dist_sq_constant(_):
    return 1

def inv_dist_sq_manhattan(pair):
    speaker = pair['speaker']
    hearer = pair['hearer']
    dist_sq = (abs(speaker.pos[0] - hearer.pos[0]) + abs(speaker.pos[1] - hearer.pos[1])) ** 2
    return 1 / dist_sq

def inv_dist_sq_euclidean(pair):
    speaker = pair['speaker']
    hearer = pair['hearer']
    dist_sq = (speaker.pos[0] - hearer.pos[0]) ** 2 + (speaker.pos[1] - hearer.pos[1]) ** 2
    return 1 / dist_sq

class Agora:
    """A collection of simulated speakers influencing each other."""

    def __init__(self):
        self.speakers = []
        self.clear_caches()
        self.sim_iteration = None
        self.sim_cancelled = False
        self.graphics_on = False
        self.starting_speakers = None
        self.speaker_pairs = None
        self.cum_weights = None
        self.pick = None
        self.pick_queue = None

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

    def save_to_file(self, filepath):
        with open(filepath, 'w') as stream:
            stream.write(dumps(self.speakers, indent=1, default=lambda x: x.to_json()))

    def load_from_file(self, filepath):
        with open(filepath, 'r') as stream:
            speaker_dicts = load(stream)
        speakers = [Speaker.from_dict(s) for s in speaker_dicts]
        self.clear_speakers()
        self.load_speakers(speakers)
        self.save_starting_state()

    def load_speakers(self, speakers):
        self.speakers = [Speaker.fromspeaker(s) for s in speakers]
        self.clear_caches()

    def add_speaker(self, speaker):
        self.speakers.append(Speaker.fromspeaker(speaker))
        self.clear_caches()

    def dominant_form(self):
        if all(s.principal_weight() > 0.5 for s in self.speakers):
            return self.speakers[0].para[0][0].form_a
        if all(s.principal_weight() < 0.5 for s in self.speakers):
            return self.speakers[0].para[0][0].form_b
        return None

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
            if not self.cum_weights:
                if SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.CONSTANT:
                    inv_dist_sq = inv_dist_sq_constant
                elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.MANHATTAN:
                    inv_dist_sq = inv_dist_sq_manhattan
                elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.EUCLIDEAN:
                    inv_dist_sq = inv_dist_sq_euclidean
                else:
                    assert False
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
        assert SETTINGS.bias_threshold > 0.5
        def stable(x):
            if x.is_broadcaster:
                return True
            return abs(x.principal_weight() - 0.5) > SETTINGS.bias_threshold - 0.5
        return all(stable(s) for s in self.speakers)

    def all_biased_and_experienced(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased and experienced."""
        assert SETTINGS.bias_threshold > 0.5
        def stable(x):
            if x.is_broadcaster:
                return True
            return abs(x.principal_weight() - 0.5) > SETTINGS.bias_threshold - 0.5 and x.experience > SETTINGS.experience_threshold
        return all(stable(s) for s in self.speakers)

    def simulate_till_stable(self, batch_size=None, is_stable=all_biased_and_experienced):
        """Keep running the simulation until the stability condition is reached."""
        debug("Simulation until stable started:", time())
        max_iteration = SETTINGS.sim_max_iteration
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
            if max_iteration <= self.sim_iteration:
                self.sim_iteration = None
                return True
        debug("Simulation until stable finished:", time())
        return False
