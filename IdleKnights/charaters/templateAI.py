import numpy as np
from ..core.ai import BaseAI

CREATOR = 'JohnDoe'


class TemplateWarrior(BaseAI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, kind='warrior', **kwargs)
        self.previous_position = [0, 0]
        self.previous_health = 0

    def run(self, t: float, dt: float, info: dict):
        me = info['me']

        if all(me['position'] == self.previous_position) or (
                me['health'] < self.previous_health):
            self.heading = np.random.random() * 360.0

        elif len(info['flags']) == 2:
            flag_pos = info['flags'][self.opposing_team]
            self.goto = flag_pos

        elif len(info['enemies']) > 0 and (me['cooldown'] == 0):
            target = info['enemies'][0]
            self.goto = [target['x'], target['y']]

        elif info['gems']:
            self.goto = [info['gems']['x'][0], info['gems']['y'][0]]

        self.previous_position = me['position']
        self.previous_health = me['health']


class TemplateScout(BaseAI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, kind='scout', **kwargs)
        self.previous_position = [0, 0]
        self.previous_health = 0

    def run(self, t: float, dt: float, info: dict):
        me = info['me']

        if all(me['position'] == self.previous_position) or (
                me['health'] < self.previous_health):
            self.heading = np.random.random() * 360.0

        elif len(info['flags']) == 2:
            flag_pos = info['flags'][self.opposing_team]
            self.goto = flag_pos

        elif len(info['enemies']) > 0:
            target = info['enemies'][0]
            self.heading = (self.towards(target['x'], target['y']) + 180) % 360

        elif info['gems']:
            self.goto = [info['gems']['x'][0], info['gems']['y'][0]]

        self.previous_position = me['position']
        self.previous_health = me['health']


team = {
    'Arthur': TemplateWarrior,
    'Galahad': TemplateWarrior,
    'Lancelot': TemplateScout
}
