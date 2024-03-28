import operator
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
    chess.piece_symbol(chess.PAWN): 1,
    chess.piece_symbol(chess.KNIGHT): 3,
    chess.piece_symbol(chess.BISHOP): 3,
    chess.piece_symbol(chess.ROOK): 5,
    chess.piece_symbol(chess.QUEEN): 9,
    chess.piece_symbol(chess.KING): 200,
}


def get_piece_value(symbol):
    try:
        val = pieces_values[symbol.lower()]
        if symbol != symbol.upper():
            return -val
        return val
    except KeyError:
        return 0


def heuristique(board):
    s = 0
    for piece in board.piece_map().values():
        s += get_piece_value(piece.symbol())
    return s


def minimax(board, depth, selector=max):
    def swap():
        return min if selector == max else max

    if depth <= 0:
        return heuristique(board)

    if board.is_game_over():
        return heuristique(board)  # temporary

    values = []
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, selector=swap())
        board.pop()
        values.append(value)

    extremum = selector(values)
    return choice([v for v in values if v == extremum])



def maximin(board, depth):
    values = []
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, selector=min)
        board.pop()
        values.append((value, move))

    return max(values, key=operator.itemgetter(0))[1]


def random_player(board):
    return choice(list(board.legal_moves))


def minmax_player(level):
    return lambda b: maximin(b, level)


def play_match(board, player1, player2, max_length=500):

    def swap_players():
        return player1 if current_player == player2 else player2

    current_player = player1
    game_length = 0
    while not board.is_game_over():
        move = current_player(board)
        board.push(move)

        current_player = swap_players()
        game_length += 1
        print(game_length, move)
        print(board)
        if game_length > max_length:
            print("game too long !")
            return

    print(f"Game over in {game_length} moves")


if __name__ == "__main__":
    board = chess.Board()
    play_match(board, minmax_player(1), minmax_player(3))

