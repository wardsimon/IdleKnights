__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np

from quest.core.match import Match
from quest.core.manager import make_team

from IdleKnights import IdleTeam
from IdleKnights.constants import CREATOR
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight

GAME_MODE = "flag"
SPEEDUP = 1.25

knight_modifiers = {
    'gem_ratio': 1/2
}

AwsomeTeam = IdleTeam(CREATOR,
                      Melchior=make_character(SpeedyKnight, index=0, mode=GAME_MODE),
                      Caspar=make_character(SpeedyKnight, index=1, mode=GAME_MODE, inject_kwargs=knight_modifiers),
                      Balthazar=make_character(SpeedyKnight, index=2, mode=GAME_MODE, inject_kwargs=knight_modifiers))

AwsomeTeam2 = IdleTeam(CREATOR,
                       Ruohtta=make_character(SpeedyKnight, index=0, mode=GAME_MODE),
                       Parnashavari=make_character(SpeedyKnight, index=1, mode=GAME_MODE),
                       Matarajin=make_character(SpeedyKnight, index=2, mode=GAME_MODE))

Awsome = [AwsomeTeam, AwsomeTeam2]
indexes = np.random.choice(2, 2, replace=False)

match = Match(red_team=make_team(Awsome[indexes[0]]),
              blue_team=make_team(Awsome[indexes[1]]),
              best_of=1,
              game_mode=GAME_MODE)

match.play(speedup=SPEEDUP, show_messages=False)
