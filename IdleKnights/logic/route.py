from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from collections import deque
from typing import Optional, Union, List

import numpy as np

MAX_STACK = 10


class Route:
    """
    Class which describes a route and can calculate waypoints.
    """
    def __init__(self, route: np.ndarray, view_distance: float = None):
        self._reduced = None
        self._len = 0
        self._route = None
        if view_distance is None:
            view_distance = np.inf
        self._view_distance = view_distance
        self.path = route

    @property
    def view_distance(self) -> float:
        """
        Return the view distance
        :return:
        """
        return self._view_distance

    @view_distance.setter
    def view_distance(self, new_view_distance: float):
        """
        Set the view distance and update the reduced route
        :param new_view_distance:
        :return:
        """
        self._view_distance = new_view_distance
        self._reduced_route()

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
        step_size = np.sum(np.diff(self.path, axis=0), axis=1)
        points = [self.path[0]]
        previous_step_size = step_size[0]
        mini_path_distance = 0
        for idx, current_step_size in enumerate(step_size[1:]):
            mini_path_distance += current_step_size
            if current_step_size != previous_step_size or mini_path_distance > 2*self._view_distance:
                points.append(self.path[idx+1])
                previous_step_size = current_step_size
                mini_path_distance = 0
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
    def __init__(self, destinations=None):
        if destinations is None:
            destinations = []
        self._destination = deque(np.array(destinations).astype(np.intc))
        self.old_position = None
        self.old_lengths = deque(maxlen=MAX_STACK)

    @property
    def destination(self):
        """
        Returns the destination stack.
        :return:
        """
        return self._destination
    @destination.setter
    def destination(self, new_destination: Union[np.ndarray, List[np.ndarray]]):
        """
        Sets the destination stack.
        :param new_destination:
        :return:
        """
        self._destination = deque(np.array(new_destination).astype(np.intc))
        self.old_position = None
        self.old_lengths.clear()

    @property
    def next_destination(self) -> np.ndarray:
        """
        Returns the next waypoint in the stack
        :return:
        """
        point = None
        if len(self.destination) > 0:
            point = self.destination[0]
        return point

    def add_final_waypoint(self, waypoint: np.ndarray):
        """
        Adds a waypoint to the end of the stack
        :param waypoint:
        :return:
        """
        self._destination.append(np.array(waypoint, dtype=np.intc))

    def add_next_waypoint(self, waypoint: np.ndarray):
        """
        Adds a waypoint to the start of the stack
        :param waypoint:
        :return:
        """
        if np.any(self._destination == waypoint):
            return
        self._destination.appendleft(np.array(waypoint, dtype=np.intc))

    def pop_waypoint(self, from_start: bool = True):
        """
        Pops the next waypoint from the stack, if from_start is True, then the first waypoint is popped, otherwise the last
        :param from_start:
        :return:
        """
        if len(self._destination) == 0:
            return
        if from_start:
            self.destination.popleft()
        else:
            self.destination.pop()

    def next_waypoint(self, current_position: np.ndarray, tol: float = 0.1) -> Optional[np.ndarray]:
        """
        Returns the next waypoint if the current position is within the tolerance of the next waypoint. None otherwise.
        :param current_position:
        :param tol:
        :return:
        """
        if len(self._destination) == 0:
            return None
        l1 = np.hypot(current_position[0] - self.next_destination[0], current_position[1] - self.next_destination[1])
        if self.old_position is not None:
            self.old_lengths.appendleft(np.hypot(current_position[0] - self.old_position[0], current_position[1] - self.old_position[1]))
        if l1 <= tol:
            # print(f'Current: {current_position}, Target {self.next_destination}, Distance: {l1}')
            self.old_lengths.clear()
            self.pop_waypoint()
        if len(self.old_lengths) == MAX_STACK and self.old_lengths.count(self.old_lengths[-1]) == MAX_STACK and l1 < 1.25:
            # print(f'Pruned {self.next_destination} ({current_position})')
            self.pop_waypoint()
            self.old_lengths.clear()
        self.old_position = current_position
        return self.next_destination


class WaypointStack:
    def __init__(self):
        self._stack = deque()

    def add_waypoint(self, waypoint: Waypoint):
        """
        Add a waypoint to the stack
        :param waypoint:
        :return:
        """
        self._stack.appendleft(waypoint)

    def remove_waypoint(self, first=True):
        """
        Remove a waypoint from the stack
        :param first:
        :return:
        """
        if first:
            self._stack.popleft()
        else:
            self._stack.pop()

    def next_destination(self, current_position: np.ndarray, tol=0.1) -> np.ndarray:
        """
        Return the next destination
        :param current_position:
        :param tol:
        :return:
        """
        if len(self._stack) == 0:
            return None
        destination = self._stack[0].next_waypoint(current_position, tol)
        if destination is None:
            self.remove_waypoint()
            destination = self.next_destination(current_position, tol)
        return destination

    def next_waypoint(self) -> np.ndarray:
        """
        Return the next waypoint
        :return:
        """
        if len(self._stack) == 0:
            return None
        return self._stack[0].next_destination()

