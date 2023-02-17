__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.logic.route_generation.gradient_rtt import GradientMaze
from IdleKnights.logic.Maze import Maze
import numpy as np
# import matplotlib.pyplot as plt

nx = 400
ny = 600
m = Maze(nx, ny)
blocks = 5
walls = np.array([])
for i in range(blocks):
    x = np.random.randint(0, nx-30)
    y = np.random.randint(0, ny-30)
    w = np.random.randint(20, 30)
    h = np.random.randint(20, 30)
    m.update_maze_matrix([x, y], np.ones((w, h)), np.ones((w, h)))
o = m._board.copy()
gm = GradientMaze(nx, ny, o)
xy_start = [350, 300]
xy_goal = [100, 100]
f = gm.combined_potential(xy_goal)
# plt.figure(figsize=(10, 10))
# plt.imshow(m._board)
# gm.draw_gradient(f)
# plt.plot(xy_start[0], xy_start[1],'bo', color='red', markersize=10, label='start')
# plt.plot(xy_goal[0], xy_goal[1],'bo', color='green', markersize=10, label='goal')
# plt.legend()
# plt.show()
route = gm.solve(xy_start, xy_goal)
# plt.figure(figsize=(10, 10))
# plt.imshow(gm.map)
# gm.draw_gradient(f)
# plt.plot(route._route[:, 0], route._route[:, 1], linewidth=5)
# plt.plot(xy_start[0],xy_start[1],'bo', color='red', markersize=10, label='start')
# plt.plot(xy_goal[0], xy_goal[1],'bo', color='green', markersize=10, label='goal')
# plt.legend()
# plt.show()