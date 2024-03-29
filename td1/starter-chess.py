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


white_pawn_map = \
    ([10 for _ in range(8)] +
     [9 for _ in range(8)] +
     [8 for _ in range(8)] +
     [7 for _ in range(8)] +
     [6 for _ in range(8)] +
     [5 for _ in range(8)] +
     [4 for _ in range(8)] +
     [3 for _ in range(8)])

black_pawn_map = \
    ([3 for _ in range(8)] +
     [4 for _ in range(8)] +
     [5 for _ in range(8)] +
     [6 for _ in range(8)] +
     [7 for _ in range(8)] +
     [8 for _ in range(8)] +
     [9 for _ in range(8)] +
     [10 for _ in range(8)])


def pawn_bonus(piece: chess.Piece, square):
    if piece.color:
        return -white_pawn_map[square]
    return black_pawn_map[square]


PAWN_BONUS_FACTOR = 0.05


def heuristique(board):
    s = 0
    for square, piece in board.piece_map().items():
        s += get_piece_value(piece.symbol())
        if piece.symbol().lower() == chess.piece_symbol(chess.PAWN):
            s += pawn_bonus(piece, square) * PAWN_BONUS_FACTOR
    return s


WINNER_VALUE = 10e6
def score_over(board):
    outcome = board.outcome()
    if outcome is None:
        return 0
    if outcome.winner is None:
        return 0
    if outcome.winner:
        return WINNER_VALUE
    return -WINNER_VALUE


def minimax(board, depth, selector=max):
    def swap():
        return min if selector == max else max

    if depth <= 0:
        return heuristique(board)

    if board.is_game_over():
        return score_over(board)

    values = []
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, selector=swap())
        board.pop()
        values.append(value)

    extremum = selector(values)
    return extremum


def alpha_beta(board, depth, alpha=-10e10, beta=10e10, selector=max):
    def swap():
        return min if selector == max else max

    if depth <= 0:
        return heuristique(board), alpha, beta

    if board.is_game_over():
        return score_over(board), alpha, beta

    values = []
    for move in board.legal_moves:
        board.push(move)
        value, alpha, beta = alpha_beta(board, depth - 1, alpha, beta, selector=swap())
        board.pop()
        # Pruning phase
        if selector == min:
            if value <= alpha:
                return alpha, alpha, beta
        else:
            if value >= beta:
                return beta, alpha, beta

        values.append(value)

    extremum = selector(values)

    # Update pruning values
    if selector == min:
        alpha = max(alpha, extremum)
    else:
        beta = min(beta, extremum)

    return extremum, alpha, beta


def maximin(board, depth, selector=min):
    def swap():
        return min if selector == max else max

    values = []
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, selector=swap())
        board.pop()
        values.append((value, move))

    extremum = selector(values, key=operator.itemgetter(0))[0]
    return choice(list(filter(lambda v: v[0] == extremum, values)))[1]


def max_alpha(board, depth, selector=min):
    def swap():
        return min if selector == max else max

    values = []
    for move in board.legal_moves:
        board.push(move)
        value, _, _ = alpha_beta(board, depth - 1, selector=swap())
        board.pop()
        values.append((value, move))

    extremum = selector(values, key=operator.itemgetter(0))[0]
    return choice(list(filter(lambda v: v[0] == extremum, values)))[1]


def iter_deep(board, available_time, selector=max):

    best_estimation = choice(list(board.legal_moves))

    depth = 1
    time_took = 0
    while available_time > time_took:
        start = time.perf_counter()
        best_estimation = max_alpha(board, depth, selector=selector)
        end = time.perf_counter()
        time_took += end - start
        depth += 1
    print(f"iter_deep took {time_took} seconds, reached depth {depth}.")
    return best_estimation


def random_player(board):
    return choice(list(board.legal_moves))


def minmax_player(level, is_player1=True):
    return lambda b: maximin(b, level, max if is_player1 else min)


def alpha_beta_player(level, is_player1=True):
    return lambda b: max_alpha(b, level, max if is_player1 else min)


def iter_deep_player(available_time, is_player1=True):
    return lambda b: iter_deep(b, available_time, max if is_player1 else min)


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
        print(game_length, move, heuristique(board))
        print(board)

        if game_length > max_length:
            print("game too long !")
            return

    print(f"Game over in {game_length} moves")


if __name__ == "__main__":
    board = chess.Board()
    play_match(board, alpha_beta_player(4), minmax_player(1, False))

