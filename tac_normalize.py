#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

# ONCE AND FOR ALL
from pprint import pprint

import tac

# work to "normalize" a tictacto board by rotating it such that 
# more massive sides of the board are on the bottom and left, respectively
board = tac.Board()
board[1,1] = 'X'
board[1,0] = 'O'
board[2,1] = 'X'
board[0,2] = 'O'
board[2,2] = 'X'
print(board)
center = board[1, 1]
top = board[0, :]
right = board[:, -1]
bottom = board[-1, :]
left = board[:, 0]
sides = {'top': top, 'right': right, 'bottom':bottom, 'left': left}

def mass(square):
    if square == 'X':
        return 1
    if square == 'O':
        return 2
    return 0

def positional_factor(side):
    rv = [mass(square) for square in side]
    rv = [m * val for m, val in zip(rv, [0.5, 1, 0.5])]

    return sum(rv)

masses = {side_name: positional_factor(side) for side_name, side in sides.items()}
pprint(masses)
