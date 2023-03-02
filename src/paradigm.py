"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

from abc import ABC, abstractmethod

def _clamp(value):
    return max(0., min(1., value))

class _Cell(ABC):
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    def __init__(self, bias_a=0.5, form_a='', form_b='', prominence=1.0):
        self.bias_a = bias_a
        self.form_a = form_a
        self.form_b = form_b
        if not form_a and not form_b:
            self.prominence = 0
        else:
            self.prominence = prominence

    def __bool__(self):
        return 0 != len(self.form_a)

    def __str__(self):
        if not self:
            return ''
        return "(%s, %g * \"%s\" + %g * \"%s\")" % \
            (self.get_morphosyntactic_properties(), self.bias_a, self.form_a, 1.0-self.bias_a, self.form_b)

    @abstractmethod
    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""

    def to_json(self):
        """Returns own state for JSON serialization."""
        return self.__dict__

    @staticmethod
    def from_dict(cell_dict):
        """Reconstruct cell object from an imported JSON dictionary."""
        return _NounCell(cell_dict['number'],
                         cell_dict['case'],
                         cell_dict['bias_a'],
                         cell_dict['form_a'],
                         cell_dict['form_b'],
                         cell_dict['prominence'])

    def to_str_short(self):
        if 0 == len(self.form_a):
            return ''
        return "%g*\"%s\" + %g*\"%s\"" % \
            (self.bias_a, self.form_a, 1.0-self.bias_a, self.form_b)

class _Paradigm(ABC):
    """A 2D or 5D matrix of competing noun of verb forms for given morphosyntactic contexts."""
    # pylint: disable=no-member

    def __getitem__(self, index):
        """Return a row of cells (assignable)."""
        return self.para[index]

    def __str__(self):
        def descend(cells):
            if not isinstance(cells, list):
                return str(cells)
            below = [descend(c) for c in cells]
            below = filter(lambda cells: bool(len(cells)), below)
            return '[' + ', '.join(below) + ']'
        return descend(self.para)

    @staticmethod
    @abstractmethod
    def morphosyntactic_properties(i, j):
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""

    @abstractmethod
    def nudge(self, amount, i, j):
        """Adjust the weights in a single cell."""

    @abstractmethod
    def propagate(self, amount, i, j):
        """Spread a weight change down each dimension in the paradigm."""

    def to_json(self):
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

    @staticmethod
    def from_dict(para_dict):
        assert list(para_dict.keys()) == ['para']
        para_list = para_dict['para']
        new_para = NounParadigm()
        assert len(para_list) <= 2
        while para_list:
            list_below = para_list.pop(0)
            assert len(list_below) <= 13
            while list_below:
                cell = _Cell.from_dict(list_below.pop(0))
                new_para.para[cell.number][cell.case] = cell
        return new_para

    def passive_decay(self):
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
    def __init__(self, number=0, case=0, bias_a=0.5, form_a='', form_b='', prominence=1.0):
        super().__init__(bias_a, form_a, form_b, prominence)
        self.number = number
        self.case = case

    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""
        return NounParadigm.morphosyntactic_properties(self.number, self.case)

class _VerbCell(_Cell):
    """A single cell in a verb paradigm for a given morphosyntactic context."""
    def __init__(self, person=0, number=0, defness=0, tense=0, mood=0, bias_a=0.5, form_a='', form_b='', prominence=1.0):
        super().__init__(bias_a, form_a, form_b, prominence)
        self.person = person
        self.number = number
        self.defness = defness
        self.tense = tense
        self.mood = mood

    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""
        return VerbParadigm.morphosyntactic_properties(self.person, self.number, self.defness, self.tense, self.mood)

class NounParadigm(_Paradigm):
    """A 2D matrix representing the competing forms of a single noun.
       Hungarian nouns inflect for number and case."""
    def __init__(self, bias_a=0.5, form_a='', form_b=''):
        self.para = [[_NounCell(i, j, bias_a) for j in range(13)] for i in range(2)]
        self.para[0][0].form_a = form_a
        self.para[0][0].form_b = form_b
        self.para[0][0].prominence = 1.0

    @staticmethod
    def morphosyntactic_properties(i, j):
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        assert i < 2 and j < 13
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
        return "{%s, %s}" % (numbers[i], cases[j])

    def nudge(self, amount, i, j):
        """Adjust the weights in a single cell."""
        assert -1 <= amount <= 1
        assert i < 2 and j < 13
        self.para[i][j].bias_a = _clamp(self.para[i][j].bias_a + amount)

    def propagate(self, amount, i, j):
        """Spread a weight change down each dimension in the paradigm."""
        delta = _clamp(self.para[i][j].prominence * amount)
        for self_i in range(2):
            if self_i != i:
                self.nudge(delta, self_i, j)
        for self_j in range(13):
            if self_j != j:
                self.nudge(delta, i, self_j)

class VerbParadigm(_Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self, bias_a=0.5):
        self.para = [[[[[_VerbCell(i, j, k, l, m, bias_a) for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]

    @staticmethod
    def morphosyntactic_properties(i, j, k, l, m):
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

    def nudge(self, amount, i, j, k, l, m):
        """Adjust the weights in a single cell."""
        assert 0 <= amount <= 1
        assert i < 3 and j < 2 and k < 2 and l < 2 and m < 3
        self.para[i][j][k].bias_a = _clamp(self.para[i][j][k][l][m].bias_a + amount)

    def propagate(self, amount, i, j, k, l, m):
        """Spread a weight change down each dimension in the paradigm."""
        delta = _clamp(self.para[i][j][k][l][m].prominence * amount)
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
