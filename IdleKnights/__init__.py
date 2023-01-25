__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.knights.exampleAI import Team, ExampleWarrior
from IdleKnights.logic.manager import Manager
from .constants import *
from IdleKnights.charaters.warrior import make_warrior
from IdleKnights.charaters.seeker import make_seeker

class MyTeam(Team):
    def reset_team(self):
        manager = Manager(team)
        for knight in self.values():
            knight.manager = manager


team = MyTeam(CREATOR,
            Arthur=make_seeker(0), Galahad=make_seeker(1), Lancelot=make_warrior(0))

team2 = MyTeam(CREATOR,
            Arthur=make_seeker(0), Galahad=make_warrior(1), Lancelot=make_warrior(0))