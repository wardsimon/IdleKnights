__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np

from quest.core.match import Match
from quest.core.manager import make_team

from IdleKnights import IdleTeam
from IdleKnights.constants import CREATOR
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight
from IdleKnights.charaters.castlekiller import DeadlyKnight
from IdleKnights.logic.searching import king_defender

ANGRY = {
    'health_ratio':   0.15,
    'distance_ratio': 0.1,
    'fight_ratio':    0.2,
    'gem_ratio':      1/2,
}

AwsomeTeam = IdleTeam(CREATOR,
                Caspar=make_character(DeadlyKnight, index=0, mode='king', initial_mode=king_defender, inject_kwargs=ANGRY),
                Melchior=make_character(DeadlyKnight, index=0, mode='king', initial_mode=king_defender,
                                        inject_kwargs=ANGRY),
                Balthazar=make_character(DeadlyKnight, index=1, mode='king', initial_mode=king_defender, inject_kwargs=ANGRY))

AwsomeTeam2 = IdleTeam(CREATOR,
                       Ruohtta=make_character(SpeedyKnight, index=0, mode='king'),
                       Parnashavari=make_character(DeadlyKnight, index=1, mode='king'),
                       Matarajin=make_character(DeadlyKnight, index=0, mode='king'))

Awsome = [AwsomeTeam, AwsomeTeam2]
indexes = np.random.choice(2, 2, replace=False)

match = Match(red_team=make_team(Awsome[indexes[0]]),
              blue_team=make_team(Awsome[indexes[1]]),
              best_of=3,
              game_mode='king')

match.play(speedup=1.25, show_messages=False)
