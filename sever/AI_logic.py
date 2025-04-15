from NegamaxSolver.Position import Position
from NegamaxSolver.Solver import Solver

solver = Solver()

def get_best_move(board: list[list[int]], valid_moves: list[int]) -> int:
    """
    Given a 2D board and list of valid column indices (0-based), returns the best column to play (0-based).
    """
    # 0 = empty, 1 = player 1, 2 = player 2
    move_sequence = ""
    height = len(board)
    width = len(board[0]) if board else 0

    # Convert board into a move sequence
    # Traverse column-wise since Connect Four moves stack from bottom
    col_heights = [0] * width
    flat_board = [[board[row][col] for row in reversed(range(height))] for col in range(width)]

    for move_number in range(height * width):
        for col in range(width):
            if col_heights[col] < height and flat_board[col][col_heights[col]] != 0:
                move_player = flat_board[col][col_heights[col]]
                if move_player == (move_number % 2) + 1:
                    move_sequence += str(col + 1)  # Convert 0-based to 1-based
                    col_heights[col] += 1
                    break

    # Build Position
    P = Position()
    P.play_seq(move_sequence)

    # Analyze best move
    scores = solver.analyze(P)

    # Choose column with the highest score (among valid moves)
    best_col = max(valid_moves, key=lambda c: scores[c])
    return best_col