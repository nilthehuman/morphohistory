"""See if we have simplerandom available. If not, fall back on standard random."""

from bisect import bisect

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

RAND = RNG()