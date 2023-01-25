# distutils: language = c++

import cython as cython
import numpy as np
cimport numpy as cnp

from cython.operator cimport dereference as deref
from libcpp.limits cimport numeric_limits

# from libc.math cimport abs as cabs
from libcpp.pair cimport pair
from libcpp.vector cimport vector
from libcpp.set cimport set as cset
from libcpp.stack cimport stack

DTYPE  = np.intc
DTYPE_CPP = int

cdef float FLT_MAX = numeric_limits[float].max()

ctypedef pair[int, int] Pair
ctypedef pair[double, pair[int, int]] pPair
ctypedef vector[pair[int, int]] vPair

ctypedef struct cell:
    int parent_i
    int parent_j
    double f
    double g
    double h


cdef bint isValid(int row, int col, int MAXrow, int MAXcol):
    return (row >= 0) and (row < MAXrow) and (col >= 0) and (col < MAXcol);

cdef bint isUnblocked(int[:, ::1] board, int row, int col):
    if board[row, col] == 1:
        return False
    else:
        return True

cdef bint isDestination(int row, int col, Pair destination):
    if row == destination.first and col == destination.second:
        return True
    else:
        return False

cdef double calculateHValue(int row, int col, Pair destination):
    return ((row - destination.first)  * (row - destination.first) +
            (col - destination.second) * (col - destination.second)) ** 0.5


cdef cnp.ndarray[int, ndim=2] tracePath(cell[:, ::1] cellDetails_view, Pair dest):

    cdef int row = dest.first
    cdef int col = dest.second

    cdef int temp_row
    cdef int temp_col
    cdef int i = 0
    cdef stack[Pair] Path
    while not (cellDetails_view[row, col].parent_i == row and cellDetails_view[row, col].parent_j == col):
        Path.push(Pair(row, col))
        temp_row = cellDetails_view[row, col].parent_i
        temp_col = cellDetails_view[row, col].parent_j
        row = temp_row
        col = temp_col
        i += 1
    Path.push(Pair(row, col))

    cdef Pair p
    result = np.zeros((i+1, 2), dtype=np.intc)
    cdef int[:,::1] result_view = result

    while not Path.empty():
        p = Path.top()
        result_view[i, 0] = p.first
        result_view[i, 1] = p.second
        Path.pop()
        i = i -1
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
def compute(int[:, ::1] board, int[::1] start_point,  int[::1] end_point):

    cdef Pair start_pair = Pair(start_point[0], start_point[1])
    cdef Pair end_pair = Pair(end_point[0], end_point[1])

    cdef int nx = board.shape[0]
    cdef int ny = board.shape[1]

    # If the source is out of range
    if not isValid(start_pair.first, start_pair.second, nx, ny):
        print("Source is invalid")
        return np.array([], dtype=np.intc)

    # If the destination is out of range
    if not isValid(end_pair.first, end_pair.second, nx, ny):
        print("Destination is invalid")
        return np.array([], dtype=np.intc)

    # Either the source or the destination is blocked
    if (not isUnblocked(board, start_pair.first, start_pair.second)) or (not isUnblocked(board, end_pair.first, end_pair.second)):
        print("Source [" + str(not isUnblocked(board, start_pair.first, start_pair.second)) +
              "] or the destination [" + str(not isUnblocked(board, end_pair.first, end_pair.second)) + "] is blocked")
        return np.array([], dtype=np.intc)

    # If the destination cell is the same as source cell
    if isDestination(start_pair.first, start_pair.second, end_pair):
        print("We are already at destination")
        return np.array([], dtype=np.intc)

    # Create a closed list and initialise it to false which means that no cell
    # has been included yet This closed  list is implemented as a boolean 2D array
    closedList = np.zeros_like(board, dtype=np.intc)
    cdef int[:,::1] closedList_view = closedList

    # Declare a 2D array of structure to hold the details. Note the custom dtype
    cdef cell cell_tmp
    cellDetailsType = np.asarray(<cell[:1]> &(cell_tmp)).dtype
    cellDetails = np.zeros_like(board, dtype=cellDetailsType)
    cdef cell[:, ::1] cellDetails_view = cellDetails

    # To  iterate over the array
    cdef Py_ssize_t i
    cdef Py_ssize_t j

    # To store the 'g', 'h' and 'f' of the 8 successors
    cdef double gNew
    cdef double hNew
    cdef double fNew

    cdef vPair operationVector

    for i in range(nx):
        for j in range(ny):
            cellDetails_view[i, j].parent_i = -1
            cellDetails_view[i, j].parent_j = -1
            cellDetails_view[i, j].f = FLT_MAX
            cellDetails_view[i, j].g = FLT_MAX
            cellDetails_view[i, j].h = FLT_MAX

    # Initialising the parameters of the starting node
    i = start_pair.first
    j = start_pair.second
    cellDetails_view[i, j].f = 0.0
    cellDetails_view[i, j].g = 0.0
    cellDetails_view[i, j].h = 0.0
    cellDetails_view[i, j].parent_i = i
    cellDetails_view[i, j].parent_j = j

    # Create an open list having information as <f, <i, j>>
    # where f = g + h, and i, j are the row and column index of that cell
    # Note that 0 <= i <= ROW-1 & 0 <= j <= COL-1 This open list is implemented
    # as a set of pair of pair.
    cdef cset[pPair] openList
    # Put the starting cell on the open list and set its  'f' as 0
    openList.insert(pPair(0.0, Pair(i, j)))

    # We set this boolean value as false as initially
    # the destination is not reached.
    cdef bint foundDest = False
    # Define the current working point
    cdef pPair p

    while not openList.empty():
        # Get the vertex
        p = deref(openList.begin())

        # Remove this vertex from the open list
        openList.erase(openList.begin())

        # Add this vertex to the closed list
        i = p.second.first
        j = p.second.second
        closedList_view[i, j] = 1

         # Generating all the 8 successor of this cell
         #
         #     N.W   N   N.E
         #       \   |   /
         #        \  |  /
         #     W----Cell----E
         #          / | \
         #        /   |  \
         #     S.W    S   S.E
         #
         # Cell-->Popped Cell (i, j)
         # N -->  North       (i-1, j)
         # S -->  South       (i+1, j)
         # E -->  East        (i, j+1)
         # W -->  West           (i, j-1)
         # N.E--> North-East  (i-1, j+1)
         # N.W--> North-West  (i-1, j-1)
         # S.E--> South-East  (i+1, j+1)
         # S.W--> South-West  (i+1, j-1)
        operationVector = [Pair(i-1, j), Pair(i+1, j), Pair(i, j+1), Pair(i, j-1),
                           Pair(i-1, j+1), Pair(i-1, j-1), Pair(i+1, j+1), Pair(i+1, j-1)]

        for op in operationVector:
            if isValid(op.first, op.second, nx, ny):
                # If the destination cell is the same as the current successor
                if isDestination(op.first, op.second, end_pair):
                    cellDetails_view[op.first, op.second].parent_i = i
                    cellDetails_view[op.first, op.second].parent_j = j
                    foundDest = True
                    return tracePath(cellDetails_view, end_pair)
                # If the successor is already on the closed list or if it is blocked,
                # then ignore it. Else do the following
                elif closedList_view[op.first, op.second] == 0 and isUnblocked(board, op.first, op.second):

                    gNew = cellDetails_view[i, j].g + 1.0
                    # gNew = cellDetails_view[i, j].g + 1.0 # THIS SHOULD BE sqrt(2) for diagonal elements
                    hNew = calculateHValue(op.first, op.second, end_pair)
                    fNew = gNew + hNew
                    # If it isn’t on the open list, add it to the open list.
                    # Make the current square the parent of this square. Record the
                    # f, g, and h costs of the square cell
                    #                 OR
                    # If it is on the open list already, check to see if this path
                    # to that square is better, using 'f' cost as the measure.
                    if cellDetails_view[op.first, op.second].f == FLT_MAX or cellDetails_view[op.first, op.second].f > fNew:
                        openList.insert(pPair(fNew, Pair(op.first, op.second)))
                        cellDetails_view[op.first, op.second].f = fNew
                        cellDetails_view[op.first, op.second].g = gNew
                        cellDetails_view[op.first, op.second].h = hNew
                        cellDetails_view[op.first, op.second].parent_i = i
                        cellDetails_view[op.first, op.second].parent_j = j
    if foundDest is False:
        print("Failed to find the Destination Cell\n")
    return np.array([], dtype=np.intc)