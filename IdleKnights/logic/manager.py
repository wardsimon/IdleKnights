__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.constants import NX, NY
from IdleKnights.logic.Maze import Maze

class Manager:

    def __init__(self, team):
        self.maze = Maze(NX, NY)
        self.route = dict.fromkeys(team.keys())
        self.override = dict.fromkeys(team.keys(), None)
        self._others = {v: k for k, v in team.items()}

    def others(self, filter=None):
        if filter is None:
            filter = lambda item: True
        return {key: value for key, value in self._others.items() if filter(key)}
