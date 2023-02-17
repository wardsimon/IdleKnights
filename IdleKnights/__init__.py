__author__ = 'github.com/wardsimon'
from . __version__ import __version__


from quest.core.team import Team
from IdleKnights.logic.manager import Manager


class IdleTeam(Team):
    def reset_team(self):
        manager = Manager(self)
        for knight in self.values():
            knight.manager = manager
