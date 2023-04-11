"""Bare-bones simulated speakers that use one-word sentences to interact with each other."""

from copy import deepcopy
from logging import debug

from .paradigm import CellIndex, NounParadigm
from .rng import RAND
from .settings import SETTINGS
from typing import Optional, Self, TypedDict

class Speaker:
    """A simulated individual within the speaking community."""
    def __init__(self, n: int, pos: tuple[float, float], para: NounParadigm,
                 experience: int=SETTINGS.starting_experience, is_broadcaster: bool=False) -> None:
        self.n = n
        self.pos = pos
        self.para = para
        self.experience = experience
        self.is_broadcaster = is_broadcaster
        self.principal_bias_cached = None

    @classmethod
    def fromspeaker(cls, speaker: Self) -> Self:
        """Copy an existing Speaker."""
        new_speaker = cls(speaker.n, speaker.pos, deepcopy(speaker.para),
                          speaker.experience, speaker.is_broadcaster)
        return new_speaker

    @classmethod
    def frombias(cls, n: int, pos: tuple[float, float], bias_a: float,
                 experience: int=SETTINGS.starting_experience, is_broadcaster: bool=False) -> Self:
        """Construct a Speaker from a single bias value."""
        assert SETTINGS.paradigm.para is not None
        if SETTINGS.sim_single_cell:
            para = NounParadigm(bias_a=bias_a, form_a=SETTINGS.paradigm.para[0][0].form_a,
                                               form_b=SETTINGS.paradigm.para[0][0].form_b)
        else:
            para = deepcopy(SETTINGS.paradigm)
            for cell in para:
                cell.bias_a = bias_a
        new_speaker = cls(n, pos, para, experience, is_broadcaster)
        return new_speaker

    def to_dict(self):
        """Export object contents for JSON serialization."""
        speaker_only = Speaker.fromspeaker(self)
        speaker_dict = speaker_only.__dict__
        del speaker_dict['principal_bias_cached']
        return speaker_dict

    @classmethod
    def from_dict(cls, speaker_dict) -> Self:
        """Construct Speaker object from an imported JSON dictionary."""
        para = NounParadigm.from_dict(speaker_dict['para'])
        return cls(speaker_dict['n'],
                   speaker_dict['pos'],
                   para,
                   speaker_dict['experience'],
                   speaker_dict['is_broadcaster'])

    def principal_bias(self, force_update: bool=False) -> float:
        """Which way the speaker is leaning, summed up in a single float."""
        if not force_update and self.principal_bias_cached is not None:
            return self.principal_bias_cached
        sum_bias = 0
        sum_prominence = 0
        for cell in self.para:
            if cell.alternates():
                sum_bias += cell.bias_a * cell.prominence
                sum_prominence += cell.prominence
        self.principal_bias_cached = sum_bias / sum_prominence
        return self.principal_bias_cached

    def uniform_paradigm(self, strong=False) -> bool:
        """Is the speaker consistently biased towards the same kind of alternants?"""
        if strong:
            assert SETTINGS.bias_threshold >= 0.5
            threshold = SETTINGS.bias_threshold
        else:
            threshold = 0.5
        if SETTINGS.sim_single_cell:
            main_cell = self.para[CellIndex()]
            if not main_cell.alternates():
                # no bias possible at all
                return False
            uniformly_a = main_cell.bias_a >     threshold
            uniformly_b = main_cell.bias_a < 1 - threshold
        else:
            uniformly_a = all(cell.bias_a >     threshold for cell in self.para if cell.alternates())
            uniformly_b = all(cell.bias_a < 1 - threshold for cell in self.para if cell.alternates())
        return uniformly_a or uniformly_b

    def name_tag(self) -> str:
        """Text to display next to SpeakerDot label on mouse hover."""
        for main_cell in self.para:
            if main_cell.alternates():
                break
        bias = self.principal_bias()
        form_a = main_cell.form_a
        form_b = main_cell.form_b
        return "%g*\"%s\" + %g*\"%s\"; xp:%d" % (bias, form_a, 1-bias, form_b, self.experience)

    def talk(self, pick: 'PairPick') -> tuple[CellIndex, bool]:
        """Interact with and influence another Speaker in the Agora."""
        assert pick['speaker'] == self
        hearer = pick['hearer']
        assert not hearer.is_broadcaster # broadcasters are deaf
        index = CellIndex()
        if not SETTINGS.sim_single_cell:
            # pick a non-empty cell to share with the hearer
            while True:
                index = CellIndex(RAND.next() % 2, RAND.next() % 14)
                if self.para[index].form_a:
                    break
        cum_weights = [self.para[index].bias_a, 1]
        form_a_used = RAND.choices([True, False], cum_weights=cum_weights)[0]
        if SETTINGS.sim_prefer_opposite:
            form_a_used = not form_a_used
        hearer.hear_noun(index, form_a_used)
        if SETTINGS.sim_influence_self:
            self.hear_noun(index, form_a_used)
        return index, form_a_used  # let the Agora know which form of which cell we used

    def hear_noun(self, index: CellIndex, form_a_used: bool) -> None:
        """Accept a given form from another Speaker and adjust own bias based on it."""
        form = self.para[index].form_a if form_a_used else self.para[index].form_b
        debug("Speaker: I just heard '%s'" % form)
        if not self.para[index].alternates():
            # impossible to tell which kind of form we got
            return
        learning_model_funcs = {
            SETTINGS.LearningModel.HARMONIC    : self._hear_noun_harmonic,
            SETTINGS.LearningModel.RW          : self._hear_noun_rw_vanilla,
            SETTINGS.LearningModel.RW_WEIGHTED : self._hear_noun_rw_weighted
        }
        learning_model_funcs[SETTINGS.sim_learning_model](index, form_a_used)
        self.experience = self.experience + 1
        self.principal_bias_cached = None

    def _hear_noun_harmonic(self, index: CellIndex, form_a_used: bool) -> None:
        """The n'th interaction has +-1/n impact on the exact cell's bias."""
        delta = (1 if form_a_used else -1) / (self.experience + 1)
        self.para.nudge(delta, index)
        self.para.propagate(delta, index)

    def _hear_noun_rw_vanilla(self, index: CellIndex, form_a_used: bool) -> None:
        """Vanilla implementation of the Rescorla-Wagner learning model.
        All cells containing a substring of the string just heard are assumed to be activated."""
        cell_used = self.para[index]
        form = cell_used.form_a if form_a_used else cell_used.form_b
        if SETTINGS.sim_single_cell:
            assert index == CellIndex()
            activated_cells = [cell_used]
        else:
            activated = lambda c: c.alternates() and (form.startswith(c.form_a) or form.startswith(c.form_b))
            activated_cells = [cell for cell in self.para if activated(cell)]
        lambda_ = 1  # maximum conditioning (in a single cell)
        v_max = lambda_ * len(activated_cells)
        # total weight of associations
        v_total = sum(cell.bias_a - (1 - cell.bias_a) for cell in activated_cells) / v_max
        # adjust affected cells only
        for cell in activated_cells:
            alpha = cell.prominence       # salience of conditioned stimulus
            beta  = cell_used.prominence  # salience of unconditioned stimulus
            surprise = lambda_ * (1 if form_a_used else -1) - v_total
            delta_v = SETTINGS.sim_rw_default_rate * alpha * beta * surprise
            cell.nudge(0.5 * delta_v)  # [-1,1] scaled to [0,1]

    def _hear_noun_rw_weighted(self, index: CellIndex, form_a_used: bool) -> None:
        """Tweaked implementation of the Rescorla-Wagner learning model where v_total is weighted
        according to the salience (prominence) of each conditioned stimulus."""
        cell_used = self.para[index]
        form = cell_used.form_a if form_a_used else cell_used.form_b
        if SETTINGS.sim_single_cell:
            assert index == CellIndex()
            activated_cells = [cell_used]
        else:
            activated = lambda c: c.alternates() and (form.startswith(c.form_a) or form.startswith(c.form_b))
            activated_cells = [cell for cell in self.para if activated(cell)]
        lambda_ = 1  # maximum conditioning (in a single cell)
        v_max = lambda_ * len(activated_cells)
        # total weight of associations
        v_total = sum((cell.bias_a - (1 - cell.bias_a)) * cell.prominence for cell in activated_cells) / v_max
        # adjust affected cells only
        for cell in activated_cells:
            alpha   = cell.prominence       # salience of conditioned stimulus
            beta    = cell_used.prominence  # salience of unconditioned stimulus
            surprise = lambda_ * (1 if form_a_used else -1) - v_total
            delta_v = SETTINGS.sim_rw_default_rate * alpha * beta * surprise
            cell.nudge(0.5 * delta_v)  # [-1,1] scaled to [0,1]

    def passive_decay(self) -> None:
        """Tilt all biases slightly in favor of the preferred form, fading the opposite form."""
        self.para.passive_decay()


class PairPick(TypedDict):
    speaker: Speaker
    hearer : Speaker
