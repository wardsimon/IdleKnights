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
    X_DIFF = 75
    Y_DIFF = 60
    # Do an upper/lower split search
    if target[1] > NY / 2:
        pts.append([NX - X_DIFF,
                    NY - Y_DIFF/2 - Y_DIFF*(2*np.random.random()-0.5) - knight.number * (NY - knight.view_radius) / number_of_knights])
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
        [100, 50 + np.random.randint(10, 60)],
        [100, NY - 50 - np.random.randint(10, 60)]
    ]

    return pts, [team_reflector(knight.team, p) for p in run_out_of_pts]


def king_defender(knight, info, name):
    target = np.array(CONVERTER(knight, info)[knight.team])

    pts1 = []
    if target[1] > NY / 2:
        # explore the upper half of the map
        pts1.append([target[0]+50, NY - 100])
        pts1.append([target[0]-50, NY - 100])
        pts1.append([target[0]-50, NY/2])
        pts1.append([target[0]+50, NY/2])
    else:
        pts1.append([target[0]+50, 100])
        pts1.append([target[0]-50, 100])
        pts1.append([target[0]-50, NY/2])
        pts1.append([target[0]+50, NY/2])

    castle_type = info['castle']['direction']
    if castle_type == 3:
        pts = [
            np.array([target[0]-16, target[1] - 32]),
            np.array([target[0]+16, target[1] - 32]),
        ]
    elif castle_type == 1:
        pts = [
            np.array([target[0]-16, target[1] + 32]),
            np.array([target[0]+16, target[1] + 32]),
        ]
    elif castle_type == 0:
        pts = [
            np.array([target[0]+32, target[1] - 16]),
            np.array([target[0]+32, target[1] + 16]),
        ]
    elif castle_type == 2:
        pts = [
            np.array([target[0]-32, target[1] - 16]),
            np.array([target[0]-32, target[1] + 16]),
        ]
    knight.control_parameters['gem_ratio'] = 1/10
    return [team_reflector(knight.team, p) for p in pts1], [team_reflector(knight.team, p) for p in pts]







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
