import copy

class Board:
    ROW = 6
    COL = 7

    def __init__(self, Row = 6, Col = 7, Mov = ""):
        self.board = [[0 for _ in range(self.COL)] 
                        for _ in range(self.ROW)]
        self.ROW = Row
        self.COL = Col
        self.current_player = 1
        self.MOV = []
        for i in Mov:
            self.play(int(i)-1)
            self.printBoard()

    def copy(self):
        return copy.deepcopy(self)
    
    def changePlayer(self):
        self.current_player = 3 - self.current_player

    def minimax(self, alpha, beta):
        # check for draw game
        if len(self.MOV) == self.ROW * self.COL:
            return 0
        
        for x in range(self.COL):
            if self.play(x) != -1:
                if self.isWinningMove():
                    return (self.ROW * self.COL + 1 - len(self.MOV)) / 2
                else:
                    self.undoMove()
                            
        # upper bound of our score as we can't win immediately
        mx = (self.ROW * self.COL - 1 - len(self.MOV)) / 2

        if beta > mx:
            beta = mx
            if alpha >= beta:
                return beta
            
        for x in range(self.COL):
            if(self.isValid(x)):
                P2 = self.copy()
                P2.play(x)
                score = -P2.minimax(-beta, -alpha)

                if score >= beta:
                    return score
                if score > alpha: 
                    alpha = score

        return alpha

    def undoMove(self):
        if len(self.MOV):
            c = self.MOV[-1]
            self.MOV.pop()
            for r in range(self.ROW):
                if self.board[r][c] != 0:
                    self.board[r][c] = 0
                    self.changePlayer()
                    return
        else:
            print('Unable to undo move')

    def isValid(self, col):
        return 0 <= col < self.COL and self.board[0][col] == 0
    
    def play(self, col):
        # tha vao cot da chon va check win chua
        if not self.isValid(col):
            return -1
        
        # tha vao hang thap nhat
        for row in reversed(range(self.ROW)):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                self.MOV.append(col)
                self.changePlayer()
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
                if self.board[r][c] != 0:
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
if __name__ == "__main__":
    board = Board(Mov = "6216633712715125334265163163777225")
    board.printBoard()
    print(board.MOV)
    print('score after run minimax:', board.minimax(-100, 100))