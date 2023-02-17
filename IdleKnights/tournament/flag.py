__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights import IdleTeam
from IdleKnights.constants import CREATOR
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight

GAME_MODE = "flag"

knight_modifiers = {
    'gem_ratio': 1/2
}

team = IdleTeam(CREATOR,
                      Melchior=make_character(SpeedyKnight, index=0, mode=GAME_MODE),
                      Caspar=make_character(SpeedyKnight, index=1, mode=GAME_MODE, inject_kwargs=knight_modifiers),
                      Balthazar=make_character(SpeedyKnight, index=2, mode=GAME_MODE, inject_kwargs=knight_modifiers))
