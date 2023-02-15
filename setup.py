__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

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


from setuptools import Extension
from setuptools.dist import Distribution
from distutils.command.build_ext import build_ext
import os
import numpy
from Cython.Build import cythonize

# This function will be executed in setup.py:
def build(setup_kwargs):
    # The file you want to compile
    extensions = [
        "IdleKnights/**/*.pyx"
    ]

    # gcc arguments hack: enable optimizations
    os.environ['CFLAGS'] = '-O3'

    exts = [Extension('*', extensions,
                      include_dirs=[numpy.get_include()],
                      libraries=["m"]
                      )]

    # Build
    setup_kwargs.update({
        'ext_modules': cythonize(
            exts,
            language_level=3,
            compiler_directives={'linetrace': True},
        ),
        'cmdclass': {'build_ext': build_ext}
    })

if __name__ == "__main__":
    build(setup_kwargs)
    setup(**setup_kwargs)
