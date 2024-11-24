"""Some tools for evaluating the goodness of the simulation model."""

from collections import OrderedDict
from dataclasses import dataclass
from math import log2
from typing import Dict, List, Tuple

from .agora import Agora


def _cross_entropy(truth: float, estimate: float) -> float:
    truth = min(max(truth, 0.00001), 0.99999)
    estimate = min(max(estimate, 0.00001), 0.99999)
    return -(truth * log2(estimate) + (1-truth) * log2(1-estimate))


@dataclass(frozen=True)
class BiasDataItem:
    """An entry in the observed diachronic preferences of a binary variable.
    Stores the name of a speaker, the year of the observations and the number
    of form A vs form B occurrences in the speaker's output in the given year."""
    name: str
    year: int  # redundant, but it may come in handy
    occurrences_a: int
    occurrences_b: int

    def bias(self) -> float:
        return float(self.occurrences_a) / (self.occurrences_a + self.occurrences_b)

    def total_occurrences(self) -> int:
        return self.occurrences_a + self.occurrences_b


class BiasData(OrderedDict[int, BiasDataItem]):
    """A set of year-to-year observations of a single binary linguistic variable
    in several different speakers."""
    def __init__(self, data: OrderedDict[BiasDataItem]):
        super().__init__(data)

    @classmethod
    def fromcsv(cls, csv_content: list[tuple[str, str, str, str]]):
        """Create BiasData from the cooked contents of a CSV file."""
        data_items = [ BiasDataItem(row[0], int(row[1]), int(row[2]), int(row[3])) for row in csv_content ]
        years = map(lambda x: x.year, data_items)
        by_year = [ (y, list(filter(lambda x: x.year == y, data_items))) for y in years ]
        odict = OrderedDict()
        for year in by_year:
            odict[year[0]] = year[1]
        return cls(odict)

    @classmethod
    def fromfile(cls, filename: str):
        """Create BiasData from a raw CSV file."""
        with open(filename, 'r') as fh:
            header = [ col.strip() for col in fh.readline().split(',') ]
            columns = ( header.index('name'),
                        header.index('year'),
                        header.index('occurrences_a'),
                        header.index('occurrences_b') )
            csv_content = [ tuple(line.split(',')[i] for i in columns) for line in fh.readlines() ]
            return cls.fromcsv(csv_content)

    def occurrences_in_year(self, year: int) -> int:
        return sum(item.occurrences_a + item.occurrences_b for item in self[year])

    def avg_occurrences_per_year(self) -> float:
        return sum(self.occurrences_in_year(year) for year in self.keys()) / len(self)


class EvaluatedAgora(Agora):
    """A simulated speech community whose fate is compared with the actual
    observed diachronic data."""
    def __init__(self, data: BiasData, steps_per_year=100):
        # is this necessary though?:
        super().__init__()
        self.data = data
        self.steps_per_year = steps_per_year

    def simulate(self) -> None:
        min_year = min(self.data.keys())
        max_year = max(self.data.keys())
        # measure total error or "deviance" as a sum of all years
        total_weighted_ideal_deviance = 0
        total_weighted_fifty_deviance = 0
        total_weighted_naive_deviance = 0
        total_weighted_sim_deviance = 0
        for year in range(min_year, max_year+1):
            # run a number of simulation steps
            for i in range(self.steps_per_year):
                super().simulate()
            # evaluate distance from ground truth
            try:
                data = self.data[year]
            except KeyError:
                # no data for this year apparently
                continue
            ideal_deviance_this_year = 0
            fifty_deviance_this_year = 0
            naive_deviance_this_year = 0
            sim_deviance_this_year = 0
            for item in data:
                print("author=", item.name)
                print("year=", item.year)
                try:
                    sim_speaker = list(filter(lambda s: s.name == item.name, self.state.speakers))[0]
                except IndexError:
                    # author not included in simulation
                    continue
                # calculate theoretical limit of deviance assuming perfect knowledge
                observed_bias = item.bias()
                ideal_deviance = _cross_entropy(observed_bias, observed_bias)
                ideal_deviance_this_year += ideal_deviance
                # calculate deviance according to the most naive model (i.e. all biases are always == 0.5)
                fifty_deviance = _cross_entropy(observed_bias, 0.5)
                fifty_deviance_this_year += fifty_deviance
                # calculate deviance according to the second most naive model (i.e. no change in biases ever)
                starting_speaker = [ s for s in self.starting_state.speakers if item.name == s.name ][0]
                naive_deviance = _cross_entropy(observed_bias, starting_speaker.principal_bias())
                naive_deviance_this_year += naive_deviance
                # calculate deviance according to the actual model
                sim_deviance = _cross_entropy(observed_bias, sim_speaker.principal_bias())
                sim_deviance_this_year += sim_deviance
                # DEBUG
                print("experience: ", sim_speaker.experience)
                print("observed: ", observed_bias)
                print("naive:    ", starting_speaker.principal_bias())
                print("simulated:", sim_speaker.principal_bias())
            total_weighted_ideal_deviance += ideal_deviance_this_year * self.data.occurrences_in_year(year) / self.data.avg_occurrences_per_year()
            total_weighted_fifty_deviance += fifty_deviance_this_year * self.data.occurrences_in_year(year) / self.data.avg_occurrences_per_year()
            total_weighted_naive_deviance += naive_deviance_this_year * self.data.occurrences_in_year(year) / self.data.avg_occurrences_per_year()
            total_weighted_sim_deviance   += sim_deviance_this_year   * self.data.occurrences_in_year(year) / self.data.avg_occurrences_per_year()
        print("total_weighted_ideal_deviance", total_weighted_ideal_deviance)
        print("total_weighted_fifty_deviance", total_weighted_fifty_deviance)
        print("total_weighted_naive_deviance", total_weighted_naive_deviance)
        print("total_weighted_sim_deviance", total_weighted_sim_deviance)


#### #### #### #### #### #### #### ####

bd = BiasData.fromfile('data_gerund_fonteynnini_summarized.csv')
a = EvaluatedAgora(bd)
a.load_from_file('/home/nil/fonteyn_nini_authors_studied.csv')

