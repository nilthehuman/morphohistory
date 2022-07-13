"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

class Cell:
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    def __init__(self, form_a, form_b, weight_a):
        self.form_a = form_a
        self.form_b = form_b
        self.weight_a = weight_a
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
    def __init__(self):
        self.para = [[[None for k in range(17)] for j in range(7)] for i in range(2)]
    def fill_cell(self, cell, i, j, k):
        self.para[i][j][k] = cell
    def nudge(self, amount, i, j, k):
        assert(0 <= amount and amount <= 1)
        assert(i < 2 and j < 7 and k < 17)
        self.para[i][j][k].weight_a += amount

class VerbParadigm(Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self):
        self.para = [[[[[None for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]
    def fill_cell(self, cell, i, j, k, l, m):
        self.para[i][j][k][l][m] = cell
    def nudge(self, amount, i, j, k, l, m):
        assert(0 <= amount and amount <= 1)
        assert(i < 3 and j < 2 and k < 2 and l < 2 and m < 3)
        self.para[i][j][k][l][m] += amount
