__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import pytest
import numpy as np
from IdleKnights.logic.Maze import Maze, BOARD_EMPTY

nx = 50
ny = 50
blocks = .2
reduction_factor = 2
from time import time

m = Maze(nx, ny, flip=True)

walls = np.asarray(np.floor(np.random.random(int(np.floor((nx - 2)*(ny-2)*blocks))).reshape((-1, 2)) * np.array([nx-2, ny-2])), dtype=np.intc)
m.update_maze_single(walls, 1 * np.ones_like(walls[:, 0]))

m.write_board[0, 0] = BOARD_EMPTY
m.write_board[m.nx-1, m.ny-1] = BOARD_EMPTY

t_start = time()
route = m.solve_maze([0, 0], [m.nx-1, m.ny-1])
t_end = time()
print(f'Time taken: {t_end - t_start}s')
print(Maze.insert_route(m, route))
t_start = time()
reduced = Maze.reduce_map(m, reduction_factor)
t_end = time()
print(f'Time taken for reduction: {t_end - t_start}s')
# Make sure we can even attempt a solution
reduced.write_board[0:2, 0:2] = BOARD_EMPTY
reduced.write_board[reduced.nx-2:reduced.nx, reduced.ny-2:reduced.ny] = BOARD_EMPTY
route2 = reduced.solve_maze([0, 0], [reduced.nx-1, reduced.ny-1])
print(Maze.insert_route(reduced, route2))