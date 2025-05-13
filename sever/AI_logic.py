import sys
import os
from typing import List
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NegamaxSolver.Position import Position
from NegamaxSolver.Solver import Solver

filename = "NegamaxSolver/7x6.book"
solver = Solver()
solver.load_book(filename)

def get_best_move(board: List[List[int]], valid_moves: List[int]) -> int:
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

if __name__ == "__main__":
    board = [[0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 2, 0, 0, 0],
        [0, 2, 1, 1, 2, 0, 0]]
    valid_move = [0, 1, 2, 3, 4, 5, 6]
    get_best_move(board, valid_move)