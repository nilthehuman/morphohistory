"""See if we have simplerandom available. If not, fall back on standard random."""
from typing import TypeVar

T = TypeVar('T')

# TODO: see if numpy is much faster (buffering a lot of random numbers ahead of time)

try:
    from simplerandom.iterators import MWC1
    from bisect import bisect

    class _RNG:
        def __init__(self, random_seed: int) -> None:
            self.mwc = MWC1(random_seed)

        def next(self) -> int:
            return next(self.mwc)

        def choices(self, population: list[T], cum_weights: list[float]) -> list[T]:
            assert len(population) == len(cum_weights)
            scale = cum_weights[-1] + 0.0
            random = next(self.mwc) / 2**32
            # copied this trick from the original Lib/random.py
            return [population[bisect(cum_weights, random * scale, 0, len(population) - 1)]]
except ImportError:
    from random import choices, randrange, seed

    class _RNG:
        def __init__(self, random_seed: int) -> None:
            seed(random_seed)

        def next(self) -> int:
            return randrange(2**32)

        def choices(self, population: list[T], cum_weights: list[float]) -> list[T]:
            return choices(population, cum_weights=cum_weights)


# random seed courtesy of Lia & Bella
_LIA_BELLA_MD5 = 0xae10de48e999b5ba913ac8cd5cc32155
RAND = _RNG(_LIA_BELLA_MD5)
