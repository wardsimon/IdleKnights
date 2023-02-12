# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['IdleKnights',
 'IdleKnights.charaters',
 'IdleKnights.charaters.objectives',
 'IdleKnights.logic',
 'IdleKnights.logic.route_generation',
 'IdleKnights.tools']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24,<2.0', 'quest @ git+https://github.com/wardsimon/quest.git@main']

setup_kwargs = {
    'name': 'idlequestknights',
    'version': '0.1.0',
    'description': 'Knights for the game Quest',
    'long_description': '# Quest Characters\nKnight for the game Quest\n',
    'author': 'Simon Ward',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
