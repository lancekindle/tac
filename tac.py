#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

class player:
    X = 'X'
    O = 'O'

class Board(object):
    def __init__(self):
        self._board = [[' ']*3 for i in range(3)]

    def __setitem__(self, indices, val):
        """Set the value of the cell at 'row' 'col' to the value 'val',
        assuming cell is unoccupied"""
        row, col = indices
        if self._board[row][col] == ' ':
            self._board[row][col] = val
        else:
            raise ValueError("That's an invalid move you big dumb")
    
    def __getitem__(self, indices):
        """Get the value of the board cell at 'row', 'col'. As an example, you
        may access the board @ row 1, column 2 like so: board[1, 2]
        """
        row, col = indices
        return self._board[row][col]

    def get_legal_moves(self):
        """return list of tuples of all legal moves, where the tuple
        consists of row, column coordinates
        """
        moves = []
        for r, row in enumerate(self._board):
            for c, col in enumerate(row):
                if col == ' ':
                    moves.append((r,c))
        return moves
    
    def __str__(self):
        """Return visual representation of tic-tac-toe board"""
        return "─┼─┼─\n".join(["│".join(row)+'\n' for row in self._board])


class Vhat(object):
    """Vhat is responsible for evaluating a given board and returning a value
    that represents (in arbitrary numerical form) the likelyhood of winning
    this board game

    This numerical representation is calculated as a series of board
    "markers" (such as how many 2-in a row's do I have?) multiplied by
    a corresponding weight. The sum of these markers give an
    approximation of the state of the board.
    """

    def __init__(self, me_symbol, weights):
        self.me = me_symbol
        self.blank = ' '
        self.z = weights
        # create a set of row/column/diagonal coordinates
        self.rows = []
        for r in range(3):
            row = [(r, 0), (r, 1), (r, 2)]
            self.rows.append(row)
        self.columns = []
        for c in range(3):
            col = [(0, c), (1, c), (2, c)]
            self.columns.append(col)

        self.diagonals = [
                [(0, 0), (1, 1), (2, 2)],
                [(0, 2), (1, 1), (2, 0)],
                ]

    def get_middle_me(self, board):
        if board[1, 1] == self.me:
            return self.z[0]
        return 0

    def get_corner_me(self,board):
        corners = 0
        for row, col in [(0,0), (2,2), (0,2), (2,0)]:
            if board[row, col] == self.me:
                corners += 1
        return corners * self.z[4]

    def get_near_complete_sequence_count(self, board):
        """return number of almost completed sequences where 2 of the
        coordinates are occupied by "me" and the third square in the sequence
        is open
        """
        sequence_almost_done = lambda sequence: sequence.count(self.me) == 2 and \
                               sequence.count(self.blank) == 1
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_almost_done(symbols):
                    score += 1
        return score

    def get_near_losing_sequence_count(self, board):
        sequence_almost_done = lambda sequence: sequence.count(self.me) == 0 and \
                               sequence.count(self.blank) == 1
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_almost_done(symbols):
                    score += 1
        return score
    
    def get_winning_count(self, board):
        sequence_completed = lambda sequence: sequence.count(self.me) == 3
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_completed(symbols):
                    score += 1
        return score

    def get_losing_count(self, board):
        sequence_completed = lambda sequence: sequence.count(self.me) == 0 and \
                             sequence.count(self.blank) == 0
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_completed(symbols):
                    score += 1
        return score


if __name__ == '__main__':
    print("nothing is happening so far")
    board = Board()
    vhat = Vhat(player.X, None)
    board[1, 1] = player.X
    board[0, 0] = player.X
    board[0, 1] = player.X
    board[0, 2] = player.O
    board[1, 2] = player.O
    board[2, 2] = player.X
    print(board)
    print(board[1, 1])
    print(board.get_legal_moves())
    print('number of almost completed X sequence', vhat.get_near_complete_sequence_count(board))
    print('number of almost completed O sequence', vhat.get_near_losing_sequence_count(board))
    print('number of winning sequences', vhat.get_winning_count(board))
    print('number of losing sequences', vhat.get_losing_count(board))

