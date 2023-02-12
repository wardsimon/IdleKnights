__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


from IdleKnights.constants import np, NY
from .templateAI import IdleTemplate
from IdleKnights.tools.positional import team_reflector
from ..logic.situation import Fighter, Positional, Harvester, Castler

KIND = 'warrior'
WARRIOR_DICT = {
    'health_ratio': 0.5,
    'distance_ratio': 0.25,
    'fight_ratio': 0.75,
    'gem_ratio': 1/8,
    'castle_ratio': 0,
}


class CastleKiller(IdleTemplate):

    def __init__(self, *args, health_ratio: float = None, distance_ratio: float = None,
                 fight_ratio: float = None, gem_ratio: float = None, castle_ratio: float = None, **kwargs):
        super().__init__(*args, kind=KIND, **kwargs)
        self._enemy_override = None
        self.previous_gem = None
        self.control_parameters = WARRIOR_DICT.copy()
        if health_ratio is not None:
            self.control_parameters['health_ratio'] = health_ratio
        if distance_ratio is not None:
            self.control_parameters['distance_ratio'] = distance_ratio
        if fight_ratio is not None:
            self.control_parameters['fight_ratio'] = fight_ratio
        if gem_ratio is not None:
            self.control_parameters['gem_ratio'] = gem_ratio
        if castle_ratio is not None:
            self.control_parameters['castle_ratio'] = castle_ratio

    def run(self, t: float, dt: float, info: dict):
        super().run(t, dt, info)
        me = info['me']
        reset_run = self.run_override(info, me)
        if reset_run:
            return
        castle_ratio, castle_position, castle_friends = Castler(self, info).calculate()
        if castle_ratio > self.control_parameters['castle_ratio']:
            for name in castle_friends:
                self.manager.override[name] = castle_position, 'going_to_castle', self.name
            self.logger.info(f"Found opposing castle at {castle_position} - Calling Reinforcements")
            self.goto_castle(me, info, other_castle=True)
            self.set_status('going_to_castle')
        else:
            fighting_ratio, fighting_position, fighting_friends = Fighter(self, info,
                                                                          health_ratio=self.control_parameters['health_ratio'],
                                                                          distance_ratio=self.control_parameters['distance_ratio']
                                                                          ).calculate()
            explore_ratio = Positional(self, info).calculate()
            harvester_ratio, harvester_position, harvester_friends = Harvester(self, info).calculate()
            self.logger.debug(f'Exploring ratio: {explore_ratio}, harvest_ration: {harvester_ratio}, fighting_ratio: {fighting_ratio}, castle_ratio: {castle_ratio}')
            if fighting_ratio > self.control_parameters['fight_ratio']:
                self.logger.info(f'Found enemy, engaging to: {fighting_position}, fighting ratio: {fighting_ratio}')
                if self._enemy_override is not None:
                    if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
                        self.manager.route[me['name']].pop_waypoint()
                self.manager.route[me['name']].add_next_waypoint(fighting_position)
                self._enemy_override = fighting_position
            elif harvester_ratio > self.control_parameters['gem_ratio']:
                if self.previous_gem is not None and not np.all(self.previous_gem == harvester_position):
                    self.logger.info(f'Found gem, going to: {harvester_position}, harvester ratio: {harvester_ratio}')
                    self.manager.route[me['name']].add_next_waypoint(harvester_position)
                    self._waypoints.destination = []
                    self.previous_gem = harvester_position
                if self.previous_gem is None:
                    self.previous_gem = harvester_position
                self.set_status('going_to_gem')
            else:
                if self._enemy_override is not None:
                    if np.all(self._enemy_override == np.array(self.manager.route[me['name']].next_destination)):
                        self.manager.route[me['name']].pop_waypoint()
                    self.logger.info('No enemies, returning to route')
                    self._enemy_override = None
            point = None
            try:
                point = self.manager.route[me['name']].next_waypoint(me['position'])
            except TypeError:
                self.logger.Warn(f'Waypoint Error, Waypoint stack: {self.manager.route[me["name"]].waypoints}')
            if point is None:
                self.logger.info('No more waypoints, going to explore')
                self.set_status('going_exploring')
                for pnt in self.backup_waypoints:
                    self.manager.route[me['name']].add_next_waypoint(team_reflector(self.team, pnt))
            self.explore_position(me, point)
        self.post_run(t, dt, info)
