import copy

class Board:
    ROW = 6
    COL = 7

    def __init__(self, Row = 6, Col = 7, Mov = ""):
        self.board = [[' ' for _ in range(self.COL)] 
                        for _ in range(self.ROW)]
        self.ROW = Row
        self.COL = Col
        self.current_player = 0
        self.MOV = Mov

    def copy(self):
        return copy.deepcopy(self)

    def minimax(self, lo, hi):
        # check for draw game
        if len(self.MOV) == self.ROW * self.COL:
            return 0
        
        for x in range(self.COL):
            if self.play(x) != -1:
                if not self.isWinningMove():
                    self.undoMove()
                    return (self.ROW * self.COL + 1 - len(self.MOV)) / 2
                            
        # upper bound of our score as we can't win immediately
        mx = (self.ROW * self.COL - 1 - len(self.MOV)) / 2

        if hi > mx:
            hi = mx
            if lo >= hi:
                return hi
            
        for x in range(self.COL):
            if(self.isValid(x)):
                P2 = self.copy()
                P2.play(x)
                score = -P2.minimax(-hi, -lo)

                if score >= hi:
                    return score
                if score > lo: 
                    lo = score

        return lo

    def undoMove(self):
        if len(self.MOV):
            c = self.MOV[-1]
            self.MOV = self.MOV[:-1]
            for r in range(self.ROW):
                if self.board[r][c] != ' ':
                    self.board[r][c] = ' '
                    return
        else:
            print('Unable to undo move')

    def isValid(self, col):
        return 0 <= col < self.COL and self.board[0][col] == ' '
    
    def play(self, col):
        # tha vao cot da chon va check win chua
        if not self.isValid(col):
            return -1
        
        # tha vao hang thap nhat
        for row in reversed(range(self.ROW)):
            if self.board[row][col] == ' ':
                self.board[row][col] = self.current_player
                self.MOV += str(col)
                return row

    def isWinningMove(self):
        # Check whether there are 4 aligning discs
        # Start with row (r), column (c)
        # Moving in row/horizontal direction (dr), column/vertical direction (dc)
        # player: The disc is of the same color/player
        def check_direction(r, c, dr, dc, player):
            count = 0
            for _ in range(4):
                if 0 <= r < self.ROW and 0 <= c < self.COL and self.board[r][c] == player:
                    count += 1
                    r += dr
                    c += dc
                else:
                    break
            return count == 4

        for r in reversed(range(self.ROW)):
            for c in range(self.COL):
                if self.board[r][c] != ' ':
                    player = self.board[r][c]
                    if (check_direction(r, c, 1, 0, player) or  # Vertical
                            check_direction(r, c, 0, 1, player) or  # Horizontal
                            check_direction(r, c, 1, 1, player) or  # Diagonal /
                            check_direction(r, c, 1, -1, player)):  # Diagonal \
                        return True
        return False
    
    def printBoard(self):
        for row in self.board:
            print(row)
        print("-" * (self.COL * 2 - 1))

########################################################
# board = Board()

# while True:
#     board.printBoard()
#     try:
#         col = int(input("(0-6): "))
#         if col < 0 or col > 6:
#             raise ValueError("nhập từ 0 đến 6!")
#         result = board.play(col)
#         if result == "WIN":
#             break
#     except ValueError:
#         print("nhập từ 0 đến 6!")