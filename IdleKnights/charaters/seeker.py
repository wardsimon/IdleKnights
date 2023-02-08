__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from IdleKnights.logic.route import Waypoint
from IdleKnights.constants import np, NX, NY
from .templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector
from ..logic.situation import Fighter, Positional, Harvester, Castler

KIND = 'healer'


class Seeker(IdleTemplate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind=KIND, **kwargs)
        self._enemy_override = None
        self.previous_gem = None

    def run(self, t: float, dt: float, info: dict):
        super().run(t, dt, info)
        me = info['me']
        if self.manager.override[me['name']] is not None:
            override_point = self.manager.override[me['name']]
            self.logger.warn(f"Routing overriden, going to {override_point}")
            self.explore_position(me, override_point)
            return
        if self.first_run:
            # How many seekers are there?
            n = len([k for k in self.manager._others.keys() if 'Seeker' in k.__name__])
            # Get the flag position
            target = np.array(info['flags'][self.team])
            pts = []
            if target[1] / 2 > NY / 2:
                pts.append([NX - self.view_radius - 50,
                            NY - 0.5 * self.view_radius - self.number * (NY - self.view_radius) / n])
                pts.append([NX - self.view_radius - 50,
                            NY - 0.5 * self.view_radius - (self.number + 1) * (NY - self.view_radius) / n])
                pts.append([NX - self.view_radius - 50, NY - 0.5 * self.view_radius])
            else:
                pts.append(
                    [NX - self.view_radius - 50, 0.5 * self.view_radius + self.number * (NY - self.view_radius) / (n)])
                pts.append([NX - self.view_radius - 50,
                            0.5 * self.view_radius + (self.number + 1) * (NY - self.view_radius) / n])
                pts.append([NX - self.view_radius - 50, 0.5 * self.view_radius])

            wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
            self.manager.route[me['name']] = wp
            self.first_run = False
            self.set_status('going_exploring')
        fighting_ratio, fighting_position, fighting_friends = Fighter(self, info).calculate()
        explore_ratio = Positional(self, info).calculate()
        castle_ratio, castle_position, castle_friends = Castler(self, info).calculate()
        harvester_ratio, harvester_position, harvester_friends = Harvester(self, info).calculate()
        self.logger.debug(f'Exploring ratio: {explore_ratio}, harvest_ration: {harvester_ratio}, fighting_ratio: {fighting_ratio}, castle_ratio: {castle_ratio}')

        if castle_ratio > 0:
            for name in castle_friends:
                self.manager.override[name] = castle_position
            self.logger.info(f"Found opposing castle at {castle_position} - Calling Reinforcements")
            self.goto_castle(me, info, other_castle=True)
            self.set_status('going_to_castle')
        elif harvester_ratio > 1/8:
            self.logger.info(f'Found gem, going to: {harvester_position}, harvester ratio: {harvester_ratio}')
            if self.previous_gem is not None and not np.all(self.previous_gem == harvester_position):
                # self.logger.info(f'Gem {harvester_position} added')
                self.manager.route[me['name']].add_next_waypoint(harvester_position)
                self._waypoints.destination = []
                self.previous_gem = harvester_position
            if self.previous_gem is None:
                self.previous_gem = harvester_position
        elif fighting_ratio > 0.2:
            self.logger.info(f'Found enemy, engaging to: {fighting_position}, fighting ratio: {fighting_ratio}')
            if self._enemy_override is not None:
                if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
                    self.manager.route[me['name']].pop_waypoint()
            self.manager.route[me['name']].add_next_waypoint(fighting_position)
            self._enemy_override = fighting_position
        else:
            if self._enemy_override is not None:
                if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
                    self.manager.route[me['name']].pop_waypoint()
                self.logger.info('No enemies, returning to route')
                self._enemy_override = None
        try:
            point = self.manager.route[me['name']].next_waypoint(me['position'])
        except TypeError:
            print(self.manager.route[me['name']].waypoints)
        if point is None:
            self.logger.info('No more waypoints, going to explore')
            self.set_status('going_exploring')
            self.manager.route[me['name']].add_next_waypoint(team_reflector(self.team, [100, 100*np.random.random()]))
            self.manager.route[me['name']].add_next_waypoint(team_reflector(self.team, [100, NY-100*np.random.random()]))
        self.explore_position(me, point)
        self.post_run(t, dt, info)


# __author__ = 'github.com/wardsimon'
# __version__ = '0.0.1'
#
# from IdleKnights.logic.route import Waypoint
# from IdleKnights.constants import np, NX, NY
# from .templateAI import IdleTemplate
# from IdleKnights.tools.positional import team_reflector
# from ..logic.situation import Fighter, Positional, Harvester, Castler
#
# KIND = 'healer'
# SEEKER_DICT = {
#     'health_ratio': 0.5,
#     'distance_ratio': 0.5,
#     'fight_ratio': 0.15,
#     'gem_ratio': 1/8,
#     'castle_ratio': 0,
# }
#
#
# class Seeker(IdleTemplate):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, kind=KIND, **kwargs)
#         self._enemy_override = None
#         self.previous_gem = None
#
#     def run(self, t: float, dt: float, info: dict):
#         super().run(t, dt, info)
#         me = info['me']
#         if self.manager.override[me['name']] is not None:
#             override_point = self.manager.override[me['name']]
#             self.logger.warn(f"Routing overriden, going to {override_point}")
#             self.explore_position(me, override_point)
#             return
#         if self.first_run:
#             # How many seekers are there?
#             n = len([k for k in self.manager._others.keys() if 'Seeker' in k.__name__])
#             # Get the flag position
#             target = np.array(info['flags'][self.team])
#             pts = []
#             if target[1] / 2 > NY / 2:
#                 pts.append([NX - self.view_radius - 50,
#                             NY - 0.5 * self.view_radius - self.number * (NY - self.view_radius) / n])
#                 pts.append([NX - self.view_radius - 50,
#                             NY - 0.5 * self.view_radius - (self.number + 1) * (NY - self.view_radius) / n])
#                 pts.append([NX - self.view_radius - 50, NY - 0.5 * self.view_radius])
#             else:
#                 pts.append(
#                     [NX - self.view_radius - 50, 0.5 * self.view_radius + self.number * (NY - self.view_radius) / (n)])
#                 pts.append([NX - self.view_radius - 50,
#                             0.5 * self.view_radius + (self.number + 1) * (NY - self.view_radius) / n])
#                 pts.append([NX - self.view_radius - 50, 0.5 * self.view_radius])
#
#             wp = Waypoint([team_reflector(self.team, pt) for pt in pts])
#             self.manager.route[me['name']] = wp
#             self.first_run = False
#             self.set_status('going_exploring')
#
#         fighting_ratio, fighting_position, fighting_friends = Fighter(self, info, health_ratio=SEEKER_DICT['health_ratio'], distance_ratio=SEEKER_DICT['distance_ratio']).calculate()
#         explore_ratio = Positional(self, info).calculate()
#         castle_ratio, castle_position, castle_friends = Castler(self, info).calculate()
#         harvester_ratio, harvester_position, harvester_friends = Harvester(self, info).calculate()
#         self.logger.debug(f'Exploring ratio: {explore_ratio}, harvest_ration: {harvester_ratio}, fighting_ratio: {fighting_ratio}, castle_ratio: {castle_ratio}')
#
#         if castle_ratio > SEEKER_DICT['castle_ratio']:
#             for name in castle_friends:
#                 self.manager.override[name] = castle_position
#             self.logger.info(f"Found opposing castle at {castle_position} - Calling Reinforcements")
#             self.goto_castle(me, info, other_castle=True)
#             self.set_status('going_to_castle')
#         else:
#             if self._enemy_override is not None:
#                 if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
#                     self.manager.route[me['name']].pop_waypoint()
#                 self.logger.info('No enemies, returning to route')
#                 self._enemy_override = None
#             if harvester_ratio > SEEKER_DICT['gem_ratio'] and castle_ratio < SEEKER_DICT['castle_ratio']:
#                 self.logger.info(f'Found gem, going to: {harvester_position}, harvester ratio: {harvester_ratio}')
#                 if self.previous_gem is not None and not np.all(self.previous_gem == harvester_position):
#                     # self.logger.info(f'Gem {harvester_position} added')
#                     self.manager.route[me['name']].add_next_waypoint(harvester_position)
#                     self._waypoints.destination = []
#                     self.previous_gem = harvester_position
#                 if self.previous_gem is None:
#                     self.previous_gem = harvester_position
#             elif fighting_ratio > SEEKER_DICT['fight_ratio']:
#                 self.logger.info(f'Found enemy, engaging to: {fighting_position}, fighting ratio: {fighting_ratio}')
#                 if self._enemy_override is not None:
#                     if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
#                         self.manager.route[me['name']].pop_waypoint()
#                 self.manager.route[me['name']].add_next_waypoint(fighting_position)
#                 self._enemy_override = fighting_position
#         try:
#             point = self.manager.route[me['name']].next_waypoint(me['position'])
#         except TypeError:
#             print(self.manager.route[me['name']].waypoints)
#         if point is None:
#             self.logger.info('No more waypoints, going to explore')
#             self.set_status('going_exploring')
#             self.manager.route[me['name']].add_next_waypoint(team_reflector(self.team, [100, 100*np.random.random()]))
#             self.manager.route[me['name']].add_next_waypoint(team_reflector(self.team, [100, NY-100*np.random.random()]))
#         self.explore_position(me, point)
#         self.post_run(t, dt, info)