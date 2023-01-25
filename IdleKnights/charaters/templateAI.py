import numpy as np
from scipy.signal import convolve2d

from IdleKnights.constants import CREATOR, KERNEL, INPUT_UNKNOWN, INPUT_EMPTY, INPUT_WALL, BOARD_WALL, BOARD_EMPTY
from quest.knights.templateAI import TemplateAI
from IdleKnights.tools.logging import get_logger
from IdleKnights.tools.positional import circle_around, parse_position


class IdleTemplate(TemplateAI):

    manager = None
    number = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, **kwargs)
        self.previous_position = [0, 0]
        self.previous_health = 0
        self.destination = None
        self.first_run = True
        self.logger = get_logger(f'{CREATOR}-{self.__class__.__name__}{id(self)}')

    def update_map(self, me, info):
        fog_of_war = info['local_map'] < 0
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
        i_mask = result < 0
        e_mask = result == 0
        w_mask = result > 0
        result[i_mask] = INPUT_UNKNOWN
        result[e_mask] = INPUT_EMPTY
        result[w_mask] = INPUT_WALL
        self.manager.maze.update_maze_matrix([mi_x, mi_y], result)


    def can_see_castle(self, me, info, other_castle: bool=False):
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
        self.goto_position(me["position"], info['flags'][find_team], backup_position=info['flags'][find_team], extra=80)

    def path_runner(self, route, default):
        if route.length > 0:
            if route.path.shape[0] > 2:
                self._goto_position(route.path[2, :])
            elif route.path.shape[0] > 1:
                self._goto_position(route.path[1, :])
            else:
                self._goto_position(default)
            return
        self._goto_position(self.spiral_around_position(default, n= 5**2))

    def _goto_position(self, position):
        self.goto = [position[0], position[1]]

    def goto_position(self, start_position, end_position, backup_position=None, extra=None):
        start_position = parse_position(start_position)
        if self.manager.maze._board[start_position[0], start_position[1]] == BOARD_WALL:
            self.logger.info(f'Position {start_position} is blocked, spiralling')
            start_position = self.spiral_around_position(start_position)
        end_position = parse_position(end_position)
        if backup_position is None:
            backup_position = end_position
        else:
            backup_position = parse_position(backup_position)
        end_position = end_position.astype(np.intc)
        if self.manager.maze._board[end_position[0], end_position[1]] == BOARD_WALL:
            self.logger.info(f'Position {end_position} is blocked, spiralling')
            end_position = self.spiral_around_position(end_position)
        r = self.manager.maze.solve_maze(start_position, end_position, extra=extra)
        self.path_runner(r, backup_position)
    def goto_gem(self, me, info):
        gems = np.array([[x, y] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems_distance = np.array([[x-me["x"], y -me["y"]] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems = gems[np.apply_along_axis(lambda row: np.hypot(row[0], row[1]), axis=1, arr=gems_distance).argsort()]
        self.goto_position(me["position"], gems[0, :], backup_position=None, extra=40)
    def get_n_gem(self, me, info, n=1):
        gems = np.array([[x, y] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems_distance = np.array([[x-me["x"], y -me["y"]] for x, y in zip(info['gems']['x'], info['gems']['y'])])
        gems = gems[np.apply_along_axis(lambda row: np.hypot(row[0], row[1]), axis=1, arr=gems_distance).argsort()]
        if n == 1:
            return gems[0, :]
        return gems[0:n, :]

    def explore_position(self, me, position, D: float =None):
        if D is None:
            D = me['view_radius'] * 1.5
        current = me["position"].copy()
        if np.hypot(me["position"][0] - position[0], me["position"][1] - position[1]) < 1.5:
            self.logger.warn(f'Bypassing  routing for point: {position}')
            self.manager.route[me["name"]].pop_waypoint()
            self._goto_position(position)
            return
        position_bu = position.copy()
        if np.hypot(position[0]-current[0], position[1]-current[1]) > D:
            position = current + D*self.vector_from_heading(self.heading_from_vector([position[0]-current[0], position[1]-current[1]]))
        position = parse_position(position)
        self.goto_position(current, position, backup_position=position_bu, extra=200)

    def spiral_around_position(self, position, n=36**2, value=BOARD_EMPTY):
        for ind, p in circle_around(position[0], position[1]):
            point = parse_position(p)
            if self.manager.maze._board[point[0], point[1]] == value:
                self.logger.info(f'Spiraler found point {point} (from {position})')
                return point
            if ind > n:
                self.logger.info(f'Spiraler did not find valid {position}')
                return position

    def run(self, t: float, dt: float, info: dict):
        me = info['me']
        self.update_map(me, info)

    def post_run(self, t: float, dt: float, info: dict):
        me = info['me']
        self.previous_position = me['position']
        self.previous_health = me['health']

