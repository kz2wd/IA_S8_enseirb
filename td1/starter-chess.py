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


def measure_time(fn):
    def decorated(*args, **kwargs):
        start = time.perf_counter_ns()
        result = fn(*args, **kwargs)
        end = time.perf_counter_ns()
        print(f"Took {(end - start) * 1e-9}s")
    return decorated



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
CHECK_VALUE = 0.5


def heuristique(board):
    if board.is_game_over():
        return score_over(board)
    s = 0
    for square, piece in board.piece_map().items():
        s += get_piece_value(piece.symbol())
        if piece.symbol().lower() == chess.piece_symbol(chess.PAWN):
            s += pawn_bonus(piece, square) * PAWN_BONUS_FACTOR
    if board.is_check():
        s += -CHECK_VALUE if board.turn else CHECK_VALUE
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

    if depth <= 0 or board.is_game_over():
        return heuristique(board)

    values = []
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, selector=swap())
        board.pop()
        values.append(value)

    extremum = selector(values)
    return extremum


class OutOfTimeException(Exception):
    pass


def alpha_beta(board, depth, alpha=-10e10, beta=10e10, selector=max, time_remaining=None):
    if time_remaining is not None:
        start = time.perf_counter()

    def swap():
        return min if selector == max else max

    if depth <= 0 or board.is_game_over():
        h = heuristique(board)
        return h, board.is_game_over(), h

    values = []
    reached_end = True  # Only used if there are no legal moves
    best_board = 0
    for move in board.legal_moves:
        board.push(move)

        if time_remaining is not None:
            end = time.perf_counter()
            time_remaining -= end - start
            if time_remaining < 0:
                print('out of time')
                raise OutOfTimeException()
        # if time_remaining is not None:
        #     start = time.perf_counter()
        value, reached_end, best_board = alpha_beta(board, depth - 1, alpha, beta, selector=swap(), time_remaining=time_remaining)

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
    print(f"(minmax found {extremum:.2f})", end=" ")
    return choice(list(filter(lambda v: v[0] == extremum, values)))[1]


def max_alpha(board, depth, selector=min, total_time=None):
    def swap():
        return min if selector == max else max
    board = board.copy()
    reached_end = True  # Only used if there are no legal moves
    best_board = 0
    values = []
    for move in board.legal_moves:
        board.push(move)
        value, reached_end, best_board = alpha_beta(board, depth - 1, selector=swap(), time_remaining=total_time)
        board.pop()
        values.append((value, move))

    extremum = selector(values, key=operator.itemgetter(0))[0]
    # print(f"(alphabeta found {extremum:.2f})", end=" ")
    return choice(list(filter(lambda v: v[0] == extremum, values)))[1], best_board, reached_end


def iter_deep(board, available_time, selector=max):

    best_estimation = choice(list(board.legal_moves))

    depth = 1
    time_took = 0
    reached_end = False
    board_value = "unknown"
    try:
        while available_time > time_took and not reached_end:
            start = time.perf_counter()
            best_estimation, board_value, reached_end = max_alpha(board, depth, selector=selector, total_time=available_time)
            end = time.perf_counter()
            time_took += end - start
            depth += 1
    except OutOfTimeException as ignored:
        pass
    print(f"iter_deep took {time_took} seconds, reached depth {depth} ({reached_end=}), board estimated : {board_value}.")
    return best_estimation


def random_player(board):
    return choice(list(board.legal_moves))


def minmax_player(level, is_player1=True):
    return lambda b: maximin(b, level, max if is_player1 else min)


def alpha_beta_player(level, is_player1=True):
    return lambda b: max_alpha(b, level, max if is_player1 else min)[0]


def iter_deep_player(available_time, is_player1=True):
    return lambda b: iter_deep(b, available_time, max if is_player1 else min)


@measure_time
def play_match(board, player1, player2, max_length=500):

    def swap_players():
        return player1 if current_player == player2 else player2

    current_player = player1
    white = True
    game_length = 0
    while not board.is_game_over():
        move = current_player(board)
        board.push(move)

        current_player = swap_players()
        game_length += 1
        print(f"{'white' if white else 'black'} plays", move, game_length, f"{heuristique(board):.2f}")
        print(board)
        # input()

        if game_length > max_length:
            print("game too long !")
            return
        white = not white
    print(f"{board.outcome().result()} in {game_length} moves")


if __name__ == "__main__":
    board = chess.Board()
    play_match(board, iter_deep_player(2), random_player)

