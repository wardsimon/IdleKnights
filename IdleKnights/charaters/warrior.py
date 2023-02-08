__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.constants import np, NY, NX
from IdleKnights.logic.route import Waypoint
from .templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector

KIND = 'scout'


class Warrior(IdleTemplate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind=KIND, **kwargs)
        self.previous_gem = None

    def run(self, t: float, dt: float, info: dict):
        me = info['me']
        super().run(t, dt, info)
        if self.first_run:
            flag = np.array(info['flags'][self.team])
            extent = 100
            pts = np.array([[-extent, -extent], [extent, -extent], [extent, extent], [-extent, extent]])
            pts = pts + flag
            pts[:, 0] = np.clip(pts[:, 0], 5, NX-5)
            pts[:, 1] = np.clip(pts[:, 1], 5, NY-5)
            print(pts)
            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
            self.first_run = False
        if self.manager.override[me['name']] is not None:
            override_point = self.manager.override[me['name']]
            self.logger.warn(f"Routing overriden, going to {override_point}")
            self.explore_position(me, override_point)
            return
        if info["gems"]:
            gem = self.get_n_gem(me, info)
            if self.team == 'red':
                con = gem[0] < team_reflector(self.team, [400, 0])[0]
            else:
                con = gem[0] > team_reflector(self.team, [400, 0])[0]
            if con and np.hypot(me['position'][0] - gem[0], me['position'][1] - gem[1]) < 50:
                if self.previous_gem is not None and not np.all(self.previous_gem == gem):
                    self.logger.info(f'Gem {gem} added')
                    self.manager.route[me['name']].add_next_waypoint(gem)
                    self._waypoints.destination = []
                    self.previous_gem = gem
                if self.previous_gem is None:
                    self.previous_gem = gem
        if len(self.manager.route[me['name']].destination) == 0:
            flag = np.array(info['flags'][self.team])
            extent = 300
            pts = np.array([[-extent, -extent], [extent, -extent], [extent, extent], [-extent, extent]])
            pts = pts + flag
            pts[:, 0] = np.clip(pts[:, 0], 5, NX-5)
            pts[:, 1] = np.clip(pts[:, 1], 5, NY-5)
            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
        point = self.manager.route[me['name']].next_waypoint(me['position'])
        self.explore_position(me, point)
        self.post_run(t, dt, info)
