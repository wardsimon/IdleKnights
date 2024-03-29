import numpy as np
import logging

BOARD_EMPTY = 0
BOARD_WALL = 1
BOARD_CLOAK = -1
BOARD_ROUTE = 2

INPUT_EMPTY = 0
INPUT_WALL = 1
INPUT_UNKNOWN = -1
NX = 1790
NY = 960

TIME = 180

CREATOR = 'IdleKnights'

KERNEL = np.ones((7, 3), dtype=np.intc)
BLOCK_SIZE = 32
LOG_LEVEL = logging.INFO
