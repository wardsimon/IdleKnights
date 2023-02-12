__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


def make_character(cls, index=0, inject_kwargs=None, **kwargs):
    new_init = dict()
    if inject_kwargs is not None:
        new_init = {
            '__init__': lambda *arg, **karg: cls.__init__(*arg, **inject_kwargs, **karg),
            '__old_init__': cls.__init__
        }
    return type(cls.__name__, (cls, ), {'number': index, '__old_cls__': cls, **kwargs, **new_init})