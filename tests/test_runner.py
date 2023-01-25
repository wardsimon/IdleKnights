__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from quest.core.match import Match
from quest.core.manager import make_team

from IdleKnights import team as AwsomeTeam
from IdleKnights import team2 as AwsomeTeam2
from quest.knights.exampleAI import team as ExampleTeam


match = Match(red_team=make_team(AwsomeTeam),
              blue_team=make_team(AwsomeTeam2),
              best_of=3)

match.play(speedup=1, show_messages=False)