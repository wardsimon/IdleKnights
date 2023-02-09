__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from IdleKnights import NY, NX
from IdleKnights.charaters.templateAI import CONVERTER


def general_search_points(knight, info, name):
    number_of_knights = len([k for k in knight.manager._others.keys() if name in k.__name__])
    # Get the flag position
    target = np.array(CONVERTER(knight, info)[knight.team])
    pts = []
    X_DIFF = 50
    Y_DIFF = 50
    # Do an upper/lower split search
    if target[1] / 2 > NY / 2:
        pts.append([NX - X_DIFF,
                    NY - Y_DIFF - knight.number * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF,
                    NY - Y_DIFF - (knight.number + 1) * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF, NY - Y_DIFF])
    else:
        pts.append([NX - X_DIFF,
                    Y_DIFF + knight.number * (NY - knight.view_radius) / (number_of_knights)])
        pts.append([NX - X_DIFF,
                    Y_DIFF + (knight.number + 1) * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF, Y_DIFF])
    return pts
