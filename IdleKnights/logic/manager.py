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


class Manager:

    def __init__(self, team: Team):
        # super().__init__(**team)
        self.maze = Maze(NX, NY)
        self.route = dict.fromkeys(team.keys())
        self.override = dict.fromkeys(team.keys(), None)
        self._others = {v: k for k, v in team.items()}
        self.waypoints = {k: WaypointStack() for k in team.keys()}
        self.king_health = None
        self.king_old_health = None
        self.king_hit_time = None

    def update_king_health(self, knight, info):
        current_t = knight.time_taken
        friends = info['friends']
        new_king_health = [friend['health'] for friend in friends if friend['name'].lower() == 'king']
        new_king_health = new_king_health[0] if len(new_king_health) > 0 else None
        if new_king_health is not None and self.king_old_health is not new_king_health:
            # The king is under attack
            self.king_old_health = int(self.king_health) if self.king_health is not None else 100
            self.king_health = new_king_health
            if self.king_hit_time is None or self.king_hit_time == 0:
                self.king_hit_time = current_t

    def king_saved(self):
        self.king_health = None
        self.king_hit_time = None
        self.king_old_health = None

    def others(self, knight_filter=None):
        if knight_filter is None:
            knight_filter = lambda item: True
        return {key: value for key, value in self._others.items() if knight_filter(key)}
