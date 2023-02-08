__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from .templateAI import IdleTemplate
import numpy as np

base_decisions = {
    'explore': 0.4,
    'collect': 0.2,
    'attack':  0.5,
    'defend':  0.5,
    'flee':    0.5,
}


class TaskDecider:
    def __init__(self, decision_base: dict):
        self.decision_base = decision_base


    def decide(self, info: dict):
        me = info['me']
        if me['health'] < 0.5:
            return 'flee'
        if me['health'] < 0.8:
            return 'defend'
        if me['health'] < 1.0:
            return 'collect'
        if me['health'] > 0.8:
            return 'attack'
        return 'explore'


class IdleBasicKnight(IdleTemplate):

    def __init__(self, *args, decision_base: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.decision_base = decision_base or base_decisions

    def run(self, t: float, dt: float, info: dict):
        super().run(t, dt, info)
        me = info['me']
        if self.manager.override[me['name']] is not None:
            if np.all(self.manager.override[me['name']] == me['position']):
                self.manager.override[me['name']] = None
            else:
                override_point = self.manager.override[me['name']]
                self.logger.warn(f"Routing overriden, going to {override_point}")
                self.explore_position(me, override_point)
                return

