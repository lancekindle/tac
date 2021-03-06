#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import random
import copy
from collections import defaultdict
import itertools
import numpy as np

# ONCE AND FOR ALL
from pprint import pprint

class player:
    X = 'X'
    O = 'O'
    BLANK = ' '

class Board(object):

    def __init__(self):
        board = [[player.BLANK]*3 for i in range(3)]
        self._board = np.array(board)

    @classmethod
    def from_string(cls, board):
        """reconstruct a board out of a string"""
        self = cls()
        r, c = 0, 0
        for character in board:
            if character in (player.X, player.O, player.BLANK):
                self[r, c] = character
                c += 1
            if c == 3:
                c = 0
                r += 1
        return self

    def __setitem__(self, indices, val):
        """Set the value of the cell at 'row', 'col' to the value 'val',
        assuming cell is unoccupied"""
        self._board.__setitem__(indices, val)

    def __getitem__(self, indices):
        """Get the value of the board cell at 'row', 'col'. As an example, you
        may access the board @ row 1, column 2 like so: board[1, 2]
        OR get values of board, if row or column indices are slices.
        """
        return self._board.__getitem__(indices)

    def get_legal_moves(self):
        """return list of tuples of all legal moves, where the tuple
        consists of row, column coordinates
        """
        moves = []
        for r, row in enumerate(self._board):
            for c, col in enumerate(row):
                if col == player.BLANK:
                    moves.append((r,c))
        return moves

    def normalized_copy(self):
        """rotate and flip board such that the lightest faces of the
        board are at the top-left. This should make the board rotation
        and flip equivalent, such that similar games will look exactly
        the same. Return a new instance of the board
        """
        copy = self.copy()
        leftside = copy[:, 0].tolist()
        rightside = copy[:, 2].tolist()
        topside = copy[0, :].tolist()
        bottomside = copy[2, :].tolist()
        left = 3 - leftside.count(player.BLANK)
        right = 3 - rightside.count(player.BLANK)
        top = 3 - topside.count(player.BLANK)
        bottom = 3 - bottomside.count(player.BLANK)
        if left > right:
            copy = copy._flip(horizontal=True)
        if top > bottom:
            copy = copy._flip(vertical=True)
        return copy

    def _rotate(self, rotations):
        """rotate a set number of rotations in the counter-clockwise
        direction. Return rotated COPY of board
        """
        rotated = self.copy()
        rotations %= 4
        for _ in range(4):
            rotated[:, 0] = self[0, :]
            rotated[2, :] = self[:, 0]
            rotated[:, 2] = self[2, :]
            rotated[0, :] = self[:, 2]
        return rotated

    def _flip(self, vertical=False, horizontal=False):
        """flip the board vertically or horizontally"""
        flipped = self.copy()
        if vertical:
            flipped[2, :] = self[0, :]
            flipped[0, :] = self[2, :]
        else:
            flipped[:, 2]= self[:, 0]
            flipped[:, 0] = self[:, 2]
        return flipped

    def copy(self):
        board = self.__class__()
        board._board = copy.deepcopy(self._board)
        return board

    def __repr__(self):
        """Return visual representation of tic-tac-toe board"""
        return "─┼─┼─\n".join(["│".join(row)+'\n' for row in self._board])


class Competitor(object):
    """Competitor is responsible for evaluating a given board and
    returning a value that represents (in arbitrary numerical form) the
    likelyhood of winning this board game. In addition it contains a
    method "get_best_next_move" which will evaluate any given board and
    return the move that it deems best.

    This numerical representation is calculated as a series of board
    "markers" (such as how many 2-in a row's do I have?) multiplied by a
    corresponding weight. The sum of these markers give an approximation
    of the state of the board.
    """

    def __init__(self, weights=None):
        """if Competitor is not given any weights, a set of random
        weights will be created
        """
        if weights is None:
            weights = [random.randint(-30, 30) for _ in range(6)]
        if not len(weights) == 6:
            raise ValueError("Weights can only be a list of 6 numbers, has wrong length")
        self.weights = weights
        self.generation = 0
        self.lost_games = set()
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

    def set_symbol(self, me_symbol):
        self.me = me_symbol

    def get_next_board_moves(self, board):
        """get list of next possible board moves, with respective board
        states, and board score
        """
        next_states = []
        for r, c in board.get_legal_moves():
            copy = board.copy()
            copy[r, c] = self.me
            score = self.score_board(copy)
            move = (r, c)
            next_states.append((score, move, copy))
        return next_states

    def get_best_next_move(self, board):
        next_states = self.get_next_board_moves(board)
        next_states.sort()
        # Get state with the LARGEST score
        _, move, _ = next_states[-1]
        return move

    def get_middle_me(self, board):
        if board[1, 1] == self.me:
            return 1
        return 0

    def get_corner_me(self,board):
        corners = 0
        for row, col in [(0,0), (2,2), (0,2), (2,0)]:
            if board[row, col] == self.me:
                corners += 1
        return corners

    def get_near_complete_sequence_count(self, board):
        """return number of almost completed sequences where 2 of the
        coordinates are occupied by "me" and the third square in the
        sequence is open
        """
        sequence_almost_done = lambda sequence: sequence.count(self.me) == 2 and \
                               sequence.count(player.BLANK) == 1
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_almost_done(symbols):
                    score += 1
        return score

    def get_near_losing_sequence_count(self, board):
        sequence_almost_done = lambda sequence: sequence.count(self.me) == 0 and \
                               sequence.count(player.BLANK) == 1
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
                             sequence.count(player.BLANK) == 0
        score = 0
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = [board[r, c] for r, c in sequence]
                if sequence_completed(symbols):
                    score += 1
        return score

    def score_board(self, board):
        """score the given board by the sum of the weights * their
        respective evaluation criteria
        """
        scoring_functions = [self.get_corner_me, self.get_middle_me,
                self.get_losing_count, self.get_winning_count,
                self.get_near_complete_sequence_count,
                self.get_near_losing_sequence_count]
        score = 0
        for weight, score_fxn in zip(self.weights, scoring_functions):
            score += weight * score_fxn(board)
        return score

    def is_game_over(self, board):
        """tells if the board has been completed"""
        # Check all the sequences of three moves, and if there's one non-blank
        # sequence of three the game is over.
        board_set = set()
        for genre in (self.columns, self.diagonals, self.rows):
            for sequence in genre:
                symbols = set([board[r, c] for r, c in sequence])
                board_set = board_set | symbols
                if len(symbols) == 1 and player.BLANK not in symbols:
                    return True
        # If there are no blank spaces on the board
        if player.BLANK not in board_set:
            # catskill reached
            return True
        return False
    
    def remember_loss(self, board):
        """call this function with the board on which this player lost.
        The player will attempt to learn to avoid reaching this same
        board state
        """
        if self.is_game_over(board):
            raise ValueError('board should be in state prior to end-game')
        board = board.normalized_copy()
        self.lost_games.add(board)

    def __repr__(self):
        """Oh i just love printing."""
        return str(self.weights) + ' ' + str(self.generation)
    
    def __lt__(self, other):
        """is used if sort() tries to sort this instance. Just
        return a single number so that sorting does not affect these
        """
        return 0


def play_game(leaderboard, player1, player2):
    """given a dictionary (leaderboard) of player to winning count.
    Play two players against each other, allowing each to play 1st.
    """
    board = Board()
    player1.set_symbol(player.X)
    player2.set_symbol(player.O)
    players = [player2, player1]
    for _ in range(2):
        # play two games, swapping turn order
        players = list(reversed(players))
        board = Board()
        turn = 0
        while not player1.is_game_over(board):
            current = players[turn % len(players)]
            r, c = current.get_best_next_move(board)
            board[r, c] = current.me
            turn += 1
        # increase score on leaderboard for winning player
        # inform losing player of loss (so it can learn)
        player1_win = player1.get_winning_count(board) > 0
        player2_win = player2.get_winning_count(board) > 0
        # rewind previous move to replicate board before winning move
        # played
        board[r, c] = player.BLANK
        if player1_win:
            leaderboard[player1] += 1
            player2.remember_loss(board)
        elif player2_win:
            leaderboard[player2] += 1
            player1.remember_loss(board)


def mix_genetics(parent1, parent2, generation_count):
    """Return the average of the weights of the two parents, with
    some random mutations thrown in
    """
    mixed_dna = []
    for w1, w2 in zip(parent1.weights, parent2.weights):
        # Mutate value +/- 1, about 20% of the time
        mutation = 0
        if not random.randint(0, 3):
            mutation = random.randint(-1, 1)

        mixed_dna.append(((w1 + w2) / 2) + mutation)

    child = Competitor(mixed_dna)
    child.generation = generation_count

    return child


def play_tournament_round(leaderboard, generation):
    for player1, player2 in itertools.combinations(leaderboard, 2):
        play_game(leaderboard, player1, player2)
    pool_size = len(leaderboard)
    ranked = list((score, vhatter) for vhatter, score in leaderboard.items())
    ranked.sort()
    ranked.reverse()
    pprint(ranked)

    # eliminate lower-scoring players
    breeders = ranked[:len(ranked) // 2]
    random.shuffle(breeders)
    leaderboard = {}

    # for remaining players, breed them and produce 1 child for each two players
    for (_, parent1), (_, parent2) in zip(breeders[1::2], breeders[::2]):
        child = mix_genetics(parent1, parent2, generation)
        for entrant in (parent1, parent2, child):
            leaderboard[entrant] = 0

    # add new random players until leaderboard is filled
    while len(leaderboard) < pool_size:
        # Creates Competitor with random weights
        stranger = Competitor()
        stranger.generation = generation
        leaderboard[stranger] = 0

    return leaderboard, generation+1

# (22, [1, 12, -4, 16, 12, -2] 4)
def play_by_play(leaderboard, player1, player2):

    played = []
    player1.set_symbol(player.X)
    player2.set_symbol(player.O)
    players = [player1, player2]
    for game in range(2):
        print("Playing game {}/2".format(game+1))
        # play two games, swapping turn order
        players = list(reversed(players))
        players[0].set_symbol(player.X)
        players[1].set_symbol(player.O)
        print("Player {} ({}) is going first".format(players[0].me, players[0].weights))
        print("Player {} ({}) is going second".format(players[1].me, players[1].weights))
        board = Board()
        turn = 0
        while not player1.is_game_over(board):
            current = players[turn % len(players)]
            r, c = current.get_best_next_move(board)
            board[r, c] = current.me
            turn += 1
            print("Turn #{}, after player {} moved:".format(turn, current.me))
            print(board)
        # increase score on leaderboard for winning player
        leaderboard[player1] += player1.get_winning_count(board) > 0
        leaderboard[player2] += player2.get_winning_count(board) > 0
        played.append(board)
    return played


if __name__ == '__main__':
    leaderboard0 = {Competitor(): 0 for _ in range(20)}
    player1 = Competitor([1, 5, -29, 30, 4, -15])
    player1.generation = "ME"
    # WOW, these random weights induce winning via corner case!
    player2 = Competitor([5, 2, -12, 23, -1, -16])
    leaderboard0[player1] = 0
    leaderboard0[player2] = 0
    b1, b2 = play_by_play(leaderboard0, player1, player2)
    f = b1._flip(True)
    x = b1.normalized_copy()

    generation = 0
    leaderboard, generation = play_tournament_round(leaderboard0, generation)
    losers = [comp for comp, gen in leaderboard.items() if comp.lost_games]
    lost = losers[0].lost_games
    raise
    for _ in range(500):
        print(generation)
        leaderboard, generation = play_tournament_round(leaderboard, generation)









