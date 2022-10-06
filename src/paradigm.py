"""A simple probabilistic model of Hungarian noun and verb paradigms and their internal mechanics."""

def clamp(x):
    return max(0., min(1., x))

class Cell:
    """A weighted superposition of two word forms for the same morphosyntactic context."""
    def __init__(self, weight_a=0.5, form_a='', form_b='', importance=0.):
        self.weight_a = weight_a
        self.form_a = form_a
        self.form_b = form_b
        self.importance = importance

    def __str__(self):
        if 0 == len(self.form_a):
            return ''
        else:
            return "(%s, %g * \"%s\" + %g * \"%s\")" % \
            (self.get_morphosyntactic_properties(), self.weight_a, self.form_a, 1.0-self.weight_a, self.form_b)

    def to_str_short(self):
        if 0 == len(self.form_a):
            return ''
        else:
            return "%g*\"%s\" + %g*\"%s\"" % \
            (self.weight_a, self.form_a, 1.0-self.weight_a, self.form_b)

class Paradigm:
    """A 3D or 5D matrix of competing noun of verb forms for a given morphosyntactic context."""
    def __str__(self):
        def descend(xs):
            if type(xs) is not list:
                return str(xs)
            else:
                below = [descend(x) for x in xs]
                below = filter(lambda s: bool(len(s)), below)
                return '[' + ', '.join(below) + ']'
        return descend(self.para)

class NounCell(Cell):
    """A single cell in a noun paradigm for a given morphosyntactic context."""
    def __init__(self, number=0, possessor=0, case=0, weight_a=0.5, form_a='', form_b='', importance=0.):
        super().__init__(weight_a, form_a, form_b, importance)
        self.number = number
        self.possessor = possessor
        self.case = case

    def get_morphosyntactic_properties(self):
        return NounParadigm.morphosyntactic_properties(self.number, self.possessor, self.case)

class VerbCell(Cell):
    """A single cell in a verb paradigm for a given morphosyntactic context."""
    def __init__(self, person=0, number=0, defness=0, tense=0, mood=0, weight_a=0.5, form_a='', form_b='', importance=0.):
        super().__init__(weight_a, form_a, form_b, importance)
        self.person = person
        self.number = number
        self.defness = defness
        self.tense = tense
        self.mood = mood

    def get_morphosyntactic_properties(self):
        return VerbParadigm.morphosyntactic_properties(self.person, self.number, self.defness, self.tense, self.mood)

class NounParadigm(Paradigm):
    """A 3D matrix representing the competing forms of a single noun.
       Hungarian nouns inflect for number, possessor and case."""
    def __init__(self, weight_a=0.5):
        self.para = [[[NounCell(i, j, k, weight_a) for k in range(18)] for j in range(7)] for i in range(2)]

    def __getitem__(self, n):
        """Return a single cell (assignable)."""
        return self.para[n]

    @staticmethod
    def morphosyntactic_properties(i, j, k):
        """Get the set of features describing a cell's context.
        (Gregory Stump's exact term if I'm not mistaken.)"""
        assert (i < 2 and j < 7 and k < 18)
        numbers = {
            0 : 'sg',
            1 : 'pl'
        }
        possessors = {
            0 : 'none',
            1 : '1sg',
            2 : '2sg',
            3 : '3sg',
            4 : '1pl',
            5 : '2pl',
            6 : '3pl'
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
        return "{%s, %s, %s}" % (numbers[i], possessors[j], cases[k])

    def nudge(self, amount, i, j, k):
        """Adjust the weights in a single cell."""
        assert(-1 <= amount and amount <= 1)
        assert(i < 2 and j < 7 and k < 18)
        self.para[i][j][k].weight_a = clamp(self.para[i][j][k].weight_a + amount)

    def propagate(self, amount, i, j, k):
        """Spread a weight change down each dimension in the paradigm."""
        delta = clamp(self.para[i][j][k].importance * amount)
        for i_ in range(2):
            if i_ != i:
                self.nudge(delta, i_, j, k)
        for j_ in range(7):
            if j_ != j:
                self.nudge(delta, i, j_, k)
        for k_ in range(18):
            if k_ != k:
                self.nudge(delta, i, j, k_)

class VerbParadigm(Paradigm):
    """A 5D matrix representing the competing forms of a single verb.
       Hungarian verbs inflect for person, number, object definiteness, tense and mood."""
    def __init__(self, weight_a=0.5):
        self.para = [[[[[VerbCell(i, j, k, l, m, weight_a) for m in range(3)] for l in range(2)] for k in range(2)] for j in range(2)] for i in range(3)]

    def fill_cell(self, cell, i, j, k, l, m):
        """Assign a single cell."""
        self.para[i][j][k][l][m] = cell

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
        assert(0 <= amount and amount <= 1)
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
