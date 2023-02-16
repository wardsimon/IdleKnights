__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.core.match import Match
from quest.core.manager import make_team

from IdleKnights import IdleTeam
from IdleKnights.constants import CREATOR
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight


AwsomeTeam = IdleTeam(CREATOR,
                      Melchior=make_character(SpeedyKnight, index=0, mode='flag', inject_kwargs={'gem_ratio': 1/2}),
                      Caspar=make_character(SpeedyKnight, index=1, mode='flag', inject_kwargs={'gem_ratio': 1/2}),
                      Balthazar=make_character(SpeedyKnight, index=2, mode='flag', inject_kwargs={'gem_ratio': 1/2}))

AwsomeTeam2 = IdleTeam(CREATOR,
                       Ruohtta=make_character(SpeedyKnight, index=0, mode='flag'),
                       Parnashavari=make_character(SpeedyKnight, index=1, mode='flag'),
                       Matarajin=make_character(SpeedyKnight, index=2, mode='flag'))


match = Match(red_team=make_team(AwsomeTeam),
              blue_team=make_team(AwsomeTeam2),
              best_of=1,
              game_mode='flag')

match.play(speedup=1.25, show_messages=False)