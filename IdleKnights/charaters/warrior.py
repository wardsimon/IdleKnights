__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.constants import np, NY
from IdleKnights.logic.route import Waypoint
from .templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector

def make_warrior(i: int):
    return type(Warrior.__name__, (Warrior,), {'number': i, '__old_cls__': Warrior})

KIND ='scout'


class Warrior(IdleTemplate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind=KIND, **kwargs)
        self.previous_gem = None

    def run(self, t: float, dt: float, info: dict):
        me = info['me']
        super().run(t, dt, info)
        if self.first_run:
            pts = [[100, 100], [300, 100], [300, NY - 100], [100, NY - 100]]
            wp = Waypoint([*[team_reflector(self.team, pt) for pt in pts], info['flags'][self.team]])
            self.manager.route[me['name']] = wp
            self.first_run = False
        if self.manager.override[me['name']] is not None:
            self.explore_position(me, self.manager.override[me['name']])
            return
        if info["gems"]:
            gem = self.get_n_gem(me, info)
            if gem[0] < 400 and np.hypot(me['position'][0] - gem[0], me['position'][1] - gem[1]) < 50:
                if self.previous_gem is not None and not np.all(self.previous_gem == gem):
                    self.logger.info(f'Gem {gem} added')
                    self.manager.route[me['name']].add_next_waypoint(gem)
                    self.previous_gem = gem
                if self.previous_gem is None:
                    self.previous_gem = gem
        if len(self.manager.route[me['name']].destination) == 0:
            self.manager.route[me['name']].add_next_waypoint(info['fountains'][self.team])
        point = self.manager.route[me['name']].next_waypoint(me['position'])
        self.explore_position(me, point)
        self.post_run(t, dt, info)
