__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np

from IdleKnights.constants import NX, NY

def team_reflector(team, position):
    new_position = np.array(position, dtype=np.intc)
    if team == 'blue':
        new_position[0] = -new_position[0] + NX
    return new_position

def circle_around(x, y):
    r = 1
    i, j = x - 1, y - 1
    while True:
        while i < x + r:
            i += 1
            yield r, (i, j)
        while j < y + r:
            j += 1
            yield r, (i, j)
        while i > x - r:
            i -= 1
            yield r, (i, j)
        while j > y - r:
            j -= 1
            yield r, (i, j)
        r += 1
        j -= 1
        yield r, (i, j)


def parse_position(position):
    position = np.array(position, dtype=np.intc)
    if len(position.shape) == 0:
        raise ValueError('Malformed position')
    if position[0] < 0:
        position[0] = 0
    elif position[0] > NX:
        position[0] = NX
    if position[1] < 0:
        position[1] = 0
    elif position[1] > NY:
        position[1] = NY
    return position
