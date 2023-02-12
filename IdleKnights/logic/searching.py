__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from IdleKnights import NY, NX
from IdleKnights.tools.positional import team_reflector


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
                    NY - Y_DIFF/2 - Y_DIFF*(np.random.random()-0.5) - knight.number * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF,
                    NY - Y_DIFF/2 - Y_DIFF*(np.random.random()-0.5) - (knight.number + 1) * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF, NY - Y_DIFF])
    else:
        pts.append([NX - X_DIFF,
                    Y_DIFF/2 + Y_DIFF*(np.random.random()-0.5) + knight.number * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF,
                    Y_DIFF/2 + Y_DIFF*(np.random.random()-0.5) + (knight.number + 1) * (NY - knight.view_radius) / number_of_knights])
        pts.append([NX - X_DIFF, Y_DIFF])

    run_out_of_pts = [
        [100, 100 * np.random.random()],
        [100, NY - 100 * np.random.random()]
    ]

    return pts, run_out_of_pts


def king_defender(knight, info, name):
    target = np.array(CONVERTER(knight, info)[knight.team])
    fountain_offset = np.array([0, NY/3])
    fountain_radius = 200
    lower_fountain = True
    f = knight.view_radius/2
    if target[1] > NY/2:
        lower_fountain = False
        f = - f

    if target[1] > NY/2:
        # we are at the top
        pts = [
            [target[0] - 75, NY - 125],
            [target[0] - 75, 125],
            [target[0] + 75, 125],
            [target[0] + 75, NY - 125]
        ]
    else:
        pts = [
            [target[0] - 75, 125],
            [target[0] - 75, NY - 125],
            [target[0] + 75, NY - 125],
            [target[0] + 75, 125]
        ]
    off1 = np.array([knight.view_radius/2, 0])
    off2 = [0, f]
    run_out_of_pts = [
        target - off1 + off2,
        target + off1 + off2,
    ]

    return [team_reflector(knight.team, p) for p in pts], [team_reflector(knight.team, p) for p in run_out_of_pts]







def CONVERTER(knight, info):
    mode = knight.mode
    if mode == 'flag':
        return info['flags']
    elif mode == 'king':
        d = {knight.team: np.array([info['friends'][-1]['x'], info['friends'][-1]['y']])}
        for enemy in info['enemies']:
            if enemy['name'].lower() == 'king':
                d[knight.opposing_team] = np.array([enemy['x'], enemy['y']])
                break
        return d
