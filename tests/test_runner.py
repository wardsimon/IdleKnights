__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import sys

from match import Match
from manager import make_team

from IdleKnights.charaters.templateAI import  team as TemplateTeam


match = Match(red_team=make_team(TemplateTeam),
              blue_team=make_team(TemplateTeam),
              best_of=3)

match.play(speedup=1, show_messages=False)