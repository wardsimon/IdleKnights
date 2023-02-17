__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights import IdleTeam
from IdleKnights.constants import CREATOR
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight
from IdleKnights.charaters.castlekiller import DeadlyKnight


GAME_MODE = "king"

team = IdleTeam(CREATOR,
                       Ruohtta=make_character(SpeedyKnight, index=0, mode=GAME_MODE),
                       Parnashavari=make_character(DeadlyKnight, index=1, mode=GAME_MODE),
                       Matarajin=make_character(DeadlyKnight, index=0, mode=GAME_MODE))
