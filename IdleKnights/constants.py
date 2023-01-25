import numpy as np

BOARD_EMPTY = 0
BOARD_WALL = 1
BOARD_CLOAK = -1
BOARD_ROUTE = 2

INPUT_EMPTY = 0
INPUT_WALL = 1
INPUT_UNKNOWN = -1
NX = 1790
NY = 960

CREATOR = 'IdleKnights'

KERNEL = np.ones((3, 3), dtype=np.intc)
