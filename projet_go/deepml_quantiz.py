# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''
import operator
import signal
import sys
import time
from functools import lru_cache

import numpy as np

import Goban
from random import choice
from playerInterface import *

import torch
from torch import nn
import torch.quantization

class OutOfTimeException(Exception):
    pass


def out_of_time_handler(signum, frame):
    print("Time is over", file=sys.stderr)
    raise OutOfTimeException


class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.init_model()

    def getPlayerName(self):
        return "Flowerless"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        # 1 is black player (first to play), 2 is white player (2nd to play)
        move = self.iter_deep(self._board, 2, max if self._mycolor == 1 else min)
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    def iter_deep(self, board, available_time, selector=max):
        signal.signal(signal.SIGALRM, out_of_time_handler)
        signal.alarm(available_time)

        best_estimation = choice(list(board.legal_moves()))

        depth = 1
        time_took = 0
        reached_end = False
        board_value = "unknown"
        try:
            while available_time > time_took and not reached_end:
                start = time.perf_counter()
                best_estimation, reached_end, board_value = self.max_alpha(board, depth, selector=selector)
                end = time.perf_counter()
                time_took += end - start
                depth += 1

            signal.alarm(0)
        except OutOfTimeException as ignored:
            pass

        print(
            f"iter_deep took {time_took} seconds, reached depth {depth} ({reached_end=}), board estimated : {board_value}.", file=sys.stderr)
        return best_estimation

    def max_alpha(self, board, depth, selector=min):
        def swap():
            return min if selector == max else max

        board = Goban.Board(board)
        reached_end = True  # Only used if there are no legal moves
        best_board = 0
        values = []
        for move in board.legal_moves():
            board.push(move)
            value, reached_end, best_board = self.alpha_beta(board, depth - 1, selector=swap())
            board.pop()
            values.append((value, move))

        extremum = selector(values, key=operator.itemgetter(0))[0]
        return choice(list(filter(lambda v: v[0] == extremum, values)))[1], reached_end, best_board

    def alpha_beta(self, board, depth, alpha=-10e10, beta=10e10, selector=max):
        def swap():
            return min if selector == max else max

        if depth <= 0 or board.is_game_over():
            h = self.heuristique(board)
            return h, False, h  # Broken, for now assume we never end.

        values = []
        reached_end = True  # Only used if there are no legal moves
        best_board = 0
        for move in board.legal_moves():
            board.push(move)
            value, reached_end, best_board = self.alpha_beta(board, depth - 1, alpha, beta, selector=swap())

            board.pop()

            if selector == min:  # min : enemy is choosing, we update upper_bound (beta)
                beta = min(beta, value)
                if alpha >= beta:
                    return value, reached_end, best_board
            else:  # max : ally is choosing, we update lower_bound (alpha)
                alpha = max(alpha, value)
                if alpha >= beta:
                    return value, reached_end, best_board

            values.append(value)

        extremum = selector(values)

        return extremum, reached_end, best_board

    def init_model(self):
        self.model = nn.Sequential(
            nn.Conv2d(2, 10, 3, padding=1),  # 8 * 8 * 2 (128) -> 64 * 10 (640)
            nn.ReLU(),
            nn.Conv2d(10, 10, 5, padding=2),  # 640 -> 640
            nn.ReLU(),
            nn.Conv2d(10, 10, 5, padding=2),  # 640 -> 640
            nn.ReLU(),
            nn.Flatten(start_dim=1),  # 640 -> 640
            nn.Linear(640, 300),
            nn.ReLU(),
            nn.Linear(300, 100),
            nn.ReLU(),
            nn.Linear(100, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid(),
        )
        device = torch.device("cpu")
        self.model.load_state_dict(torch.load('trained_model.pth', map_location=device))

        self.model.to(device)
        self.model.eval()
        # Quantization to reduce model size, in order to infer faster ! Does it really work though ?
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear, torch.nn.Conv2d}, dtype=torch.qint8
        )

    # Very COSTLY
    def heuristique(self, board: Goban.Board):
        blacks = np.zeros((8, 8))
        whites = np.zeros((8, 8))
        for x in range(8):
            for y in range(8):
                val = board[Goban.Board.flatten((x, y))]
                if val == Goban.Board._BLACK:
                    blacks[x, y] = 1
                elif val == Goban.Board._WHITE:
                    whites[x, y] = 1

        X = torch.Tensor([[blacks, whites]])
        return self.model(X)[0]
