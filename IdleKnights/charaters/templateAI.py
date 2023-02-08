from collections import deque, namedtuple

import numpy as np
from scipy.signal import convolve2d
from types import MappingProxyType

from IdleKnights.constants import CREATOR, KERNEL, INPUT_UNKNOWN, INPUT_EMPTY, INPUT_WALL, BOARD_WALL, BOARD_EMPTY, NX, \
    NY
from IdleKnights.logic.route import Waypoint
from IdleKnights.tools.logging import get_logger
from IdleKnights.tools.positional import circle_around, parse_position

import abc
from quest.core.ai import BaseAI

Status = namedtuple('Status', ['position', 'time', 'dt', 'speed', 'view_radius'])


class TemplateAI(BaseAI):

    def __init__(self, *args, creator: str = None, kind: str = None, **kwargs):
        if creator is None or not isinstance(creator, str):
            raise AttributeError('The AI needs a `creator`')
        if kind is None or not isinstance(kind, str):
            raise AttributeError('The warrior needs a `kind`')
        super().__init__(*args, creator=creator, kind=kind, **kwargs)

    @abc.abstractmethod
    def run(self, t: float, dt: float, info: dict):
        pass


class IdleTemplate(TemplateAI):

    manager = None
    number = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, **kwargs)
        self.name = None
        self._current_position = None
        self._r = None
        self._dt = None
        self.view_radius = None
        self.previous_position = deque(maxlen=10)
        self.previous_health = 0
        self.speed = 0
        self.destination = None
        self.first_run = True
        self._waypoints = Waypoint()
        self.logger = None
        self._status = {'going_to_castle': False,
                        'going_to_fountain': False,
                        'going_to_gem': False,
                        'going_to_enemy': False,
                        'going_exploring': False
                        }

    def reset_status(self):
        for key in self._status:
            self._status[key] = False

    def set_status(self, status):
        self.reset_status()
        self._status[status] = True

    @property
    def status(self):
        return MappingProxyType(self._status)

    def update_map(self, me, info):

        local_map = info['local_map']
        local_map[local_map == 2] = 0
        x = me['x']
        mi_x = x - me['view_radius']
        if mi_x < 0:
            mi_x = 0
        y = me['y']
        mi_y = y - me['view_radius']
        if mi_y < 0:
            mi_y = 0
        result = convolve2d(local_map.astype(np.intc), KERNEL, mode='same').astype(np.intc)

        i_mask = local_map < 0
        e_mask = local_map == 0
        w_mask = local_map > 0
        local_map[i_mask] = INPUT_UNKNOWN
        local_map[e_mask] = INPUT_EMPTY
        local_map[w_mask] = INPUT_WALL

        i_mask = result < 0
        e_mask = result == 0
        w_mask = result > 0
        result[i_mask] = INPUT_UNKNOWN
        result[e_mask] = INPUT_EMPTY
        result[w_mask] = INPUT_WALL

        self.manager.maze.update_maze_matrix([mi_x, mi_y], local_map, result)

    def can_see_castle(self, me, info, other_castle: bool = False):
        """
        The can_see_castle function checks if the castle is in the local map of a given
        unit. The function takes three arguments: me, info, and castle. Me is a dictionary
        containing information about the unit that calls it (see below). Info is also a
        dictionary containing information about all of the units on the field (see below).
        Castle contains an integer value representing which team's castle should be checked for.

        :param self: Access the object's attributes and methods
        :param me: Access the information about me
        :param info: Pass the information about the game to your bot
        :param castle=0: Specify which castle to check for
        :return: True if the flag is in view of the castle, otherwise it returns false
        :doc-author: Trelent
        """
        find_team = self.team
        if other_castle:
            find_team = self.opposing_team
        if find_team not in info["flags"].keys():
            return False
        x = me['x']
        mi_x = x - me['view_radius']
        if mi_x < 0:
            mi_x = 0
        y = me['y']
        mi_y = y - me['view_radius']
        if mi_y < 0:
            mi_y = 0
        local_map = info['local_map']
        return mi_x < info['flags'][find_team][0] < x + local_map.shape[0] and \
            mi_y < info['flags'][find_team][1] < y + local_map.shape[1]

    def goto_castle(self, me, info, other_castle: bool = False):
        find_team = self.team
        if other_castle:
            find_team = self.opposing_team
        self.goto_position(me["position"], info['flags'][find_team], extra=80)

    def path_runner(self, route, default):
        if route.length > 0:
            if route.path.shape[0] > 2:
                self._goto_position(route.path[2, :])
            elif 2 >= route.path.shape[0] > 1:
                self._goto_position(route.path[1, :])
            else:
                self._goto_position(self.spiral_around_position(default, n=5 ** 2))
            return
        self._goto_position(self.spiral_around_position(default, n=5 ** 2))

    def _goto_position(self, position):
        self.heading = self.heading_from_vector(position - self._current_position)

    def goto_position(self, start_position, end_position, extra=None):
        start_position = parse_position(start_position)
        if self.manager.maze._board[start_position[0], start_position[1]] == BOARD_WALL:
            self.logger.info(f'Start position {start_position} is blocked, spiralling')
            start_position = self.spiral_around_position(start_position)
        end_position = parse_position(end_position)
        if self.manager.maze._board[end_position[0], end_position[1]] == BOARD_WALL:
            self.logger.info(f'End position {end_position} is blocked, spiralling')
            end_position = self.spiral_around_position(end_position)
        if len(self._waypoints.destination) < 2 \
                or self._r is not None \
                and np.hypot(self._r.start[0]-start_position[0], self._r.start[1]-start_position[1]) > 0.5*self.view_radius:
            self._r = self.manager.maze.solve_maze(start_position, end_position, extra=extra)
            self._r.view_distance = 3 * self.speed * self._dt
            self._waypoints.destination = self._r.reduced_route[1:]
        mini_point = self._waypoints.next_waypoint(start_position, tol=0.95 * self.speed * self._dt)
        if mini_point is None:
            mini_point = end_position
        if self.manager.maze._board[mini_point[0], mini_point[1]] == BOARD_WALL:
            self.logger.info(f'Truncated waypoint {mini_point} is blocked, spiralling')
            mini_point = self.spiral_around_position(mini_point)
            self._waypoints.pop_waypoint()
        self._goto_position(mini_point)

    def get_n_gem(self, me, info, n=1):
        gems = np.array([[x, y] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems_distance = np.array([[x - me["x"], y - me["y"]] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems = gems[np.apply_along_axis(lambda row: np.hypot(row[0], row[1]), axis=1, arr=gems_distance).argsort()]
        if n == 1:
            return gems[0, :]
        return gems[0:n, :]

    def explore_position(self, me, position, compute_radius: float = None):
        if compute_radius is None:
            compute_radius= self.view_radius * 2.5
        current = me["position"].copy()
        if np.hypot(me["position"][0] - position[0], me["position"][1] - position[1]) <= 0.95*self.speed*self._dt:
            self.logger.warn(f'Bypassing  routing for point: {position}')
            self.manager.route[me["name"]].pop_waypoint()
            self._goto_position(position)
            return
        if np.hypot(position[0] - current[0], position[1] - current[1]) > compute_radius:
            position = current + compute_radius * self.vector_from_heading(
                self.heading_from_vector([position[0] - current[0], position[1] - current[1]]))
        position = parse_position(position)
        self.goto_position(current, position, extra=200)

    def spiral_around_position(self, position, n=36 ** 2, value=BOARD_EMPTY):
        pop_waypoint = False
        pop_waypoint2 = False
        if np.all(position == self.manager.route[self.name].next_waypoint(self._current_position)):
            pop_waypoint = True
        if np.all(position == self._waypoints.next_waypoint(self._current_position)):
            pop_waypoint2 = True
        for ind, p in circle_around(position[0], position[1]):
            point = parse_position(p)
            if self.manager.maze._board[point[0], point[1]] == value:
                self.logger.info(f'Spiraler found point {point} (from {position})')
                if pop_waypoint:
                    self.manager.route[self.name].pop_waypoint()
                    self.logger.info(f'Spiraler popped waypoint {position} from route and appended {point}')
                    self.manager.route[self.name].destination.appendleft(point)
                if pop_waypoint2:
                    self._waypoints.pop_waypoint()
                    self.logger.info(f'Spiraler popped waypoint {position} from route and appended {point}')
                    self._waypoints._destination.appendleft(point)
                return point
            if ind > n:
                self.logger.info(f'Spiraler did not find valid {position}')
                return position

    def run(self, t: float, dt: float, info: dict):
        me = info['me']
        if self.first_run:
            self.name = me['name']
            self.logger = get_logger(f'{CREATOR}-{me["name"]}')
        self.update_map(me, info)
        self.speed = me["speed"]
        self._dt = dt
        self.view_radius = me["view_radius"]
        self._current_position = me["position"]
        self.stuck_evaluation(self._current_position)

    def stuck_evaluation(self, current_position):
        if len(self.previous_position) > 0:
            l = np.hypot(np.array(self.previous_position)[:, 0] - current_position[0],
                         np.array(self.previous_position)[:, 1] - current_position[1]
                         )
            if l[0] == 0 or np.all(l / l[0] == 1) and l[0] < 2 and len(l) > 8:
                self.logger.critical('Help, I think I am stuck... Running with random waypoints')
                pos = np.random.random(2)*10 + self.previous_position[0]
                self._waypoints.destination.appendleft(pos.astype(np.intc))

    def post_run(self, t: float, dt: float, info: dict):
        me = info['me']
        self.previous_position.appendleft(me['position'])
        self.previous_health = me['health']
