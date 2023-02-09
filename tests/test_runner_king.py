__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.core.match import Match
from quest.core.manager import make_team

from IdleKnights import team3 as AwsomeTeam
from IdleKnights import team4 as AwsomeTeam2


match = Match(red_team=make_team(AwsomeTeam),
              blue_team=make_team(AwsomeTeam2),
              best_of=1,
              game_mode='king')

match.play(speedup=1.25, show_messages=False)
