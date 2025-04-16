import sys
import os
from typing import List
import time
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NegamaxSolver.Position import Position
from NegamaxSolver.Solver import Solver

filename = "NegamaxSolver/7x6.book"
solver = Solver()
solver.load_book(filename)

move_sequence = ""
position = Position()
previous_board = [[0 for _ in range(7)] for _ in range(6)]

def is_game_over(board: List[List[int]]) -> bool:
    # Check for full board (draw)
    if all(cell != 0 for row in board for cell in row):
        return True

    # Check for 4 in a row (horizontal, vertical, diagonal)
    height = len(board)
    width = len(board[0])
    for r in range(height):
        for c in range(width):
            if board[r][c] == 0:
                continue
            player = board[r][c]
            # Check right
            if c <= width - 4 and all(board[r][c+i] == player for i in range(4)):
                return True
            # Check down
            if r <= height - 4 and all(board[r+i][c] == player for i in range(4)):
                return True
            # Diagonal down-right
            if r <= height - 4 and c <= width - 4 and all(board[r+i][c+i] == player for i in range(4)):
                return True
            # Diagonal up-right
            if r >= 3 and c <= width - 4 and all(board[r-i][c+i] == player for i in range(4)):
                return True
    return False

def reset_state():
    global position, move_sequence, previous_board
    position = Position()
    move_sequence = ""
    previous_board = [[0 for _ in range(7)] for _ in range(6)]

def register_opponent_move(current_board: List[List[int]]):
    """
    Compare current_board with the global previous_board to detect the opponent's move.
    Update the Position and move_sequence accordingly.
    """
    global position, move_sequence, previous_board

    # Game over? Reset everything.
    if is_game_over(current_board):
        print("Game over detected. Resetting state.")
        reset_state()
        return

    height = len(current_board)
    width = len(current_board[0])

    # Find the column where a new piece was added
    for col in range(width):
        for row in range(height):
            if previous_board[row][col] != current_board[row][col]:
                # There is a difference — new disc dropped
                if current_board[row][col] in [1, 2] and previous_board[row][col] == 0:
                    # Register this move
                    position.play_col(col)
                    move_sequence += str(col + 1)
                    previous_board = [row[:] for row in current_board]  # update snapshot
                    return

    # If no move detected (possibly a duplicate request), just update snapshot
    previous_board = [row[:] for row in current_board]

def get_best_move(current_player: int, valid_moves: List[int]) -> int:
    global move_sequence, position, previous_board
    scores = solver.analyze(position)
    best_col = max(valid_moves, key=lambda c: scores[c])
    position.play_col(best_col)
    move_sequence += str(best_col + 1)  # Update move history

    # Update previous_board manually to reflect our move
    for row in reversed(range(len(previous_board))):
        if previous_board[row][best_col] == 0:
            previous_board[row][best_col] = current_player
            break

    return best_col

if __name__ == "__main__":
    valid_move = [0, 1, 2, 3, 4, 5, 6]

    start = time.time()
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 2, 1, 0, 0, 0, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 2, 1, 1, 0, 0, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [2, 2, 1, 1, 0, 0, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [2, 2, 1, 1, 0, 1, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [2, 2, 1, 1, 2, 1, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0],
                            [2, 2, 1, 1, 2, 1, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 2, 0, 0, 0],
                            [2, 2, 1, 1, 2, 1, 0]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 2, 0, 0, 0],
                            [2, 2, 1, 1, 2, 1, 1]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 2, 2, 0, 0],
                            [2, 2, 1, 1, 2, 1, 1]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 2, 2, 0, 0],
                            [2, 2, 1, 1, 2, 1, 1]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 2, 2, 0, 2],
                            [2, 2, 1, 1, 2, 1, 1]])
    register_opponent_move([[0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 2, 2, 1, 2],
                            [2, 2, 1, 1, 2, 1, 1]])

    move = get_best_move(1, valid_move)

    print("Move: ", move)
    print("Move sequence: ", move_sequence)
    print(f"Time Taken: {time.time() - start}")