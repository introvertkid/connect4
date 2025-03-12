class Board:
    COL = 7
    ROW = 6
    MOV = ""

    def __init__(self):
        self.board = [[' ' for _ in range(self.COL)] 
                        for _ in range(self.ROW)] 
        self.current_player = 'X'

    def isValid(self, col):
        return 0 <= col < self.COL and self.board[0][col] == ' '
    
    def play(self, col):
        # tha vao cot da chon va check win chua
        if not self.isValid(col):
            return False
        
        # tha vao hang thap nhat
        for row in reversed(range(self.ROW)):
            if self.board[row][col] == ' ':
                self.board[row][col] = self.current_player
                break
        
        # check win
        if self.isWinningMove(self.ROW, self.COL):
            self.printBoard()
            print(f"{self.current_player} WIN!")
            return "WIN"
        
        # chuyen nguoi choi
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def isWinningMove(self, ROW, COL):
        # Check whether there are 4 aligning discs
        # Start with row (r), column (c)
        # Moving in row/horizontal direction (dr), column/vertical direction (dc)
        # player: The disc is of the same color/player
        def check_direction(r, c, dr, dc, player):
            count = 0
            for _ in range(4):
                if 0 <= r < ROW and 0 <= c < COL and self.board[r][c] == player:
                    print(r, ' ', c)
                    count += 1
                    r += dr
                    c += dc
                else:
                    break
            return count == 4

        for r in reversed(range(ROW)):
            for c in range(COL):
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
            print("|".join(row))
        print("-" * (self.COL * 2 - 1))

########################################################
board = Board()

while True:
    board.printBoard()
    try:
        col = int(input("(0-6): "))
        result = board.play(col)
        if result == "WIN":
            break
    except ValueError:
        print("nhập từ 0-6!")