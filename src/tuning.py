"""Tools to exhaustively simulate a multidimensional range of model parameter settings."""

from copy import copy
from logging import info
from os.path import isfile
from time import gmtime, strftime, perf_counter
from typing import Iterator

from .agora import Agora
from .demos import DEMO_FACTORIES
from .settings import SETTINGS


def _float_range(start: float, stop: float, step: float) -> Iterator[float]:
    """Interpolate between two values, like the standard range function.
    Attention: equality is allowed, so 'stop' is included in the range."""
    if start is None or stop is None:
        yield None
        return
    if step == 0:
        yield start
        return
    up = start <= stop
    next_val = start
    while (next_val <= stop if up else next_val >= stop):
        yield next_val
        if up:
            next_val += step
        else:
            next_val -= step

def _normalize_hungarian(string: str) -> str:
    accentless = {
                   'Á':'AA', 'á':'aa',
                   'É':'EE', 'é':'ee',
                   'Í':'II', 'í':'ii',
                   'Ó':'OO', 'ó':'oo',
                   'Ö':'OE', 'ö':'oe',
                   'Ő':'OE', 'ő':'oe',
                   'Ú':'UU', 'ú':'uu',
                   'Ü':'UE', 'ü':'ue',
                   'Ű':'UE', 'ű':'ue'
                 }
    def convert(char):
        try:
            return accentless[char]
        except KeyError:
            return char
    return ''.join(map(convert, string))


# TODO: yeah I mean this class could use a bit of a cleanup...
class Tuner:
    """The class responsible for performing the parametrized simulations
    and writing the results to file."""

    class Cancelled(StopIteration):
        pass

    class Finished(StopIteration):
        pass

    result_item = {
        'egyik_bias' : None,
        'masik_bias' : None,
        'kezdo_tapasztalat' : None,
        'belso_gyuru_sugara' : None,
        SETTINGS.paradigm.para[0][0].form_a : 0,
        SETTINGS.paradigm.para[0][0].form_b : 0,
        'egyik_sem' : 0,
        'uniform_egyensuly' : 0
    }

    # why doesn't Python have macros?
    def loop_our_bias(self) -> Iterator[float]:
        return _float_range(*self.our_bias_params)

    def loop_their_bias(self) -> Iterator[float]:
        return _float_range(*self.their_bias_params)

    def loop_starting_experience(self) -> Iterator[int]:
        return map(int, _float_range(*self.starting_experience_params))

    def loop_inner_radius(self) -> Iterator[float]:
        return _float_range(*self.inner_radius_params)

    def __init__(self, our_bias_params: tuple[float, float, float],
                       their_bias_params: tuple[float, float, float],
                       starting_experience_params: tuple[int, int, int],
                       inner_radius_params: tuple[float, float, float],
                       repetitions: int) -> None:
        """Prepare for actually performing the simulations."""
        self.our_bias_params = our_bias_params
        self.their_bias_params = their_bias_params
        self.starting_experience_params = starting_experience_params
        self.inner_radius_params = inner_radius_params
        self.repetitions = repetitions

        # man, that's a lot of setups
        self.num_total_setups = len(list(self.loop_our_bias())) * \
                                len(list(self.loop_their_bias())) * \
                                len(list(self.loop_starting_experience())) * \
                                len(list(self.loop_inner_radius()))

        # state to keep track of simulation parameters and results
        self.agora = Agora()
        self.results: list[dict] = []
        self.current_setup = 0
        self.current_rep = 0
        self.num_total_reps = 0
        self.tuning_cancelled = False
        self.our_bias_range = self.loop_our_bias()
        self.their_bias_range = self.loop_their_bias()
        self.starting_experience_range = self.loop_starting_experience()
        self.inner_radius_range = self.loop_inner_radius()
        self.our_bias = next(self.our_bias_range)
        self.their_bias = next(self.their_bias_range)
        self.starting_experience = next(self.starting_experience_range)
        self.inner_radius = next(self.inner_radius_range)

        # create the CSV file, write the header line, and we're good to go
        self.output_filename = 'results.csv'
        self.initialize_csv_file()

    def run(self) -> None:
        """Run the predefined number of repetitions for every possible model parameter setting
        in the predefined range."""
        self.on_start()
        try:
            while True:
                self.iterate_tuning()
        except self.Cancelled:
            # the tuning was cancelled by the user
            self.on_cancelled()
        except self.Finished:
            # we're done with all parameter settings
            self.on_finished()

    def on_start(self) -> None:
        """Print and save the starting time of the tuning process."""
        info("Tuning: Exhaustive simulation started at %s" % strftime("%H:%M:%S", gmtime()))
        self.start_time = perf_counter()

    def on_cancelled(self) -> None:
        """Print the time the tuning process was cancelled."""
        end_time = perf_counter()
        info("Tuning: Exhaustive simulation cancelled at %s, took %s" % \
            (strftime("%H:%M:%S", gmtime()),
             strftime("%H:%M:%S", gmtime(end_time - self.start_time))))

    def on_finished(self) -> None:
        """Print the time the tuning process was finished."""
        end_time = perf_counter()
        info("Tuning: Exhaustive simulation finished at %s, took %s" % \
            (strftime("%H:%M:%S", gmtime()),
             strftime("%H:%M:%S", gmtime(end_time - self.start_time))))

    def iterate_tuning(self) -> None:
        """Repeat the simulation several times for each parameter setup in the set of
        parameter combinations chosen by the user, then dump the results in a CSV file."""
        if self.tuning_cancelled:
            raise self.Cancelled
        # poor man's nested for loop, continued from previous call...
        # this is pretty horrifying actually, maybe we could try continuation-passing style?
        if self.current_rep == self.repetitions:
            self.current_rep = 0
            # export results to file incrementally
            self.write_new_row_to_csv_file()
            try:
                self.inner_radius = next(self.inner_radius_range)
            except StopIteration:
                self.inner_radius_range = self.loop_inner_radius()
                self.inner_radius = next(self.inner_radius_range)
                try:
                    self.starting_experience = next(self.starting_experience_range)
                except StopIteration:
                    self.starting_experience_range = self.loop_starting_experience()
                    self.starting_experience = next(self.starting_experience_range)
                    try:
                        self.their_bias = next(self.their_bias_range)
                    except StopIteration:
                        self.their_bias_range = self.loop_their_bias()
                        self.their_bias = next(self.their_bias_range)
                        try:
                            self.our_bias = next(self.our_bias_range)
                        except StopIteration:
                            # we're done, stop iterating
                            raise self.Finished
        if 0 == self.current_rep:
            self.prepare_next_setup()
        self.perform_next_rep()

    def prepare_next_setup(self) -> None:
        """Initialize Agora according to next parameter setup."""
        demo_factory = DEMO_FACTORIES[SETTINGS.current_demo]
        demo_args = DemoArguments(our_bias=self.our_bias,
                                  their_bias=self.their_bias,
                                  starting_experience=self.starting_experience,
                                  inner_radius=self.inner_radius)
        self.agora.load_demo_agora(demo_factory, demo_args)
        self.new_result = copy(self.result_item)
        self.new_result['egyik_bias'] = self.our_bias
        self.new_result['masik_bias'] = self.their_bias
        self.new_result['kezdo_tapasztalat'] = self.starting_experience
        self.new_result['belso_gyuru_sugara'] = self.inner_radius
        self.current_setup += 1
        info("Tuning: Running setup %d out of %d..." % (self.current_setup, self.num_total_setups))

    def perform_next_rep(self) -> None:
        """Perform a single simulation run for the current parameter setup."""
        self.agora.simulate_till_stable()
        dominant_form = self.agora.dominant_form()
        if dominant_form is None:
            self.new_result['egyik_sem'] += 1
        else:
            self.new_result[dominant_form] += 1
        if self.agora.uniform_balance():
            self.new_result['uniform_egyensuly'] += 1
        self.agora.quick_reset()
        self.current_rep += 1
        self.num_total_reps += 1

    def initialize_csv_file(self) -> None:
        """Create output CSV file and write the first row with the column names."""
        append_num = 0
        try:
            filename_until_dot = self.output_filename[:self.output_filename.index('.csv')]
        except ValueError:
            filename_until_dot = self.output_filename
        while isfile(self.output_filename):
            self.output_filename = filename_until_dot + str(append_num) + '.csv'
            append_num += 1
        with open(self.output_filename, 'w', encoding='utf-8') as filehandle:
            keys_normalized = [_normalize_hungarian(key) for key in self.result_item.keys()]
            csv_header = ','.join(keys_normalized)
            filehandle.write(csv_header)

    def write_new_row_to_csv_file(self) -> None:
        """Output next row of simulation results to target CSV file."""
        with open(self.output_filename, 'a', encoding='utf-8') as filehandle:
            # create CSV manually for now
            filehandle.write("\n")
            csv_row = ','.join([str(value) for value in self.new_result.values()])
            filehandle.write(csv_row)
