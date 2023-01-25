__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.logic.route import Waypoint
from IdleKnights.constants import NX, NY
from .templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector

def make_seeker(i: int):
    return type(Seeker.__name__, (Seeker, ), {'number': i, '__old_cls__': Seeker})

KIND = 'healer'

class Seeker(IdleTemplate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind=KIND, **kwargs)

    def run(self, t: float, dt: float, info: dict):
        super().run(t, dt, info)
        me = info['me']
        if self.manager.override[me['name']] is not None:
            self.explore_position(me, self.manager.override[me['name']])
            return
        if self.first_run:
            pts = [[NX-100, NY/4 + 1*NY*self.number/2], [NX-100, 3*NY/4 - 2*NY*self.number/4]]
            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
            self.first_run = False
        if self.can_see_castle(me, info, other_castle=True):
            # f = lambda _cls: getattr(_cls, '__old_cls__', _cls) == getattr(self.__class__, '__old_cls__', self.__class__)
            others = [value for key, value in self.manager.others().items() if value is not me['name']]
            for name in others:
                self.manager.override[name] = np.array(info['flags'][self.opposing_team])
            self.goto_castle(me, info, other_castle=True)
        else:
            point = self.manager.route[me['name']].next_waypoint(me['position'])
            self.explore_position(me, point)
            self.post_run(t, dt, info)
