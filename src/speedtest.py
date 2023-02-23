from copy import copy
from numpy import arange
from json import load
from math import sin, cos, pi

from .agora import Agora
from .speaker import Speaker

def populate(agora, r1, r2):
    for n in range(16):
        x = sin(2 * pi * float(n) / 16) * r1
        y = cos(2 * pi * float(n) / 16) * r1
        pos = (300 + x, 300 + y)
        agora.add_speaker(Speaker.fromweight(n, pos, 0.0))
    for n in range(16):
        x = sin(2 * pi * float(n) / 16) * r2
        y = cos(2 * pi * float(n) / 16) * r2
        pos = (300 + x, 300 + y)
        agora.add_speaker(Speaker.fromweight(16 + n, pos, 1.0))

result_item = {'bias': 0, 'exp': 0, 'fotelnak' : 0, 'fotelnek' : 0, None : 0}
result = []

a = Agora()
n = 0
for r in [25, 50, 75, 100, 125, 150, 175]:
    for exp in [1, 5, 10, 15, 20]:
        a.clear_speakers()
        populate(a, r, 200)
        for s in a.speakers:
            s.experience = exp
        a.save_starting_state()
        result.append(copy(result_item))
        result[-1]['r'] = r
        result[-1]['exp'] = exp
        n = n + 1
        print("Running setup", n, "out of", 7*5)
        for _ in range(0, 50):
            a.simulate_till_stable(is_stable=None)
            dom_form = a.dominant_form()
            result[-1][dom_form] = result[-1][dom_form] + 1
            a.reset()

with open('output.csv', 'w') as stream:
    for r in result:
        stream.write(str(r['r']) + ',' + str(r['exp']) + ',' + str(r['fotelnak']) + ',' + str(r['fotelnek']) + ',' + str(r[None]) + "\n")

exit(0)
########  ########  ########
########  ########  ########

a = Agora()
a.load_from_file('./examples/core.agr')

result_item = {'bias': 0, 'exp': 0, 'fotelnak' : 0, 'fotelnek' : 0, None : 0}
result = []
n = 0
for bias in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    for exp in [1, 5, 10, 15, 20]:
        for s in a.speakers:
            if s.para[0][0].weight_a != 0:
                s.para[0][0].weight_a = bias
            s.experience = exp
        a.save_starting_state()
        result.append(copy(result_item))
        result[-1]['bias'] = bias
        result[-1]['exp'] = exp
        n = n + 1
        print("Running setup", n, "out of 30")
        for _ in range(0, 50):
            a.simulate_till_stable(is_stable=None)
            dom_form = a.dominant_form()
            result[-1][dom_form] = result[-1][dom_form] + 1
            a.reset()

with open('output.csv', 'w') as stream:
    for r in result:
        stream.write(str(r['bias']) + ',' + str(r['exp']) + ',' + str(r['fotelnak']) + ',' + str(r['fotelnek']) + ',' + str(r[None]) + "\n")

"""
        import random
        self.color[0] = random.random() - 0.2
        self.color[1] = random.random() - 0.2
        self.color[2] = random.random() + 0.4
"""
