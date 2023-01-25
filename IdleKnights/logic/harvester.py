__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Maze import Maze

class Gem:
    def __init__(self, position, maze):
        self.position = np.array(position)
        self.valid = True
        self.collector = ''
        self.in_progress = False
        self.maze = maze

    def collect_gem(self, maze: Maze):
        route = maze.solve_maze()


class Harvester:
    def __init__(self, maze: Maze):
        self.maze = maze
        self._terrain = []

    def add_gem(self, position):
        if not np.any(np.abs(np.array([gem.position for gem in self._terrain]) - position) == 0.0):
                self._terrain.append(Gem(position, self.maze))

    def _sorted_gems(self, my_position):
        gems = self._terrain[np.apply_along_axis(lambda row: np.hypot(row[0] - my_position[0], row[1]-my_position[1]),
                                                 axis=1, arr=[gem.position for gem in self._terrain]).argsort()]
        return gems

    def closest_gems(self, my_position, n_gems=1):
        gems = self._sorted_gems(my_position)
        return gems[0:n_gems]

    def collect_gem(self, me, gem: Gem):
        gem.collector = me["name"]
        gem.in_progress = True
        return self.maze.solve_maze(me["position"], gem.position, 40)
