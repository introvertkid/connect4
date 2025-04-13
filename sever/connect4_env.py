import numpy as np
import random

# Super global constant variables
BOARD_ROW = 6
BOARD_COL = 7

class Connect4Env:
    def __init__(self):
        self.rows = BOARD_ROW
        self.cols = BOARD_COL
        self.board = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.current_player = 1  # Player 1 = 1, Player 2 = 2
        self.reward = {'win': 10, 'draw': 0, 'lose': -10}

    def reset(self):
        self.__init__()
        return self.board.flatten()

    def play(self, action):
        """Thực hiện một hành động"""
        if action not in self.valid_moves():
            return self.board.flatten(), -10, True, {}  # Kết thúc nếu chọn sai

        for row in reversed(range(self.rows)):  # Tìm hàng trống thấp nhất
            if self.board[row, action] == 0:
                self.board[row, action] = self.current_player
                reward, done = self.isWinningMove()
                self.current_player = 3 - self.current_player  # Đổi lượt
                return self.board.flatten(), reward, done, {}

        reward, done = self.isWinningMove()
        if done:
            # Trả reward cho player hiện tại
            final_reward = reward if self.current_player == 1 else -reward
        else:
            final_reward = 0

        self.current_player = 3 - self.current_player
        return self.board.flatten(), final_reward, done, {}

    """ Check if current state is ended after making a move"""

    def isWinningMove(self):
        def check_direction(r, c, dr, dc, player):
            count = 0
            for _ in range(4):
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r, c] == player:
                    count += 1
                    r += dr
                    c += dc
                else:
                    break
            return count == 4

        for r in reversed(range(self.rows)):
            for c in range(self.cols):
                if self.board[r, c] != 0:
                    player = self.board[r, c]
                    if (check_direction(r, c, 1, 0, player) or  # Vertical
                            check_direction(r, c, 0, 1, player) or  # Horizontal
                            check_direction(r, c, 1, 1, player) or  # Diagonal /
                            check_direction(r, c, 1, -1, player)):  # Diagonal \
                        return (self.reward['win'], True)

        # Check draw game
        if np.all(self.board != 0):
            return (self.reward['draw'], True)

        return (0, False)  # have not done yet

    def valid_moves(self):
        """Trả về danh sách cột có thể đi"""
        return [c for c in range(self.cols) if self.board[0, c] == 0]

    def printBoard(self):
        for row in self.board:
            print(" ".join(["⚫" if x == 0 else "🚗" if x == 1 else "🚕" for x in row]))
        print(" 0  1   2  3   4  5   6")


board = Connect4Env()
state = board.reset()
print(state)
print(board.board)
