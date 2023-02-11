"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

from abc import ABC, abstractmethod

def clamp(x):
    return max(0., min(1., x))

class Cell(ABC):
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    def __init__(self, weight_a=0.5, form_a='', form_b='', importance=1.0):
        self.weight_a = weight_a
        self.form_a = form_a
        self.form_b = form_b
        if not form_a and not form_b:
            self.importance = 0
        else:
            self.importance = importance

    def __bool__(self):
        return 0 != len(self.form_a)

    def __str__(self):
        if not self:
            return ''
        return "(%s, %g * \"%s\" + %g * \"%s\")" % \
            (self.get_morphosyntactic_properties(), self.weight_a, self.form_a, 1.0-self.weight_a, self.form_b)

    @abstractmethod
    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_dict(cell_dict):
        return NounCell(cell_dict['number'],
                        cell_dict['case'],
                        cell_dict['weight_a'],
                        cell_dict['form_a'],
                        cell_dict['form_b'],
                        cell_dict['importance'])

    def to_str_short(self):
        if 0 == len(self.form_a):
            return ''
        return "%g*\"%s\" + %g*\"%s\"" % \
            (self.weight_a, self.form_a, 1.0-self.weight_a, self.form_b)

class Paradigm(ABC):
    """A 3D or 5D matrix of competing noun of verb forms for given morphosyntactic contexts."""
    def __getitem__(self, n):
        """Return a row of cells (assignable)."""
        return self.para[n]

    def __str__(self):
        def descend(xs):
            if not isinstance(xs, list):
                return str(xs)
            below = [descend(x) for x in xs]
            below = filter(lambda s: bool(len(s)), below)
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
            assert len(num) <= 18
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
        me = NounParadigm()
        assert len(para_list) <= 2
        while para_list:
            list_below = para_list.pop(0)
            assert len(list_below) <= 18
            while list_below:
                cell = Cell.from_dict(list_below.pop(0))
                me.para[cell.number][cell.case] = cell
        return me

class NounCell(Cell):
    """A single cell in a noun paradigm for a given morphosyntactic context."""
    def __init__(self, number=0, case=0, weight_a=0.5, form_a='', form_b='', importance=1.0):
        super().__init__(weight_a, form_a, form_b, importance)
        self.number = number
        self.case = case

    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""
        return NounParadigm.morphosyntactic_properties(self.number, self.case)

class VerbCell(Cell):
    """A single cell in a verb paradigm for a given morphosyntactic context."""
    def __init__(self, person=0, number=0, defness=0, tense=0, mood=0, weight_a=0.5, form_a='', form_b='', importance=1.0):
        super().__init__(weight_a, form_a, form_b, importance)
        self.person = person
        self.number = number
        self.defness = defness
        self.tense = tense
        self.mood = mood

    def get_morphosyntactic_properties(self):
        """Returns a string listing the cell's features."""
        return VerbParadigm.morphosyntactic_properties(self.person, self.number, self.defness, self.tense, self.mood)

class NounParadigm(Paradigm):
    """A 3D matrix representing the competing forms of a single noun.
       Hungarian nouns inflect for number and case."""
    def __init__(self, weight_a=0.5, form_a='', form_b=''):
        self.para = [[NounCell(i, j, weight_a) for j in range(18)] for i in range(2)]
        self.para[0][0].form_a = form_a
        self.para[0][0].form_b = form_b
        self.para[0][0].importance = 1.0

    @staticmethod
    def morphosyntactic_properties(i, j):
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        assert (i < 2 and j < 18)
        numbers = {
            0 : 'sg',
            1 : 'pl'
        }
        cases = {
            0 : 'nom',
            1 : 'acc',
            2 : 'dat',
            3 : 'ins',
            4 : 'caus',
            5 : 'transl',
            6 : 'term',
            7 : 'ess-formal',
            8 : 'ess-modal',
            9 : 'ine',
           10 : 'supe',
           11 : 'ade',
           12 : 'ill',
           13 : 'subl',
           14 : 'all',
           15 : 'ela',
           16 : 'del',
           17 : 'abl'
        }
        return "{%s, %s}" % (numbers[i], cases[j])

    def nudge(self, amount, i, j):
        """Adjust the weights in a single cell."""
        assert(-1 <= amount <= 1)
        assert(i < 2 and j < 18)
        self.para[i][j].weight_a = clamp(self.para[i][j].weight_a + amount)

    def propagate(self, amount, i, j):
        """Spread a weight change down each dimension in the paradigm."""
        delta = clamp(self.para[i][j].importance * amount)
        for i_ in range(2):
            if i_ != i:
                self.nudge(delta, i_, j)
        for j_ in range(18):
            if j_ != j:
                self.nudge(delta, i, j_)

class VerbParadigm(Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self, weight_a=0.5):
        self.para = [[[[[VerbCell(i, j, k, l, m, weight_a) for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]

    @staticmethod
    def morphosyntactic_properties(i, j, k, l, m):
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        assert (i < 3 and j < 2 and k < 2 and l < 2 and m < 3)
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
        assert(0 <= amount <= 1)
        assert(i < 3 and j < 2 and k < 2 and l < 2 and m < 3)
        self.para[i][j][k].weight_a = clamp(self.para[i][j][k][l][m].weight_a + amount)

    def propagate(self, amount, i, j, k, l, m):
        """Spread a weight change down each dimension in the paradigm."""
        delta = clamp(self.para[i][j][k][l][m].importance * amount)
        for i_ in range(3):
            if i_ != i:
                self.nudge(delta, i_, j, k, l, m)
        for j_ in range(2):
            if j_ != j:
                self.nudge(delta, i, j_, k, l, m)
        for k_ in range(2):
            if k_ != k:
                self.nudge(delta, i, j, k_, l, m)
        for l_ in range(2):
            if l_ != l:
                self.nudge(delta, i, j, k, l_, m)
        for m_ in range(3):
            if m_ != m:
                self.nudge(delta, i, j, k, l, m_)
