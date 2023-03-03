"""An evolving virtual community of speakers influencing each other stochastically."""

from copy import deepcopy
from dataclasses import dataclass, field
from itertools import product
from json import dumps, load
from logging import debug, info
from typing import List

from .rng import RAND
from .settings import SETTINGS
from .speaker import Speaker

def _inv_dist_sq_constant(_):
    return 1

def _inv_dist_sq_manhattan(pair):
    speaker = pair['speaker']
    hearer = pair['hearer']
    dist_sq = (abs(speaker.pos[0] - hearer.pos[0]) + abs(speaker.pos[1] - hearer.pos[1])) ** 2
    return 1 / dist_sq

def _inv_dist_sq_euclidean(pair):
    speaker = pair['speaker']
    hearer = pair['hearer']
    dist_sq = (speaker.pos[0] - hearer.pos[0]) ** 2 + (speaker.pos[1] - hearer.pos[1]) ** 2
    return 1 / dist_sq

class Agora:
    """A collection of simulated speakers influencing each other."""

    @dataclass
    class AgoraState:
        """The essential variables that define the current state of an Agora."""
        speakers: List[Speaker] = field(default_factory=lambda: [])
        sim_iteration_total: int = 0

        def to_json(self):
            """Returns own state for JSON serialization."""
            return self.__dict__

    def __init__(self):
        self.state = self.AgoraState()
        self.starting_state = None
        self.clear_caches()
        self.sim_iteration = None
        self.sim_cancelled = False
        self.graphics_on = False
        self.speaker_pairs = None
        self.cum_weights = None
        self.pick = None
        self.pick_queue = []

    def save_starting_state(self):
        """Stash a snapshot of the current state of the Agora."""
        self.starting_state = self.AgoraState()
        # N.B. paradigms are deep copied by Speaker.fromspeaker
        self.starting_state.speakers = [Speaker.fromspeaker(s) for s in self.state.speakers]
        self.starting_state.sim_iteration_total = self.state.sim_iteration_total

    def reset(self):
        """Restore earlier speaker snapshot."""
        self.clear_speakers()
        self.load_speakers(self.starting_state.speakers)
        self.state.sim_iteration_total = self.starting_state.sim_iteration_total

    def quick_reset(self):
        """Keep speakers but reset their biases and experience."""
        # FIXME: pair speakers based on their identifier 'n', not their raw index
        for i in range(len(self.state.speakers)):
            self.state.speakers[i].para = deepcopy(self.starting_state.speakers[i].para)
            self.state.speakers[i].experience = self.starting_state.speakers[i].experience
        # keep valuable caches (pick_queue still needs to be cleared though)
        self.pick_queue = []
        self.state.sim_iteration_total = self.starting_state.sim_iteration_total

    def clear_caches(self):
        """Invalidate cache variables."""
        # variables for expensive calculations
        self.speaker_pairs = None
        self.cum_weights = None
        self.pick_queue = []

    def clear_dist_cache(self):
        """Invalidate weights cache used for picking pairs."""
        self.cum_weights = None

    def clear_speakers(self):
        """Remove all speakers from the Agora."""
        self.state.speakers = []
        self.state.sim_iteration_total = 0
        self.clear_caches()

    def load_demo_agora(self, demo_factory, our_bias=None, their_bias=None,
        starting_experience=SETTINGS.starting_experience, inner_radius=None):
        """Replace current speaker community with a demo preset."""
        if our_bias is None and their_bias is None:
            # fall back on the default arguments
            speakers = demo_factory.get_speakers(starting_experience=starting_experience)
        else:
            speakers = demo_factory.get_speakers(our_bias, their_bias, starting_experience, inner_radius)
        self.clear_speakers()
        self.load_speakers(speakers)
        self.save_starting_state()

    def save_to_file(self, filepath):
        """Write current state to disk."""
        with open(filepath, 'w', encoding='utf-8') as stream:
            stream.write(dumps(self.state, indent=1, default=lambda x: x.to_json()))

    def load_from_file(self, filepath):
        """Restore an Agora state previously written to file."""
        with open(filepath, 'r', encoding='utf-8') as stream:
            loaded_state = load(stream)
        speakers = [Speaker.from_dict(s) for s in loaded_state['speakers']]
        self.clear_speakers()
        self.load_speakers(speakers)
        self.state.sim_iteration_total = loaded_state['sim_iteration_total']
        self.save_starting_state()
        SETTINGS.paradigm = deepcopy(self.state.speakers[0].para)

    def load_speakers(self, speakers):
        """Replace current speaker community with a copy of the argument."""
        self.state.speakers = [Speaker.fromspeaker(s) for s in speakers]
        assert not all(s.is_broadcaster for s in self.state.speakers)
        self.clear_caches()

    def add_speaker(self, speaker):
        """Add a virtual speaker to the simulated community."""
        self.state.speakers.append(Speaker.fromspeaker(speaker))
        self.clear_caches()

    def set_paradigm(self, para):
        """Update the exact forms and prominence values in all cells of all
        speakers' (redundantly stored) paradigms based on the values in para."""
        for speaker in self.state.speakers:
            for num in range(0, 2):
                for case in range(0, 13):
                    speaker.para.para[num][case].form_a = para.para[num][case].form_a
                    speaker.para.para[num][case].form_b = para.para[num][case].form_b
                    speaker.para.para[num][case].prominence = para.para[num][case].prominence

    def set_starting_experience(self, experience=None):
        """Set the experience value of each speaker in the saved snapshot,
        and also in the current state if it's identical to the snapshot."""
        # FIXME: defining a default argument value for experience failed for some reason
        if experience is None:
            experience = SETTINGS.starting_experience
        for speaker in self.starting_state.speakers:
            speaker.experience = experience
        if 0 == self.state.sim_iteration_total:
            for speaker in self.state.speakers:
                speaker.experience = experience

    def passive_decay(self):
        for speaker in self.state.speakers:
            current_picks = []
            if self.pick:
                current_picks += [self.pick['speaker'].n, self.pick['hearer'].n]
            for pick in self.pick_queue:
                current_picks += [pick['speaker'].n, pick['hearer'].n]
            if speaker.n not in current_picks:
                speaker.passive_decay()
        # TODO move to sim.py
        if self.graphics_on:
            self.update_speakerdot_colors()

    def dominant_form(self):
        if all(s.principal_bias() > 0.5 for s in self.state.speakers):
            return self.state.speakers[0].para[0][0].form_a
        if all(s.principal_bias() < 0.5 for s in self.state.speakers):
            return self.state.speakers[0].para[0][0].form_b
        return None

    def uniform_balance(self):
        """Detect a situation where no speaker is strongly biased either way."""
        return all(1 - SETTINGS.bias_threshold < s.principal_bias() < SETTINGS.bias_threshold
                   for s in self.state.speakers)

    def simulate(self, *_): # TODO: use threading to perform independent picks in parallel
        """Perform one iteration: pick two individuals to talk to each other
        and update the hearer's state based on the speaker's."""
        debug("Agora: Iterating simulation...")
        if self.pick_queue:
            # either the second half of a mutual exchange, or a broadcaster's picks
            self.pick = self.pick_queue.pop(0)
        else:
            if not self.speaker_pairs:
                self.speaker_pairs = list({'speaker': s, 'hearer': h} for (s, h) in product(self.state.speakers, self.state.speakers) if s != h)
            if not self.cum_weights:
                if SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.CONSTANT:
                    inv_dist_sq = _inv_dist_sq_constant
                elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.MANHATTAN:
                    inv_dist_sq = _inv_dist_sq_manhattan
                elif SETTINGS.sim_distance_metric == SETTINGS.DistanceMetric.EUCLIDEAN:
                    inv_dist_sq = _inv_dist_sq_euclidean
                else:
                    assert False
                self.cum_weights = [0]
                for pair in self.speaker_pairs:
                    self.cum_weights.append(inv_dist_sq(pair) + self.cum_weights[-1])
                self.cum_weights.pop(0)
            while True:
                self.pick = RAND.choices(self.speaker_pairs, cum_weights=self.cum_weights)[0]
                if not self.pick['hearer'].is_broadcaster:
                    break
            if self.pick['speaker'].is_broadcaster:
                s = self.pick['speaker']
                self.pick_queue = [ {'speaker': s, 'hearer': h} for h in self.state.speakers if h != s ]
                self.pick = self.pick_queue.pop(0)
            elif SETTINGS.sim_influence_mutual:
                reverse_pick = {'speaker': self.pick['hearer'], 'hearer': self.pick['speaker']}
                self.pick_queue.append(reverse_pick)
        debug("Agora: %d picked to talk to %d" % (self.pick['speaker'].n, self.pick['hearer'].n))
        self.pick['speaker'].talk(self.pick)
        if SETTINGS.sim_passive_decay:
            self.passive_decay()
        self.state.sim_iteration_total += 1

    def all_biased(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased."""
        assert SETTINGS.bias_threshold >= 0.5
        def stable(speaker):
            if speaker.is_broadcaster:
                return True
            bias_enough = abs(speaker.principal_bias() - 0.5) > SETTINGS.bias_threshold - 0.5
            return bias_enough
        return all(stable(s) for s in self.state.speakers)

    def all_biased_and_experienced(self):
        """Criterion to stop the simulation: every speaker is sufficiently biased and experienced."""
        assert SETTINGS.bias_threshold >= 0.5
        def stable(speaker):
            if speaker.is_broadcaster:
                return True
            bias_enough = abs(speaker.principal_bias() - 0.5) > SETTINGS.bias_threshold - 0.5
            experience_enough = speaker.experience > SETTINGS.experience_threshold
            return bias_enough and experience_enough
        return all(stable(s) for s in self.state.speakers)

    def simulate_till_stable(self, batch_size=None, is_stable=all_biased_and_experienced):
        """Keep running the simulation until the stability condition is reached."""
        max_iteration = SETTINGS.sim_max_iteration
        if not self.sim_iteration:
            self.sim_iteration = 0
            info("Agora: Simulation until stable started.")
        until = self.sim_iteration + batch_size + 1 if batch_size else max_iteration + 1
        for self.sim_iteration in range(self.sim_iteration + 1, until):
            if self.sim_cancelled:
                self.sim_cancelled = False
                self.sim_iteration = None
                info("Agora: Simulation until stable cancelled.")
                return True
            if is_stable and is_stable(self):
                info("Agora: Simulation until stable finished (stability reached after %d iterations)." % self.sim_iteration)
                self.sim_iteration = None
                return True
            self.simulate()
            # Make sure we stop eventually no matter what
            if max_iteration <= self.sim_iteration:
                self.sim_iteration = None
                info("Agora: Simulation until stable finished (max iteration reached).")
                return True
        return False
