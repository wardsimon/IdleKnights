__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from scipy.ndimage.morphology import distance_transform_edt as bwdist
from numpy.linalg import norm

from IdleKnights.logic.route import Route


class GradientMaze:
    def __init__(self, nx, ny, initial_map=None):
        self.nx = nx
        self.ny = ny
        if initial_map is None:
            self.map = np.zeros((nx, ny))
        else:
            self.map = initial_map

    def combined_potential(self, goal, influence_radius=4, attractive_coef=1./200, repulsive_coef=200):
        """ Repulsive potential """
        d = bwdist(self.map == 0)
        d2 = (d/100.) + 1 # Rescale and transform distances
        d0 = influence_radius
        nu = repulsive_coef
        repulsive = nu*((1./d2 - 1./d0)**2)
        repulsive[d2 > d0] = 0
        """ Attractive potential """
        [x, y] = np.meshgrid(np.arange(self.nx), np.arange(self.ny))
        xi = attractive_coef
        attractive = (xi * ((goal[0] - x)**2 + (goal[1] - y)**2)).T
        """ Combine terms """
        f = attractive + repulsive
        return f

    def solve(self, start, goal, max_its=700):
        f = self.combined_potential(goal)
        route = self.gradient_planner(f, start, goal, max_its)
        return route

    def gradient_planner(self, f, start, goal, max_its=400):
        # GradientBasedPlanner : This function plans a path through a 2D
        # environment from a start to a destination based on the gradient of the
        # function f which is passed in as a 2D array. The two arguments
        # start_coords and end_coords denote the coordinates of the start and end
        # positions respectively in the array while max_its indicates an upper
        # bound on the number of iterations that the system can use before giving
        # up.
        # The output, route, is an array with 2 columns and n rows where the rows
        # correspond to the coordinates of the robot as it moves along the route.
        # The first column corresponds to the x coordinate and the second to the y coordinate

        [gx, gy] = np.gradient(-f)
        start_coords = start
        end_coords = goal
        route = np.array([np.array(start_coords)])
        not_at_end = True
        i = 0
        while i < max_its and not_at_end:
            current_point = route[-1, :]
            if np.hypot(current_point[0] - end_coords[0], current_point[1] - end_coords[1]) < 5.0:
                route = np.vstack([route, np.array(end_coords)])
                not_at_end = False
            ix = int(current_point[0])
            iy = int(current_point[1])
            try:
                vx = gx[ix, iy]
                vy = gy[ix, iy]
            except IndexError:
                break
            dt = 1 / np.linalg.norm([vx, vy])
            next_point = current_point + dt * np.array([vx, vy])
            if np.any(next_point < 0) or np.any(next_point >= np.array([self.nx, self.ny])):
                break
            route = np.vstack([route, next_point])
            i += 1
        return Route(route.astype(np.intc))

    # def layered_planner(self, P, V, dt):
    #     """
    #     Layered Motion Planning:
    #     inputs: -path from global planner, P
    #             -obstacles map representation, obstacles_grid
    #     output: -route, path corrected with potential fields-based
    #              local planner
    #     """
    #     route = np.array([P[-1, :]])
    #
    #     for i in range(len(P) - 1, 0, -1):
    #         start = route[-1, :]
    #         goal = P[i - 1]
    #
    #         # Combined potential
    #         f = self.combined_potential(goal)
    #
    #         # Plan route between 2 consecutive waypoints from P
    #         V = 0.3  # [m/s]
    #         dx = V * dt
    #         route_via = self.gradient_planner(f, start, goal, 200)
    #         route = np.vstack([route, route_via])
    #     return route

    def draw_gradient(self, f, skip=10):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise RuntimeError('cannot import matplotlib, make sure matplotlib package is installed')
        [x_m, y_m] = np.meshgrid(range(self.ny), range(self.nx))
        [gy, gx] = np.gradient(-f)
        Q = plt.quiver(x_m[::skip, ::skip], y_m[::skip, ::skip], gx[::skip, ::skip], gy[::skip, ::skip])
        return Q
