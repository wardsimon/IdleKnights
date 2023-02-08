from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.constants import NX, NY
from IdleKnights.logic.Maze import Maze
from IdleKnights.logic.route import WaypointStack
from collections import UserDict
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from quest.core.team import Team

# class Manager(UserDict):
class Manager:

    def __init__(self, team: Team):
        # super().__init__(**team)
        self.maze = Maze(NX, NY)
        self.route = dict.fromkeys(team.keys())
        self.override = dict.fromkeys(team.keys(), None)
        self._others = {v: k for k, v in team.items()}
        self.waypoints = {k: WaypointStack() for k in team.keys()}

    def others(self, filter=None):
        if filter is None:
            filter = lambda item: True
        return {key: value for key, value in self._others.items() if filter(key)}

    # def __getitem__(self, key):
    #     pass
