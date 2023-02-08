import numpy as np
from typing import Tuple, Union

from IdleKnights.constants import *
from IdleKnights.logic.route import Route
from IdleKnights.logic.route_generation.a_solver import compute as a_compute


class Maze:
    def __init__(self, nx: int, ny: int, flip: bool = True, initialize: bool = True):
        self.nx = nx
        self.ny = ny
        self.flip = flip
        self._board: np.ndarray = BOARD_EMPTY * np.ones((nx, ny), dtype=np.intc)
        self._board_dilated: np.ndarray = BOARD_EMPTY * np.ones((nx, ny), dtype=np.intc)
        self.fog_of_war = np.ones((nx, ny), dtype=bool)
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

        self._board_dilated[0, :] = BOARD_WALL
        self._board_dilated[-1, :] = BOARD_WALL
        self._board_dilated[:, 0] = BOARD_WALL
        self._board_dilated[:, -1] = BOARD_WALL

    def update_maze_single(self, location: Union[Tuple[int, int], np.ndarray], new_element: Union[int, np.ndarray]):
        if isinstance(location, Tuple):
            location = np.array([[*location]])
            new_element = np.array([new_element])
        for idx, loc in enumerate(location):
            self._board[loc[0], loc[1]] = new_element[idx]
            self._board_dilated[loc[0], loc[1]] = new_element[idx]

    def update_maze_matrix(self, location: Tuple[int, int], new_section: np.ndarray, dilated_new_section: np.ndarray, inverted_section: bool = False):
        sx = location[0]
        sy = location[1]
        ex = sx + new_section.shape[0]
        ey = sy + new_section.shape[1]

        empty_mask = new_section == INPUT_EMPTY
        wall_mask = new_section == INPUT_WALL
        uk_mask = new_section == INPUT_UNKNOWN

        new_section[empty_mask] = BOARD_EMPTY
        new_section[wall_mask] = BOARD_WALL

        empty_mask2 = dilated_new_section == INPUT_EMPTY
        wall_mask2 = dilated_new_section == INPUT_WALL
        uk_mask2 = dilated_new_section == INPUT_UNKNOWN

        new_section[empty_mask] = BOARD_EMPTY
        new_section[wall_mask] = BOARD_WALL

        dilated_new_section[empty_mask2] = BOARD_EMPTY
        dilated_new_section[wall_mask2] = BOARD_WALL

        try:
            view = self._board[sx:ex, sy:ey]
            view[~uk_mask] = new_section[~uk_mask]
            view = self._board_dilated[sx:ex, sy:ey]
            view[~uk_mask2] = dilated_new_section[~uk_mask2]
        except IndexError:
            return
        # fog_view = self.fog_of_war[sx:ex, sy:ey]
        # fog_view[~uk_mask] = False

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

    def solve_maze(self, start, end, extra=None):
        try:
            start = np.array(start, dtype=np.intc)
            end = np.array(end, dtype=np.intc)
        except TypeError:
            print(start)
            print(end)
        if extra is None:
            return Route(a_compute(self._board, start, end)[::-1])
        else:
            sx = np.min([start[0], end[0]])-extra
            if sx < 0:
                sx = 0
            ex = np.max([start[0], end[0]])+extra
            if ex > 1790:
                ex = 1790
            sy = np.min([start[1], end[1]])-extra
            if sy < 0:
                sy = 0
            ey = np.max([start[1], end[1]])+extra
            if ey > 960:
                ey = 960
            off = np.array([sx, sy], dtype=np.intc)
            try:
                r = a_compute(self._board[sx:ex, sy:ey].copy(), self._board_dilated[sx:ex, sy:ey].copy(), start-off, end-off)[::-1]
            except ValueError:
                return Route(np.array([start, end], dtype=np.intc))
            except LookupError:
                return Route(np.array([start, end], dtype=np.intc))
            except ReferenceError:
                return Route(np.array([start, end], dtype=np.intc))
            r = r + off
            return Route(r)

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
        if self._board.size > 25**2:
            return self.__repr__(' TruncatedView')
        s = []
        for j in range(self.read_board.shape[1]):
            s.append(''.join([f'{self._colorize(self.read_board[i, j])}' for i in range(self.read_board.shape[0])]))
        return '\n'.join(s)

    def __repr__(self, additional_text: str=None):
        s = f'Maze <{self.nx},{self.ny}>'
        if additional_text is not None:
            s += additional_text
        return s

    @classmethod
    def insert_route(cls, input_maze, route):
        new_maze = cls(input_maze.nx, input_maze.ny, input_maze.flip, initialize=False)
        new_maze._board[input_maze._board == BOARD_WALL] = BOARD_WALL
        new_maze.update_maze_single(route.path, BOARD_ROUTE * np.ones_like(route.path[:, 0]))
        return new_maze

    @classmethod
    def reduce_map(cls, input_maze, factor_x, factor_y=None):
        if factor_y is None:
            factor_y = factor_x
        board = input_maze._board
        reduced = np.add.reduceat(np.add.reduceat(board, range(0, input_maze.ny, factor_y)).T,
                                  range(0, input_maze.nx, factor_x)).T
        new_maze = cls(reduced.shape[0], reduced.shape[1], input_maze.flip, initialize=False)
        new_maze._board[reduced > 0] = BOARD_WALL
        return new_maze


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
