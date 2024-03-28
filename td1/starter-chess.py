import time
import chess
from random import randint, choice

def randomMove(b):
    '''Renvoie un mouvement au hasard sur la liste des mouvements possibles. Pour avoir un choix au hasard, il faut
    construire explicitement tous les mouvements. Or, generate_legal_moves() nous donne un itérateur.'''
    return choice([m for m in b.generate_legal_moves()])

def deroulementRandom(b):
    '''Déroulement d'une partie d'échecs au hasard des coups possibles. Cela va donner presque exclusivement
    des parties très longues et sans gagnant. Cela illustre cependant comment on peut jouer avec la librairie
    très simplement.'''
    print("----------")
    print(b)
    if b.is_game_over():
        print("Resultat : ", b.result())
        return
    b.push(randomMove(b))
    deroulementRandom(b)
    b.pop()

def demo():
    board = chess.Board()
    deroulementRandom(board)


def depth_search(board, d=0, max_depth=None, display=True, nodes=[0], games=[0]):
    if max_depth is not None and d >= max_depth:
        return
    
    for move in board.generate_legal_moves():
        board.push(move)
        nodes[0] += 1
        if board.is_game_over():
            board.pop()
            games[0] += 1
        else:
            depth_search(board, d + 1, max_depth=max_depth, display=False)
            board.pop()
            
    if display:
        print(f"games {games[0]}, nodes {nodes[0]}")
    return

def measure_time(fn, args):
    start = time.time_ns()
    result = fn(args)
    end = time.time_ns()
    print(f"Took {(end - start) * 1e-9}s")
    return result



pieces_values = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'K': 200,
}

def get_piece_value(symbol):
    try:
        val = pieces_values[symbol.upper()]
        if symbol != symbol.upper():
            return -val
        return val
    except KeyError:
        return 0

def heuristique(board):
    s = 0
    for piece in board.pieces_map.values():
        s += get_piece_value(piece.symbol())
    return s


if __name__ == "__main__":
    board = chess.Board()
    measure_time(lambda _ : depth_search(board, max_depth=4), None)
