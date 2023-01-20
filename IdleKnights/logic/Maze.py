import numpy as np
from typing import Tuple, Union, Optional

from IdleKnights.constants import *
from IdleKnights.logic.routing.a_solver import compute as a_compute

class Maze:
    def __init__(self, nx: int, ny: int, flip: bool = True, initialize: bool = True):
        self.nx = nx
        self.ny = ny
        self.flip = flip
        self._board = BOARD_EMPTY * np.ones((nx, ny), dtype=np.intc)
        self._i_board = self._board[::-1]
        if initialize:
            self.initialize_board()

    @classmethod
    def from_matrix(cls, matrix: np.ndarray, flip: bool = True):
        nx, ny = matrix.shape
        maze = cls(nx, ny, flip, False)
        maze._board = matrix.astype(np.intc)

    def initialize_board(self):
        self._board[0, :] = BOARD_WALL
        self._board[-1, :] = BOARD_WALL
        self._board[:, 0] = BOARD_WALL
        self._board[:, -1] = BOARD_WALL

    def update_maze_single(self, location: Union[Tuple[int, int], np.ndarray], new_element: Union[int, np.ndarray]):
        if isinstance(location, Tuple):
            location = np.array([[*location]])
            new_element = np.array([new_element])
        for idx, loc in enumerate(location):
            self._board[loc[0], loc[1]] = new_element[idx]

    def update_maze_matrix(self, location: Tuple[int, int], new_section: np.ndarray, inverted_section: bool = False):
        sx = location[0]
        sy = location[1]
        ex = sx + new_section.shape[0]
        ey = sy + new_section.shape[1]

        empty_mask = new_section == INPUT_EMPTY
        wall_mask = new_section == INPUT_WALL
        uk_mask = new_section == INPUT_UNKNOWN

        new_section[empty_mask] = BOARD_EMPTY
        new_section[wall_mask] = BOARD_WALL

        if np.any(uk_mask):
            new_section = np.ma.array(new_section, mask=uk_mask)

        if inverted_section:
            self._board[sx:ex, sy:ey] = new_section[::-1]
        else:
            self._board[sx:ex, sy:ey] = new_section

    @property
    def read_board(self):
        if self.flip:
            # Return reversed memory view
            return self._i_board
        else:
            return self._board

    @property
    def write_board(self):
        return self._board

    def is_wall(self, x, y):
        return self.read_board[x, y] == BOARD_WALL

    def in_maze(self, x, y):
        return x > 0 & x < self.nx & y > 0 & y < self.ny

    def solve_maze(self, start, end):
        start = np.array(start, dtype=np.intc)
        end = np.array(end, dtype=np.intc)
        return Route(a_compute(self._board, start, end)[::-1])

    @staticmethod
    def _colorize(elm):
        if elm == BOARD_EMPTY:
            return coloured_square('#FFFFFF')
        elif elm == BOARD_WALL:
            return coloured_square('#CCFFFF')
        elif elm == BOARD_ROUTE:
            return coloured_square('#FF5733')
        else:
            return coloured_square('#CCCCCC')

    def __str__(self):
        s = []
        for j in range(self.read_board.shape[1]):
            s.append(''.join([f'{self._colorize(self.read_board[j, i])}' for i in range(self.read_board.shape[0])]))
        return '\n'.join(s)

    def __repr__(self):
        return f'Maze <{self.nx},{self.ny}>'

    @classmethod
    def insert_route(cls, input_maze, route):
        new_maze = cls(input_maze.nx, input_maze.ny, input_maze.flip, initialize=False)
        new_maze._board[input_maze._board == BOARD_WALL] = BOARD_WALL
        new_maze.update_maze_single(route.path, BOARD_ROUTE * np.ones_like(route.path[:, 0]))
        return new_maze

    @classmethod
    def reduce_map(cls, input_maze, factor_x, factor_y = None):
        if factor_y is None:
            factor_y = factor_x
        board = input_maze._board
        reduced = np.add.reduceat(np.add.reduceat(board, range(0, input_maze.ny, factor_y)).T, range(0, input_maze.nx, factor_x)).T
        new_maze = cls(reduced.shape[0], reduced.shape[1], input_maze.flip, initialize=False)
        new_maze._board[reduced > 0] = BOARD_WALL
        return new_maze


class Route:
    def __init__(self, route):
        self._reduced = None
        self._len = np.inf
        self._route = None
        self.path = route

    @property
    def path(self):
        return self._route

    @path.setter
    def path(self, value):
        self._route = value
        self._reduced_route()
        self._len_route()

    @property
    def reduced_route(self):
        return self._reduced

    def _reduced_route(self):
        if self.path.shape[0] == 0:
            self._reduced = np.array([[]])
            return
        d = np.sum(np.diff(self.path, axis=0), axis=1)
        self._reduced = np.concatenate((self.path[0, :][np.newaxis, :],
                                        self.path[:-1, :][d != 2, :],
                                        self.path[-1, :][np.newaxis, :]), axis=0)

    def _len_route(self):
        self._len = np.sum(np.sqrt(np.sum(np.diff(self._reduced, axis=0) ** 2, axis=1)))

    @property
    def length(self):
        return self._len

    @property
    def start(self):
        return self.path[0, :]

    @property
    def end(self):
        return self.path[-1, :]


def coloured_square(hex_string):
    """
    Returns a coloured square that you can print to a terminal.
    """
    hex_string = hex_string.strip("#")
    assert len(hex_string) == 6
    red = int(hex_string[:2], 16)
    green = int(hex_string[2:4], 16)
    blue = int(hex_string[4:6], 16)

    return f"\033[48:2::{red}:{green}:{blue}m \033[49m"
