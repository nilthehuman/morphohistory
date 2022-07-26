"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

def clamp(x):
    return max(0., min(1., x))

class Cell:
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    def __init__(self, form_a, form_b, weight_a, importance):
        self.form_a = form_a
        self.form_b = form_b
        self.weight_a = weight_a
        self.importance = importance

    def __str__(self):
        return "%g * \"%s\" + %g * \"%s\"" % (self.weight_a, self.form_a, 1.0-self.weight_a, self.form_b)

class Paradigm:
    """A 3D or 5D matrix of competing noun or verb forms in each cell."""
    def __str__(self):
        """TODO"""
        return str(self.para)

class NounParadigm(Paradigm):
    """A 3D matrix representing the competing forms of a single noun.
       Hungarian nouns inflect for number, possessor and case."""
    def __init__(self, weight_a=0.5):
        self.para = [[[Cell(weight_a) for k in range(17)] for j in range(7)] for i in range(2)]

    def fill_cell(self, cell, i, j, k):
        self.para[i][j][k] = cell

    def nudge(self, amount, i, j, k):
        assert(0 <= amount and amount <= 1)
        assert(i < 2 and j < 7 and k < 17)
        self.para[i][j][k].weight_a = clamp(self.para[i][j][k].weight_a + amount)

    def propagate(self, amount, i, j, k):
        delta = clamp(self.para[i][j][k].importance * amount)
        for i_ in range(0,2):
            if i_ != i:
                self.nudge(delta, i_, j, k)
        for j_ in range(0,7):
            if j_ != j:
                self.nudge(delta, i, j_, k)
        for k_ in range(0,17):
            if k_ != k:
                self.nudge(delta, i, j, k_)

class VerbParadigm(Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self, weight_a=0.5):
        self.para[i][j][k][l][m] = [[[[[Cell(weight_a) for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]

    def fill_cell(self, cell, i, j, k, l, m):
        self.para[i][j][k][l][m] = cell

    def nudge(self, amount, i, j, k, l, m):
        assert(0 <= amount and amount <= 1)
        assert(i < 3 and j < 2 and k < 2 and l < 2 and m < 3)
        self.para[i][j][k].weight_a = clamp(self.para[i][j][k][l][m].weight_a + amount)

    def propagate(self, amount, i, j, k, l, m):
        delta = clamp(self.para[i][j][k][l][m].importance * amount)
        for i_ in range(0,3):
            if i_ != i:
                self.nudge(delta, i_, j, k, l, m)
        for j_ in range(0,2):
            if j_ != j:
                self.nudge(delta, i, j_, k, l, m)
        for k_ in range(0,2):
            if k_ != k:
                self.nudge(delta, i, j, k_, l, m)
        for l_ in range(0,2):
            if l_ != l:
                self.nudge(delta, i, j, k, l_, m)
        for m_ in range(0,3):
            if m_ != m:
                self.nudge(delta, i, j, k, l, m_)
