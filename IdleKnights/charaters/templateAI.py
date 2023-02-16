from collections import deque, namedtuple

import numpy as np
from quest.core.manager import Manager
from scipy.signal import convolve2d
from types import MappingProxyType

from IdleKnights.constants import CREATOR, KERNEL, INPUT_UNKNOWN, INPUT_EMPTY, INPUT_WALL, BOARD_WALL, BOARD_EMPTY, NX, \
    NY, TIME, BLOCK_SIZE
from IdleKnights.logic.route import Waypoint
from IdleKnights.logic.route_generation.gradient_rtt import GradientMaze
from IdleKnights.logic.searching import general_search_points, CONVERTER
from IdleKnights.logic.situation import flag_game
from IdleKnights.tools.logging import get_logger
from IdleKnights.tools.positional import circle_around, parse_position, team_reflector

import abc
from quest.core.ai import BaseAI

Status = namedtuple('Status', ['position', 'time', 'dt', 'speed', 'view_radius'])


class TemplateAI(BaseAI):

    def __init__(self, *args, creator: str = None, kind: str = None, **kwargs):
        if creator is None or not isinstance(creator, str):
            raise AttributeError('The AI needs a `creator`')
        if kind is None or not isinstance(kind, str):
            raise AttributeError('The knight needs a `kind`')
        super().__init__(*args, creator=creator, kind=kind, **kwargs)

    @abc.abstractmethod
    def run(self, t: float, dt: float, info: dict):
        pass


class IdleTemplate(TemplateAI):
    manager = None
    number = None
    mode = None
    initial_mode = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, **kwargs)
        self.initial_health = None
        self.backup_waypoints = None
        self.name = None
        self._current_position = None
        self._r = None
        self._dt = None
        self.view_radius = None
        self.control_parameters = dict()
        self.control_parameters_base = dict()
        self.previous_position = deque(maxlen=10)
        self.previous_health = 0
        self.speed = 0
        self.time_taken = 0
        self.destination = None
        self.first_run = True
        self._waypoints = Waypoint()
        self.logger = None
        self._status = {'going_to_castle':   False,
                        'going_healing':     False,
                        'going_to_fountain': False,
                        'going_to_gem':      False,
                        'going_to_enemy':    False,
                        'going_exploring':   False,
                        'castle_override':   False
                        }
        if self.mode is None:
            self.mode = 'flag'
        if self.number is None:
            self.number = 0
        if self.manager is None:
            self.manager = Manager(self)

    def reset_status(self):
        for key in self._status:
            self._status[key] = False

    def set_status(self, status, field: bool = True):
        self.reset_status()
        self._status[status] = field

    @property
    def status(self):
        return MappingProxyType(self._status)

    def update_map(self, me, info, maze = None):

        local_map = info['local_map']
        local_map[local_map == 2] = 0
        x = me['x']
        mi_x = x - (me['view_radius'] + 2)
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
        if maze is None:
            self.manager.maze.update_maze_matrix([mi_x, mi_y], local_map, result)
        else:
            maze.update_maze_matrix([mi_x, mi_y], local_map, result)

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
        d = CONVERTER(self, info)
        if other_castle:
            find_team = self.opposing_team
        if find_team not in d.keys() or (isinstance(d[find_team], np.ndarray) and d[find_team].size == 0):
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
        return mi_x < d[find_team][0] < x + local_map.shape[0] and \
            mi_y < d[find_team][1] < y + local_map.shape[1]

    def goto_castle(self, me, info, other_castle: bool = False, override_position=None):
        find_team = self.team
        if other_castle:
            find_team = self.opposing_team
        if override_position is None:
            position = CONVERTER(self, info)[find_team]
        else:
            position = override_position
        position = np.array(position)
        this_offset = np.zeros_like(position)
        friends = info['friends']
        knights_positions = [knight["position"] for knight in friends if knight["name"] != me["name"]]
        # Are any of the knights in attack position?
        if not flag_game(info):
            kings_block = np.floor(position / BLOCK_SIZE) * BLOCK_SIZE
            castle_type = info['castle']['direction']
            if castle_type == 0:
                offset = np.array([(0, 1), (-1, 0), (0, -1)])
            elif castle_type == 1:
                offset = np.array([(1, 0), (0, -1), (-1, 0)])
            elif castle_type == 2:
                offset = np.array([(-1, 0), (0, 1), (0, -1)])
            else:
                offset = np.array([(-1, 0), (0, 1), (1, 0)])
            if self.team == 'blue':
                offset[:, 0] = -1 * offset[:, 0]
            my_index = list(self.manager.override.keys()).index(self.name)
            OFFSET_BLOCK = BLOCK_SIZE / 2
            if np.any(np.all(kings_block == np.floor(np.array(knights_positions) / BLOCK_SIZE) * BLOCK_SIZE,
                             axis=1)) or \
                    info["me"]["cooldown"] > 0:
                this_offset = np.floor((OFFSET_BLOCK + self._dt * self.speed * 2) * np.array(offset[my_index]))
                self.logger.warn(f"Routing overriden, going out of attack position {position + this_offset}")
        # Now we check if we have enemies in the area
        enemies = info['enemies'].copy()
        enemies = [enemy for enemy in enemies if enemy["name"] != "King"]
        y_min = int(position[1] - 256 if position[1] - 256 > 0 else 0)
        y_max = int(position[1] + 256 if position[1] + 256 < NY else NY)
        my_block = np.floor(me["position"] / BLOCK_SIZE) * BLOCK_SIZE
        if enemies and \
                (TIME - self.time_taken) > TIME/5 and \
                len(enemies) > 1 and \
                (np.any([enemy['cooldown'] < 0.75 for enemy in enemies]) or
                 np.any([np.linalg.norm(enemy['position'] - self._current_position) < 2*(2*BLOCK_SIZE**2)**0.5 and
                         enemy['cooldown'] == 0 for enemy in enemies])):
            enemy_positions = [enemy["position"] for enemy in enemies]
            if self.team == 'red':
                # We don't copy as we just read it
                map = self.manager.maze._board[NX - 256:, y_min:y_max]
                gm = GradientMaze(*map.shape, map)
                start_point = np.array(me["position"])
                start_point[0] = 256 - (NX - start_point[0])
                start_point[1] = start_point[1] - y_min
                end_point = np.array(position + this_offset)
                end_point[0] = 256 - (NX - end_point[0])
                end_point[1] = end_point[1] - y_min
            else:
                map = self.manager.maze._board[0:256, y_min:y_max]
                gm = GradientMaze(*map.shape, map)
                start_point = np.array(me["position"])
                start_point[1] = start_point[1] - y_min
                end_point = np.array(position + this_offset)
                end_point[1] = end_point[1] - y_min
            f1 = gm.combined_potential(end_point, attractive_coef=1/200)
            map = np.zeros_like(gm.map)
            for idx, enemy_position in enumerate(enemy_positions):
                enemy_block = np.floor(enemy_position / BLOCK_SIZE) * BLOCK_SIZE
                block_overlap = np.all(my_block == enemy_block)
                if enemies[idx]['cooldown'] < 0.5 or block_overlap:
                    # It can't attack us, so we attack
                    if self.team == 'red':
                        this_x = 256 - NX + enemy_position[0]
                    else:
                        this_x = enemy_position[0]
                    this_y = enemy_position[1]
                    this_y = this_y - y_min
                    off = int(BLOCK_SIZE/8)
                    # this_x = int(np.floor(this_x/BLOCK_SIZE)*BLOCK_SIZE)
                    # this_y = int(np.floor(this_y/BLOCK_SIZE)*BLOCK_SIZE)
                    map[this_x-off:this_x+off, this_y-off:this_y+off] = 1
            gm.map = map
            f2 = gm.combined_potential(end_point, attractive_coef=0, repulsive_coef=300)
            route = gm.gradient_planner(f1+f2, start_point, end_point, 15)
            idx = len(route.path)-1 if len(route.path) < 5 else 4
            if self.team == 'red':
                this_offset = np.array(route.path[idx, :] + [NX-256, y_min-1], dtype=np.intc) - position
            else:
                this_offset = np.array(route.path[idx, :] + [0, y_min-1], dtype=np.intc) - position
        position += this_offset.astype(np.intc)
        self.goto_position(self._current_position, position, extra=200)

    @staticmethod
    def array_row_intersection(a, b):
        tmp = np.prod(np.swapaxes(a[:, :, None], 1, 2) == b, axis=2)
        return a[np.sum(np.cumsum(tmp, axis=0) * tmp == 1, axis=1).astype(bool)]

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
                and np.hypot(self._r.start[0] - start_position[0],
                             self._r.start[1] - start_position[1]) > 0.5 * self.view_radius:
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
            compute_radius = self.view_radius * 2.5
        current = me["position"].copy()
        if np.hypot(me["position"][0] - position[0], me["position"][1] - position[1]) <= 0.95 * self.speed * self._dt:
            self.logger.warn(f'Bypassing  routing for point: {position}')
            self.manager.route[me["name"]].pop_waypoint()
            position = parse_position(position)
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
            self.initial_health = me['max_health']
        self.update_map(me, info)
        self.speed = me["speed"]
        self._dt = dt
        self.view_radius = me["view_radius"]
        self._current_position = me["position"]
        self.stuck_evaluation(self._current_position)
        self.manager.update_king_health(self, info)
        if self.first_run:
            if self.initial_mode is None:
                pts, backup_pts = general_search_points(self, info, self.__class__.__name__)
            else:
                pts, backup_pts = self.initial_mode(info, self.__class__.__name__)
            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
            self.backup_waypoints = backup_pts
            self.first_run = False
            self.set_status('going_exploring')

    def stuck_evaluation(self, current_position):
        if len(self.previous_position) > 0:
            l = np.hypot(np.array(self.previous_position)[:, 0] - current_position[0],
                         np.array(self.previous_position)[:, 1] - current_position[1]
                         )
            if l[0] == 0 or np.all(l / l[0] == 1) and l[0] < 2 and len(l) > 8:
                self.logger.critical('Help, I think I am stuck... Running with random waypoints')
                pos = np.random.random(2) * 10 + self.previous_position[0]
                self._waypoints.destination.appendleft(pos.astype(np.intc))

    def post_run(self, t: float, dt: float, info: dict):
        me = info['me']
        self.previous_position.appendleft(me['position'])
        self.previous_health = me['health']
        self.time_taken = t

    def run_override(self, info, me):
        if self.team == 'red':
            pos_log = self._current_position[0] < NX/2
        else:
            pos_log = self._current_position[0] > NX/2
        time1_log: bool = self.time_taken > TIME*.35 and list(self.manager.override.keys())[0] == self.name
        time2_log: bool = self.time_taken > TIME*.55 and not info['enemies'] and pos_log
        if pos_log and (time1_log or time2_log):
            self.control_parameters = self.control_parameters_base
            self.manager.override[self.name] = None
            pts, backup_pts = general_search_points(self, info, self.__class__.__name__)
            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
            self.backup_waypoints = backup_pts
            return
        override_point = self.manager.override[self.name]
        reset_run = False
        if override_point is not None:
            position, message, setter_name = override_point
            friends: list = info['friends']
            friend_names = [friend['name'] for friend in friends]
            friends_dict = {friend['name']: friend for friend in friends}
            # Check to see if he's dead and can continue giving commands
            if setter_name in friend_names:
                if message == "going_to_castle":
                    self.logger.warn(f"Routing overriden, going to castle {position}")
                    self.goto_castle(me, info, other_castle=True, override_position=position)
                elif message == "going_healing":
                    if friends_dict[setter_name]['health']/friends_dict[setter_name]['max_health'] > .75:
                        self.logger.warn(f"Healing complete {setter_name}")
                        self.manager.override[self.name] = None
                        return False
                    self.logger.warn(f"Routing overriden, going to heal {position}")
                    # Did I set this override?
                    if setter_name == self.name:
                        healers = [value for value in info['friends'] if value['kind'] == 'healer']
                        if len(healers) == 0:
                            self.manager.override[self.name] = None
                        healer_distances = [np.hypot(*(healer['position'] - self._current_position)) for healer in
                                            healers]
                        closest_healer = healers[np.argmin(healer_distances)]
                        healer_distance = np.min(healer_distances)
                        if healer_distance < closest_healer['view_radius']/1.5:
                            self.logger.warn(f"Close enough to healer, going to heal")
                            self.manager.override[self.name] = None
                            return False
                    self.explore_position(me, position)
                elif message == "going_to_fountain":
                    if me['health']/me['max_health'] > .75:
                        self.logger.warn(f"Healing complete {setter_name}")
                        self.manager.override[self.name] = None
                        return False
                else:
                    self.logger.warn(f"Routing overriden, going to {position}")
                    self.explore_position(me, position)
                reset_run = True
            else:
                if message == 'going_to_castle':
                    # We do want to go to the castle after all!
                    self.manager.route[me['name']].destination.appendleft(position)
                self.manager.override[self.name] = None
        return reset_run
