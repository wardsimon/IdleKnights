__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from collections import deque

import numpy as np

MAX_STACK = 10

class Route:
    """
    Class which describes a route and can calculate waypoints.
    """
    def __init__(self, route: np.ndarray):
        self._reduced = None
        self._len = 0
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

    def _reduced_route(self):
        if self.path.shape[0] == 0:
            self._reduced = np.array([[]])
            return
        d = np.sum(np.diff(self.path, axis=0), axis=1)
        points = [self.path[0]]
        i = d[0]
        for idx, v in enumerate(d[1:]):
            if v != i:
                points.append(self.path[idx+1])
                i = v
        points.append(self.path[-1])
        self._reduced = np.array(points, dtype=np.intc)

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


class Waypoint:
    def __init__(self, destinations):
        self._destination = deque(np.array(destinations).astype(np.intc))
        self._in_progress = False
        self.old_position = None
        self.old_lenths = deque(maxlen=MAX_STACK)
    @property
    def in_progress(self) -> bool:
        return self._in_progress

    @in_progress.setter
    def in_progress(self, new_value: bool):
        self._in_progress = new_value

    @property
    def destination(self):
        return self._destination

    @property
    def next_destination(self) -> np.ndarray:
        point = None
        if len(self.destination) > 0:
            point = self.destination[0]
        return point

    def add_final_waypoint(self, waypoint):
        self._destination.append(np.array(waypoint, dtype=np.intc))

    def add_next_waypoint(self, waypoint):
        if np.any(self._destination == waypoint):
            return
        self._destination.appendleft(np.array(waypoint, dtype=np.intc))

    def pop_waypoint(self, from_start=True):
        if from_start:
            self.destination.popleft()
        else:
            self.destination.pop()

    def next_waypoint(self, current_position: np.ndarray, tol=0.1) -> np.ndarray:
        l1 = np.hypot(current_position[0] - self.next_destination[0], current_position[1] - self.next_destination[1])
        if self.old_position is not None:
            self.old_lenths.appendleft(np.hypot(current_position[0] - self.old_position[0], current_position[1] - self.old_position[1]))
        if l1 <= tol:
            print(l1, current_position)
            self.old_lenths.clear()
            self.pop_waypoint()
        if len(self.old_lenths) == MAX_STACK and self.old_lenths.count(self.old_lenths[-1]) == MAX_STACK and l1 < 1.5:
            print(f'Pruned {self.next_destination} ({current_position})')
            self.pop_waypoint()
            self.old_lenths.clear()
        self.old_position = current_position
        return self.next_destination

