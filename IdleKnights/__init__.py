__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.core.team import Team
from IdleKnights.logic.manager import Manager
from .constants import *
from IdleKnights.charaters import make_character
from IdleKnights.charaters.warrior import CastleKiller
from IdleKnights.charaters.castleseeker import CastleSeeker


class MyTeam(Team):
    def reset_team(self):
        manager = Manager(self)
        for knight in self.values():
            knight.manager = manager


team = MyTeam(CREATOR,
              Melchior=make_character(CastleSeeker, index=0, mode='flag'), Caspar=make_character(CastleSeeker, index=1, mode='flag'),
              Balthazar=make_character(CastleSeeker, index=2, mode='flag'))

team2 = MyTeam(CREATOR,
               Ruohtta=make_character(CastleSeeker, index=0, mode='flag'), Parnashavari=make_character(CastleSeeker, index=1, mode='flag'),
               Matarajin=make_character(CastleSeeker, index=2, mode='flag'))

team3 = MyTeam(CREATOR,
              Melchior=make_character(CastleSeeker, index=0, mode='king'), Caspar=make_character(CastleKiller, index=0, mode='king'),
              Balthazar=make_character(CastleKiller, index=1, mode='king'))

team4 = MyTeam(CREATOR,
               Ruohtta=make_character(CastleSeeker, index=0, mode='king'), Parnashavari=make_character(CastleKiller, index=1, mode='king'),
               Matarajin=make_character(CastleSeeker, index=2, mode='king'))
