__author__ = 'github.com/wardsimon'
from . __version__ import __version__


from quest.core.team import Team
from IdleKnights.logic.manager import Manager
from .constants import *
from IdleKnights.charaters import make_character
from IdleKnights.charaters.warrior import CastleKiller
from IdleKnights.charaters.castleseeker import CastleSeeker
from IdleKnights.logic.searching import king_defender

class IdleTeam(Team):
    def reset_team(self):
        manager = Manager(self)
        for knight in self.values():
            knight.manager = manager


ANGRY = {
    'health_ratio':   0.15,
    'distance_ratio': 0.1,
    'fight_ratio':    0.2,
    'gem_ratio':      1/2,
}

team = IdleTeam(CREATOR,
              Melchior=make_character(CastleSeeker, index=0, mode='flag'),
              Caspar=make_character(CastleSeeker, index=1, mode='flag'),
              Balthazar=make_character(CastleSeeker, index=2, mode='flag'))

team2 = IdleTeam(CREATOR,
               Ruohtta=make_character(CastleSeeker, index=0, mode='flag'),
               Parnashavari=make_character(CastleSeeker, index=1, mode='flag'),
               Matarajin=make_character(CastleSeeker, index=2, mode='flag'))

team3 = IdleTeam(CREATOR,
                Caspar=make_character(CastleKiller, index=0, mode='king', initial_mode=king_defender, inject_kwargs=ANGRY),
                Melchior=make_character(CastleSeeker, index=0, mode='king', initial_mode=king_defender,
                                         inject_kwargs=ANGRY),
                Balthazar=make_character(CastleKiller, index=1, mode='king', initial_mode=king_defender, inject_kwargs=ANGRY))

team4 = IdleTeam(CREATOR,
               Ruohtta=make_character(CastleSeeker, index=1, mode='king'),
               Parnashavari=make_character(CastleKiller, index=1, mode='king'),
               Matarajin=make_character(CastleKiller, index=0, mode='king'))
