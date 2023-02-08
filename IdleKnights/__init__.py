__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.core.team import Team
from IdleKnights.logic.manager import Manager
from .constants import *
from IdleKnights.charaters import make_character
from IdleKnights.charaters.warrior import Warrior
from IdleKnights.charaters.seeker import Seeker


class MyTeam(Team):
    def reset_team(self):
        manager = Manager(self)
        for knight in self.values():
            knight.manager = manager


team = MyTeam(CREATOR,
              Arthur1=make_character(Seeker, index=0), Galahad1=make_character(Seeker, index=1),
              Lancelot1=make_character(Seeker, index=2))

team2 = MyTeam(CREATOR,
               Arthur2=make_character(Seeker, index=0), Galahad2=make_character(Seeker, index=1),
               Lancelot2=make_character(Seeker, index=2))
