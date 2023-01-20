__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np


class Route:
    """
    Class which describes a route and can calculate waypoints.
    """
    def __init__(self, route: np.ndarray):
        self._reduced = None
        self._len = np.inf
        self._route = None
        self.path = route

    @property
    def path(self) -> np.ndarray:
        """
        Return the stored path
        """
        return self._route

    @path.setter
    def path(self, new_path: np.ndarray):
        """
        Set the new path and update derivatives

        :param new_path: New path
        """
        self._route = new_path
        self._reduced_route()
        self._len_route()

    @property
    def reduced_route(self) -> np.ndarray:
        """
        Return a reduced route which specifies waypoint to waypoint.
        """
        return self._reduced

    def _reduced_route(self) -> None:
        """
        Generates a reduced path of waypoints.
        This means that if a point is along the same direction as the previous one, it will not
        be noted, only the point before a change of direction.
        """
        if self.path.shape[0] == 0:
            self._reduced = np.array([[]])
            return
        d = np.sum(np.diff(self.path, axis=0), axis=1)
        self._reduced = np.concatenate((self.path[0, :][np.newaxis, :],
                                        self.path[:-1, :][d != 2, :],
                                        self.path[-1, :][np.newaxis, :]), axis=0)

    def _len_route(self):
        """
        Calculates the length of a reduced route
        """
        self._len = np.sum(np.sqrt(np.sum(np.diff(self._reduced, axis=0) ** 2, axis=1)))

    @property
    def length(self) -> float:
        """
        Returns the length of a reduced route.
        """
        return self._len

    @property
    def start(self) -> np.ndarray:
        """
        Returns the starting point (x, y) of the path.
        """
        return self.path[0, :]

    @property
    def end(self) -> np.ndarray:
        """
        Returns the end point (x, y) of the path.
        """
        return self.path[-1, :]
