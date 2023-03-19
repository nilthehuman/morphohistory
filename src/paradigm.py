"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

from abc import ABC, abstractmethod
from itertools import chain
from typing import Iterator, overload, Self, Union

def _clamp(value: float) -> float:
    return max(0., min(1., value))

class _NounCellIndex(tuple[int, int]):
    """Identifies a single NounParadigm entry: a tuple of two non-negative integers."""
    def __new__(cls, number: int=0, case: int=0) -> Self:
        assert number >= 0 and case >= 0
        assert number < 2 and case < 13
        new_cell_index = super().__new__(cls, (number, case))
        return new_cell_index

#class _VerbCellIndex(tuple[int, int]):
#    """Identifies a single VerbParadigm entry: a tuple of five non-negative integers."""
#    def __new__(cls, person: int, number: int, defness: int, tense: int, mood: int) -> Self:
#        assert person >= 0 and number >= 0 and defness >= 0 and tense >= 0 and mood >= 0
#        assert person < 3 and number < 2 and defness < 2 and tense < 2 and mood < 3
#        new_cell_index = super().__new__(cls, (person, number, defness, tense, mood))
#        return new_cell_index

CellIndex = _NounCellIndex
#CellIndex = Union[_NounCellIndex, _VerbCellIndex]

class _Cell(ABC):
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    # TODO: disallow empty forms
    def __init__(self, bias_a: float=0.5, form_a: str='', form_b: str='', prominence: float=1.0) -> None:
        self.bias_a = bias_a
        self.form_a = form_a
        self.form_b = form_b
        if not form_a and not form_b:
            self.prominence = 0.0
        else:
            self.prominence = prominence

    def __bool__(self) -> bool:
        return 0 != len(self.form_a)

    def __str__(self) -> str:
        if not self:
            return ''
        return "(%s, %g * \"%s\" + %g * \"%s\")" % \
            (self.get_morphosyntactic_properties(), self.bias_a, self.form_a, 1.0-self.bias_a, self.form_b)

    @abstractmethod
    def get_morphosyntactic_properties(self) -> str:
        """Returns a string listing the cell's features."""

    def to_dict(self):
        """Returns own state for JSON serialization."""
        return self.__dict__

    @classmethod
    @abstractmethod
    def from_dict(cls, cell_dict) -> Self:
        """Construct cell object from an imported JSON dictionary."""

    def to_str_short(self) -> str:
        if 0 == len(self.form_a):
            return ''
        return "%g*\"%s\" + %g*\"%s\"" % \
            (self.bias_a, self.form_a, 1.0-self.bias_a, self.form_b)

    def nudge(self, delta: float) -> None:
        """Shift bias by the given amount."""
        assert -1 <= delta <= 1
        self.bias_a = _clamp(self.bias_a + delta)

class _Paradigm(ABC):
    """A 2D or 5D matrix of competing noun of verb forms for given morphosyntactic contexts."""
    # pylint: disable=no-member

    @overload
    def __getitem__(self, index: CellIndex) -> _Cell:
        pass

    @overload
    def __getitem__(self, index: int) -> list[_Cell]:
        pass

    @abstractmethod
    def __getitem__(self, index: Union[CellIndex, int]) -> Union[_Cell, list[_Cell]]:
        """Return a row of cells or a specific cell (assignable)."""

    def __str__(self) -> str:
        def descend(cells):
            if not isinstance(cells, list):
                return str(cells)
            below = [descend(c) for c in cells]
            below = filter(lambda cells: bool(len(cells)), below)
            return '[' + ', '.join(below) + ']'
        return descend(self.para)

    def __iter__(self) -> Iterator[_Cell]:
        """Return an iterator that will loop through our cells in order."""
        para_flattened = self.para
        while True:
            try:
                para_flattened = list(chain.from_iterable(para_flattened))
            except TypeError:
                break
        return para_flattened.__iter__()

    @staticmethod
    @abstractmethod
    def morphosyntactic_properties(index: CellIndex) -> str:
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""

    @abstractmethod
    def nudge(self, delta: float, index: CellIndex) -> None:
        """Adjust the weights in a single cell."""

    @abstractmethod
    def propagate(self, delta: float, index: CellIndex) -> None:
        """Spread a weight change down each dimension in the paradigm."""

    @abstractmethod
    def to_dict(self):
        """Returns own state for JSON serialization."""

    @classmethod
    @abstractmethod
    def from_dict(cls, para_dict) -> Self:
        """Construct paradigm object from an imported JSON dictionary."""

    def passive_decay(self) -> None:
        """Gradually forget underdog variants in each cell."""
        # TODO: optimize this if possible
        def descend(cells):
            if isinstance(cells, list):
                for below in cells:
                    descend(below)
            else:
                cell = cells
                if cell.bias_a > 0.5:
                    cell.bias_a *= 1.02
                elif cell.bias_a < 0.5:
                    cell.bias_a /= 1.02
                cell.bias_a = _clamp(cell.bias_a)
                return
        descend(self.para)

class _NounCell(_Cell):
    """A single cell in a noun paradigm for a given morphosyntactic context."""
    def __init__(self, number: int=0, case: int=0, bias_a: float=0.5, form_a: str='', form_b: str='', prominence: float=1.0) -> None:
        super().__init__(bias_a, form_a, form_b, prominence)
        self.number = number
        self.case = case

    @classmethod
    def from_dict(cls, cell_dict) -> Self:
        """Construct NounCell object from an imported JSON dictionary."""
        return cls(cell_dict['number'],
                   cell_dict['case'],
                   cell_dict['bias_a'],
                   cell_dict['form_a'],
                   cell_dict['form_b'],
                   cell_dict['prominence'])

    def get_morphosyntactic_properties(self) -> str:
        """Returns a string listing the cell's features."""
        return NounParadigm.morphosyntactic_properties(CellIndex(self.number, self.case))

class _VerbCell(_Cell):
    """A single cell in a verb paradigm for a given morphosyntactic context."""
    def __init__(self, person: int=0, number: int=0, defness: int=0, tense: int=0, mood: int=0, bias_a: float=0.5,
                 form_a: str='', form_b: str='', prominence: float=1.0) -> None:
        super().__init__(bias_a, form_a, form_b, prominence)
        self.person = person
        self.number = number
        self.defness = defness
        self.tense = tense
        self.mood = mood

    @classmethod
    def from_dict(cls, cell_dict) -> Self:
        """Construct VerbCell object from an imported JSON dictionary."""
        return cls(cell_dict['person'],
                   cell_dict['number'],
                   cell_dict['defness'],
                   cell_dict['tense'],
                   cell_dict['mood'],
                   cell_dict['bias_a'],
                   cell_dict['form_a'],
                   cell_dict['form_b'],
                   cell_dict['prominence'])

    def get_morphosyntactic_properties(self) -> str:
        """Returns a string listing the cell's features."""
        return VerbParadigm.morphosyntactic_properties(self.person, self.number, self.defness, self.tense, self.mood)

class NounParadigm(_Paradigm):
    """A 2D matrix representing the competing forms of a single noun.
       Hungarian nouns inflect for number and case."""
    def __init__(self, bias_a: float=0.5, form_a: str='', form_b: str='') -> None:
        self.para = [[_NounCell(i, j, bias_a) for j in range(13)] for i in range(2)]
        self.para[0][0].form_a = form_a
        self.para[0][0].form_b = form_b
        self.para[0][0].prominence = 1.0

    @classmethod
    def from_dict(cls, para_dict) -> Self:
        """Construct paradigm object from an imported JSON dictionary."""
        assert list(para_dict.keys()) == ['para']
        para_list = para_dict['para']
        new_para = cls()
        assert len(para_list) <= 2
        while para_list:
            list_below = para_list.pop(0)
            assert len(list_below) <= 13
            while list_below:
                cell = _NounCell.from_dict(list_below.pop(0))
                new_para.para[cell.number][cell.case] = cell
        return new_para

    def to_dict(self):
        """Returns own state for JSON serialization."""
        # output non-empty cells only to save space
        dense_para = []
        assert len(self.para) <= 2
        for num in self.para:
            assert len(num) <= 13
            dense_para.append([])
            for cell in num:
                if cell:
                    dense_para[-1].append(cell)
        my_dict = { 'para': dense_para }
        return my_dict

    @overload
    def __getitem__(self, index: CellIndex) -> _Cell:
        pass

    @overload
    def __getitem__(self, index: int) -> list[_Cell]:
        pass

    def __getitem__(self, index: Union[CellIndex, int]) -> Union[_Cell, list[_Cell]]:
        """Return a row of cells or a specific cell (assignable)."""
        if isinstance(index, CellIndex):
            num = index[0]
            cas = index[1]
            return self.para[num][cas]
        elif isinstance(index, int):
            return self.para[index]
        else:
            raise TypeError

    @staticmethod
    def morphosyntactic_properties(index: CellIndex) -> str:
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        num = index[0]
        cas = index[1]
        numbers = {
            0 : 'sg',
            1 : 'pl'
        }
        cases = {
            0 : 'acc',
            1 : 'dat',
            2 : 'ins',
            3 : 'transl',
            4 : 'ine',
            5 : 'supe',
            6 : 'ade',
            7 : 'ill',
            8 : 'subl',
            9 : 'all',
           10 : 'ela',
           11 : 'del',
           12 : 'abl'
        }
        return "{%s, %s}" % (numbers[num], cases[cas])

    def nudge(self, delta: float, index: CellIndex) -> None:
        """Adjust the weights in a single cell."""
        num = index[0]
        cas = index[1]
        self.para[num][cas].nudge(delta)

    def propagate(self, delta: float, index: CellIndex) -> None:
        """Spread a weight change down each dimension in the paradigm."""
        num = index[0]
        cas = index[1]
        delta = _clamp(self.para[num][cas].prominence * delta)
        for own_num in range(2):
            if own_num != num:
                self.nudge(delta, CellIndex(own_num, cas))
        for own_cas in range(13):
            if own_cas != cas:
                self.nudge(delta, CellIndex(num, own_cas))

class VerbParadigm(_Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self, bias_a: float=0.5) -> None:
        self.para = [[[[[_VerbCell(i, j, k, l, m, bias_a) for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]

    @staticmethod
    def morphosyntactic_properties(i, j, k, l, m) -> str:
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        assert i < 3 and j < 2 and k < 2 and l < 2 and m < 3
        persons = {
            0 : '1',
            1 : '2',
            2 : '3'
        }
        numbers = {
            0 : 'sg',
            1 : 'pl'
        }
        defnesses = {
            0 : 'def',
            1 : 'indef'
        }
        tenses = {
            0 : 'pres',
            1 : 'past'
        }
        moods = {
            0 : 'ind',
            1 : 'cond',
            2 : 'subj'
        }
        return "{%s, %s, %s, %s, %s}" % (persons[i], numbers[j], defnesses[k], tenses[l], moods[m])

    def nudge(self, delta: float, i: int, j: int, k: int, l: int, m: int) -> None:

        """Adjust the weights in a single cell."""
        assert i < 3 and j < 2 and k < 2 and l < 2 and m < 3
        self.para[i][j][k][l][m].nudge(delta)

    def propagate(self, delta: float, i: int, j: int, k: int, l: int, m: int) -> None:
        """Spread a weight change down each dimension in the paradigm."""
        delta = _clamp(self.para[i][j][k][l][m].prominence * delta)
        for self_i in range(3):
            if self_i != i:
                self.nudge(delta, self_i, j, k, l, m)
        for self_j in range(2):
            if self_j != j:
                self.nudge(delta, i, self_j, k, l, m)
        for self_k in range(2):
            if self_k != k:
                self.nudge(delta, i, j, self_k, l, m)
        for self_l in range(2):
            if self_l != l:
                self.nudge(delta, i, j, k, self_l, m)
        for self_m in range(3):
            if self_m != m:
                self.nudge(delta, i, j, k, l, self_m)
