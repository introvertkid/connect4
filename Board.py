class Board:
    COL = 7
    ROW = 6
    MOV = ""

    def __init__(self):
        pass

    def isValid(col):
        return True

    def isWinningMove(board, ROW, COL):
        # Check whether there are 4 aligning discs
        # Start with row (r), column (c)
        # Moving in row/horizontal direction (dr), column/vertical direction (dc)
        # player: The disc is of the same color/player
        def check_direction(r, c, dr, dc, player):
            count = 0
            for _ in range(4):
                if 0 <= r < ROW and 0 <= c < COL and board[r][c] == player:
                    count += 1
                    r += dr
                    c += dc
                else:
                    break
            return count == 4

        for r in range(ROW):
            for c in range(COL):
                if board[r][c] != 0:
                    player = board[r][c]
                    if (check_direction(r, c, 1, 0, player) or  # Vertical
                            check_direction(r, c, 0, 1, player) or  # Horizontal
                            check_direction(r, c, 1, 1, player) or  # Diagonal /
                            check_direction(r, c, 1, -1, player)):  # Diagonal \
                        return True
        return False

board = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 2, 1],
    [2, 2, 1, 2, 1, 2, 1],
    [1, 2, 2, 1, 2, 2, 1]
]
print(Board.isWinningMove(board, Board.ROW, Board.COL))
