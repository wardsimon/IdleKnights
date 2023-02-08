__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


def make_character(cls, index=0, **kwargs):
    return type(cls.__name__, (cls, ), {'number': index, '__old_cls__': cls}, **kwargs)