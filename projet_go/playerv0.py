# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''
import operator
import sys

import Goban
from random import choice
from playerInterface import *

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "Mini mini v0 "

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        move = self.maximin(self._board, 1, max if self._mycolor == 1 else min)
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

    def minimax(self, board: Goban.Board, depth: int, selector=max):
        def swap():
            return min if selector == max else max

        if depth <= 0 or board.is_game_over():
            return self.heuristique(board)

        values = []
        for move in board.legal_moves():
            board.push(move)
            value = self.minimax(board, depth - 1, selector=swap())
            board.pop()
            values.append(value)

        extremum = selector(values)
        return extremum

    def maximin(self, board: Goban.Board, depth: int, selector=min):
        def swap():
            return min if selector == max else max

        values = []
        for move in board.legal_moves():
            board.push(move)
            value = self.minimax(board, depth - 1, selector=swap())
            board.pop()
            values.append((value, move))

        extremum = selector(values, key=operator.itemgetter(0))[0]
        # print(f"values :  : {values}", file=sys.stderr)
        return choice(list(filter(lambda v: v[0] == extremum, values)))[1]

    def heuristique(self, board: Goban.Board):
        black_score, white_score = board.compute_score()
        return black_score - white_score
