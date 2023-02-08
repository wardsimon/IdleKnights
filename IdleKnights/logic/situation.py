__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import abc
import dataclasses
from typing import Dict, Tuple, Optional, List

import numpy as np

from IdleKnights import NY, NX
from IdleKnights.charaters.templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector


@dataclasses.dataclass
class Calculator:
    knight: IdleTemplate
    info: Dict[str, any]

    @abc.abstractmethod
    def calculate(self):
        pass

    def get_distance(self, x1, y1, x2, y2):
        return np.hypot(x1 - x2, y1 - y2)

    def others(self):
        return [value for key, value in self.knight.manager.others().items() if value is not self.knight.name]


@dataclasses.dataclass(init=False)
class Fighter(Calculator):
    health_ratio: float
    distance_ratio: float

    def __init__(self, knight: IdleTemplate, info: Dict[str, any],
                 health_ratio: float = 0.5, distance_ratio: float = 0.75):
        self.knight = knight
        self.info = info
        self.health_ratio = health_ratio
        self.distance_ratio = distance_ratio


    def calculate(self) -> Tuple[float, np.ndarray, Optional[List[IdleTemplate]]]:
        info = self.info
        me_info = info['me']
        knight = self.knight
        enemies = info['enemies']
        if len(enemies) == 0:
            return 0, np.array([0, 0]), None
        distance = np.array([np.hypot(*(knight._current_position - enemy['position'])) for enemy in enemies])
        ind = np.argmin(distance)

        enemy_distance = distance[ind]

        closest_enemy = enemies[ind]
        my_health = me_info['health']
        my_max_health = me_info['max_health']
        me_attack = me_info['attack']
        enemy_health = closest_enemy['health']
        enemy_max_health = closest_enemy['max_health']
        enemy_attack = closest_enemy['attack']

        my_view_radius = knight.view_radius
        enemy_view_radius = closest_enemy['view_radius']

        my_speed = knight.speed
        enemy_speed = closest_enemy['speed']

        my_cooldown = me_info['cooldown']
        enemy_cooldown = closest_enemy['cooldown']

        my_attack_block = np.floor(knight._current_position / 32)
        enemy_attack_block = np.floor(closest_enemy['position'] / 32)

        if knight._enemy_override is not None:
            my_destination = knight.manager.route[me_info['name']]._destination[1]
        else:
            my_destination = knight.manager.route[me_info['name']].next_destination

        my_best_vector = knight.heading_from_vector(knight._current_position - my_destination)
        enemy_vector = knight.heading_from_vector(knight._current_position - closest_enemy['position'])
        vector_component = 1 - np.abs(enemy_vector - my_best_vector) / 360
        position_distance = np.hypot(*(knight._current_position - my_destination))
        distance_component = 1 - (position_distance-enemy_distance) / position_distance
        disadvantage = np.sqrt(distance_component * vector_component)
        # print(disadvantage, distance_component, vector_component)

        # Check for cooldown
        if my_cooldown > 0:
            # Check if the enemy is on cooldown
            if enemy_cooldown > 0:
                # Who will be able to attack first?
                if my_cooldown < enemy_cooldown:
                    return disadvantage, closest_enemy['position'], None
            else:
                # Run away
                return 0, np.array([0, 0]), None

        # I'm too weak to attack
        if my_health / my_max_health < self.health_ratio:
            # Unless the enemy is too weak to attack
            if enemy_health - me_attack < 0 and my_health - enemy_attack > 0:
                return disadvantage, closest_enemy['position'], None
            return 0, np.array([0, 0]), None
        return disadvantage, closest_enemy['position'], None


@dataclasses.dataclass
class Positional(Calculator):

    def calculate(self) -> Tuple[float, np.ndarray, Optional[List[IdleTemplate]]]:
        knight = self.knight
        position = knight._current_position
        # This is the optimal position for the castle
        start_position = team_reflector(knight.team, [100, NY/2])

        # exponential decay
        f = 1 - np.exp(-np.abs(position - start_position)/(NX-200))
        return f[0]


@dataclasses.dataclass
class Harvester(Calculator):

    def calculate(self) -> Tuple[float, np.ndarray, Optional[List[IdleTemplate]]]:
        knight = self.knight
        position = knight._current_position
        me = self.info['me']
        f = 0.0
        gem = np.array([0, 0])
        if self.info["gems"]:
            gem = knight.get_n_gem(me, self.info)
            f = (2*knight._dt * knight.speed)/np.hypot(*(knight._current_position - gem))
        return f, gem, None


@dataclasses.dataclass
class Castler(Calculator):
    def calculate(self):
        knight = self.knight
        me = self.info['me']
        visible_castle = knight.can_see_castle(me, self.info, other_castle=True)
        position = self.info['flags'].get(knight.opposing_team, np.array([0, 0]))
        friends = None
        if visible_castle:
            friends = self.others()
        return float(visible_castle), position, friends


@dataclasses.dataclass
class MyCastler(Calculator):
    def calculate(self):
        knight = self.knight
        me = self.info['me']
        visible_castle = knight.can_see_castle(me, self.info, other_castle=False)
        if visible_castle:
            enemies = self.info['enemies']
            if len(enemies) == 0:
                visible_castle = False
            else:
                distance = np.array([np.hypot(*(self.info['flags'][knight.team] - enemy['position'])) for enemy in enemies])
                ind = np.argmin(distance)
                closest_enemy = enemies[ind]
                enemy_distance = distance[ind]
                my_distance = np.hypot(*(self.info['flags'][knight.team] - knight._current_position))
                my_speed = knight.speed
                enemy_speed = closest_enemy['speed']
                if enemy_distance * enemy_speed < 1.5 * my_distance * my_speed:
                    visible_castle = (enemy_distance * enemy_speed)/(my_distance * my_speed)
        position = self.info['flags'].get(knight.team)
        friends = None
        visible_castle = float(visible_castle)
        if visible_castle > 0:
            friends = self.others()
        return visible_castle, position, friends
