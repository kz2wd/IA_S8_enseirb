# -*- coding: utf-8 -*-
import random
import time
import Tictactoe 
from random import randint, choice

def getresult(b):
    '''Fonction qui évalue la victoire (ou non) en tant que X. Renvoie 1 pour victoire, 0 pour 
       égalité et -1 pour défaite. '''
    if b.result() == b._X:
        return 1
    elif b.result() == b._O:
        return -1
    else:
        return 0

def RandomMove(b):
    '''Renvoie un mouvement au hasard sur la liste des mouvements possibles'''
    return choice(b.legal_moves())

def deroulementRandom(b):
    '''Effectue un déroulement aléatoire du jeu de morpion.'''
    print("----------")
    print(b)
    if b.is_game_over():
        res = getresult(b)
        if res == 1:
            print("Victoire de X")
        elif res == -1:
            print("Victoire de O")
        else:
            print("Egalité")
        return
    b.push(RandomMove(b))
    deroulementRandom(b)
    b.pop()


def demo():
    board = Tictactoe.Board()
    print(board)

    ### Deroulement d'une partie aléatoire
    deroulementRandom(board)

    print("Apres le match, chaque coup est défait (grâce aux pop()): on retrouve le plateau de départ :")
    print(board)


def explore_all(board, display=True, games=[0], nodes=[0]):
    for move in board.legal_moves():
        board.push(move)
        nodes[0] += 1
        if board.is_game_over():
            board.pop()
            games[0] += 1
        else:
            explore_all(board, False)
            board.pop()

    if display:
        print(f"games {games[0]}, nodes {nodes[0]}")
    return games, nodes


def change_func(func):
    if func == max:
        return min
    return max


def min_max(board, func_to_use=max, display=True, games=[0], nodes=[0]):
    values = []
    for move in board.legal_moves():
        board.push(move)
        nodes[0] += 1
        if board.is_game_over():
            res = getresult(board)
            board.pop()
            games[0] += 1
            return res
        else:
            res = winning(board, change_func(func_to_use), False)
            board.pop()
            values.append(res)

    if display:
        print(f"games {games[0]}, nodes {nodes[0]}")

    return func_to_use(values)


def search_winning(board, display=True, games=[0], nodes=[0]):
    values = []
    for move in board.legal_moves():
        board.push(move)
        nodes[0] += 1
        if board.is_game_over():
            res = getresult(board)
            board.pop()
            games[0] += 1
            return res
        else:
            res = search_winning(board, False)
            board.pop()
            values.append(res)

    if display:
        print(f"games {games[0]}, nodes {nodes[0]}")
    return max(values)


def search_winning_opt(board, display=True, games=[0], nodes=[0]):
    highest = -1
    for move in board.legal_moves():
        board.push(move)
        nodes[0] += 1
        if board.is_game_over():
            res = getresult(board)
            board.pop()
            games[0] += 1
            return res
        else:
            res = search_winning_opt(board, False)
            board.pop()
            if res == 1:
                if display:
                    print(f"games {games[0]}, nodes {nodes[0]}")
                return 1
            elif res > highest:
                highest = res
    
    if display:
        print(f"games {games[0]}, nodes {nodes[0]}")

    return highest

def measure_time(fn, args):
    start = time.time_ns()
    result = fn(args)
    end = time.time_ns()
    print(f"Took {(end - start) * 1e-9}s")
    return result


if __name__ == "__main__":
    board = Tictactoe.Board()
    random.seed(2)

    board.push(RandomMove(board))
    board.push(RandomMove(board))
    board.push(RandomMove(board))
    board.push(RandomMove(board))
    board.push(RandomMove(board))
    board.push(RandomMove(board))
    print(board)
    explore_all(board)
    winning = search_winning(board)
    print(f"Winning: {winning}")


