from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import abc
import dataclasses
from typing import Dict, Tuple, Optional, List, TYPE_CHECKING

import numpy as np

from IdleKnights import NY, NX, BLOCK_SIZE, TIME
from IdleKnights.logic.route_generation.gradient_rtt import GradientMaze

if TYPE_CHECKING:
    from IdleKnights.charaters.templateAI import IdleTemplate
from IdleKnights.logic.searching import CONVERTER
from IdleKnights.tools.positional import team_reflector


def flag_game(info: dict):
    """
    Quickly determine which game we're in
    """
    return 'flags' in info.keys()


@dataclasses.dataclass
class Calculator:
    """
    Base class for logic
    """
    knight: IdleTemplate
    info: Dict[str, any]

    @abc.abstractmethod
    def calculate(self):
        pass

    def get_distance(self, x1, y1, x2, y2):
        return np.hypot(x1 - x2, y1 - y2)

    def others(self):
        return [value for key, value in self.knight.manager.others().items() if value is not self.knight.name]

    def others_of_class(self, class_name: str):
        return [value for value in self.info['friends'] if value['kind'] == class_name]

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
        position = self.knight._current_position
        me_info = info['me']
        knight = self.knight
        enemies = info['enemies']
        if knight.team == 'red':
            be_smart = knight._current_position[0] > NX - 256
        else:
            be_smart = knight._current_position[0] < 256
        if be_smart and (TIME - knight.time_taken) > TIME/5:
            enemies = [enemy for enemy in enemies if enemy["name"] != "King"]
            attempted_position = knight.manager.route[knight.name].next_waypoint(knight._current_position)
            enemy_positions = [enemy["position"] for enemy in enemies]
            y_min = attempted_position[1] - 256 if attempted_position[1] - 256 > 0 else 0
            y_max = attempted_position[1] + 256 if attempted_position[1] + 256 < NY else NY
            if knight.team == 'red':
                # We don't copy as we just read it
                map = knight.manager.maze._board[NX - 256:, y_min:y_max]
                gm = GradientMaze(*map.shape, map)
                start_point = np.array(position)
                start_point[0] = 256 - (NX - start_point[0])
                start_point[1] = start_point[1] - y_min
                end_point = np.array(attempted_position)
                end_point[0] = 256 - (NX - end_point[0])
                end_point[1] = end_point[1] - y_min
            else:
                map = knight.manager.maze._board[0:256, y_min:y_max]
                gm = GradientMaze(*map.shape, map)
                start_point = np.array(position)
                start_point[1] = start_point[1] - y_min
                end_point = np.array(attempted_position)
                end_point[1] = end_point[1] - y_min
            f1 = gm.combined_potential(end_point, attractive_coef=1/200)
            map = np.zeros_like(gm.map)
            for idx, enemy_position in enumerate(enemy_positions):
                if enemies[idx]['cooldown'] < 0.5:
                    # It can't attack us, so we attack
                    if knight.team == 'red':
                        this_x = 256 - NX + enemy_position[0]
                    else:
                        this_x = enemy_position[0]
                    this_y = enemy_position[1]
                    this_y = this_y - y_min
                    this_x = int(np.floor(this_x/BLOCK_SIZE)*BLOCK_SIZE)
                    this_y = int(np.floor(this_y/BLOCK_SIZE)*BLOCK_SIZE)
                    map[this_x:this_x+BLOCK_SIZE, this_y:this_y+BLOCK_SIZE] = 1
            gm.map = map
            f2 = gm.combined_potential(end_point, attractive_coef=0, repulsive_coef=300)
            route = gm.gradient_planner(f1+f2, start_point, end_point, 700)
            if route.path.shape[0] < 10:
                # We can't do anything :-/
                return 0, None, None
            return 0.5, route.path[9, :], None
        else:
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

            if knight._enemy_override is not None and len(knight.manager.route[me_info['name']]._destination) > 1:
                my_destination = knight.manager.route[me_info['name']]._destination[1]
            else:
                my_destination = knight.manager.route[me_info['name']].next_destination
            if my_destination is None:
                return 0, np.array([0, 0]), None
            my_best_vector = knight.heading_from_vector(knight._current_position - my_destination)
            enemy_vector = knight.heading_from_vector(knight._current_position - closest_enemy['position'])
            vector_component = 1 - np.abs(enemy_vector - my_best_vector) / 360
            position_distance = np.hypot(*(knight._current_position - my_destination))
            distance_component = 1 - (position_distance - enemy_distance) / position_distance
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
        position = knight._current_position[0]
        # This is the optimal position for the castle
        start_position = team_reflector(knight.team, [100, NY / 2])[0]
        end_position = team_reflector(knight.team, [NX - 100, NY / 2])[0]
        x = np.abs(position / (end_position - start_position))
        if start_position > end_position:
            x = np.abs(x - 1)
        # exponential decay
        f = 2 * (1 - np.exp(-np.log(2) * x))
        return f

@dataclasses.dataclass
class KingUnderAttack(Calculator):

    def calculate(self) -> Tuple[float, np.ndarray, Optional[List[IdleTemplate]]]:
        knight = self.knight
        friends = self.info['friends']
        king = [friend for friend in friends if friend['name'] == 'King']
        king = king[0]
        position = np.array(king['position'])
        if knight.manager.king_hit_time is not None and knight.manager.king_hit_time > 0:
            king_attacked_at = knight.manager.king_hit_time
            distance = np.hypot(*(position - knight._current_position))
            speed = knight.speed
            eta = speed / distance
            king_health = knight.manager.king_health
            # assume the king will be hit again in 3 seconds.
            if eta < 3 * king_health/30:
                # He's dead, Jim.
                print(f'King is probably dead. ETA: {eta}, Time left: {3 * king_health/30}')
                return 0, position, None
            else:
                # Do a sanity check
                dt = knight.time_taken - king_attacked_at
                if dt > 2 * 3 * king_health / 30:
                    knight.manager.king_saved()
                    print(f'King is probably saved. ETA: {eta}, Time left: {3 * king_health / 30}')
                    # Well, he's dead or somehow the king is not being attacked.
                    return 0, position, None
                print(f'King is in need of help. ETA: {eta}, Time left: {3 * king_health/30}')
                return 1, position, None
        return 0, position, None

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
            divisor = np.hypot(*(position - gem))
            if divisor < 1E-5:
                divisor = 1E-3
            f = (2 * knight._dt * knight.speed) / divisor
        return f, gem, None


@dataclasses.dataclass
class CallHealer(Calculator):

    def calculate(self):
        knight = self.knight
        me = self.info['me']
        if me['health']/knight.initial_health > 0.25:
            return 0, np.array([0, 0]), None
        friends = {friend['name']: friend for friend in self.info['friends']}
        healers = [healer for healer in self.others_of_class('healer') if healer['name'] in friends.keys()]
        if len(healers) == 0:
            return 0, np.array([0, 0]), None
        healer_distances = [np.hypot(*(healer['position'] - knight._current_position)) for healer in healers]
        closest_healer = healers[np.argmin(healer_distances)]
        healer_distance = np.min(healer_distances)
        if healer_distance/2 > 150 * knight.speed * knight._dt:
            return 0, np.array([0, 0]), None
        else:
            knight_position = np.array(knight._current_position)
            healer_position = np.array(closest_healer['position'])
            pos_diff = knight.vector_from_heading(knight.heading_from_vector(knight_position - healer_position)) * knight.view_radius/1.5
            return 1, knight_position + pos_diff, closest_healer['name']



@dataclasses.dataclass
class Castler(Calculator):
    def calculate(self):
        if flag_game(self.info):
            return castler_flag(self)
        else:
            return castler_king(self)


def castler_flag(calc):
    knight = calc.knight
    me = calc.info['me']
    visible_castle = knight.can_see_castle(me, calc.info, other_castle=True)
    position = CONVERTER(knight, calc.info).get(knight.opposing_team, np.array([0, 0]))
    if len(position) == 0:
        position = np.array([0, 0])
    friends = None
    if visible_castle:
        friends = calc.others()
    return float(visible_castle), position, friends


def castler_king(calc):
    knight = calc.knight
    me = calc.info['me']
    visible_castle = knight.can_see_castle(me, calc.info, other_castle=True)
    position = CONVERTER(knight, calc.info).get(knight.opposing_team, np.array([0, 0]))
    if len(position) == 0:
        position = np.array([0, 0])
    friends = None
    if visible_castle:
        friends = calc.others()
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
                distance = np.array(
                    [np.hypot(*(CONVERTER(knight, self.info)[knight.team] - enemy['position'])) for enemy in enemies])
                ind = np.argmin(distance)
                closest_enemy = enemies[ind]
                enemy_distance = distance[ind]
                my_distance = np.hypot(*(CONVERTER(knight, self.info)[knight.team] - knight._current_position))
                my_speed = knight.speed
                enemy_speed = closest_enemy['speed']
                if enemy_distance * enemy_speed < 1.5 * my_distance * my_speed:
                    visible_castle = (enemy_distance * enemy_speed) / (my_distance * my_speed)
        position = CONVERTER(knight, self.info).get(knight.team)
        friends = None
        visible_castle = float(visible_castle)
        if visible_castle > 0:
            friends = self.others()
        return visible_castle, position, friends
