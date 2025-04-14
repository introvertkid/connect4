from typing import List

from Position import Position
from TranspositionTable import TranspositionTable
from MoveSorter import MoveSorter
from Book import Book

class Solver:
    INVALID_MOVE = -1000
    TABLE_SIZE = 24  # stores 2^24 elements in the transposition table

    def __init__(self):
        self.book = Book()
        self.transTable = TranspositionTable()
        self.nodeCount = 0
        self.columnOrder = [Position.WIDTH // 2 + (1 - 2 * (i % 2)) * ((i + 1) // 2)
                            for i in range(Position.WIDTH)]

    def negamax(self, P: Position, alpha: int, beta: int) -> int:
        assert alpha < beta
        assert not P.can_win_next()

        self.nodeCount += 1

        possible = P.possible_non_losing_moves()
        if possible == 0:
            return -(Position.WIDTH * Position.HEIGHT - P.nb_moves()) // 2

        if P.nb_moves() >= Position.WIDTH * Position.HEIGHT - 2:
            return 0  # draw

        min_score = -(Position.WIDTH * Position.HEIGHT - 2 - P.nb_moves()) // 2
        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha

        max_score = (Position.WIDTH * Position.HEIGHT - 1 - P.nb_moves()) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta

        key = P.key()
        val = self.transTable.get(key)
        if val:
            if val > Position.MAX_SCORE - Position.MIN_SCORE + 1:
                min_score = val + 2 * Position.MIN_SCORE - Position.MAX_SCORE - 2
                if alpha < min_score:
                    alpha = min_score
                    if alpha >= beta:
                        return alpha
            else:
                max_score = val + Position.MIN_SCORE - 1
                if beta > max_score:
                    beta = max_score
                    if alpha >= beta:
                        return beta

        book_val = self.book.get(P)
        if book_val:
            return book_val + Position.MIN_SCORE - 1

        moves = MoveSorter()
        for i in reversed(range(Position.WIDTH)):
            move = possible & Position._column_mask(self.columnOrder[i])
            if move:
                moves.add(move, P.move_score(move))
        
        while True:
            next_move = moves.get_next()
            if not next_move:
                break
            P2 = P.copy()
            P2.play(next_move)
            score = -self.negamax(P2, -beta, -alpha)
        
            if score >= beta:
                self.transTable.put(key, score + Position.MAX_SCORE - 2 * Position.MIN_SCORE + 2)
                return score
            if score > alpha:
                alpha = score

        self.transTable.put(key, alpha - Position.MIN_SCORE + 1)
        return alpha

    def solve(self, P: Position, weak: bool = False) -> int:
        if P.can_win_next():
            return (Position.WIDTH * Position.HEIGHT + 1 - P.nb_moves()) // 2

        min_score = -(Position.WIDTH * Position.HEIGHT - P.nb_moves()) // 2
        max_score = (Position.WIDTH * Position.HEIGHT + 1 - P.nb_moves()) // 2

        if weak:
            min_score = -1
            max_score = 1

        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2
            if med <= 0 and min_score // 2 < med:
                med = min_score // 2
            elif med >= 0 and max_score // 2 > med:
                med = max_score // 2

            r = self.negamax(P, med, med + 1)
            if r <= med:
                max_score = r
            else:
                min_score = r

        return min_score

    def analyze(self, P: Position, weak: bool = False) -> List[int]:
        scores = [Solver.INVALID_MOVE] * Position.WIDTH
        for col in range(Position.WIDTH):
            if P.can_play(col):
                if P.is_winning_move(col):
                    scores[col] = (Position.WIDTH * Position.HEIGHT + 1 - P.nb_moves()) // 2
                else:
                    P2 = P.copy()
                    P2.play_col(col)
                    scores[col] = -self.solve(P2, weak)
        return scores

    def get_node_count(self) -> int:
        return self.nodeCount
    
    # def reset(self):
    #     self.nodeCount = 0
    #     self.transTable.reset()
    
    def load_book(self, book_file: str):
        self.book.load(book_file)
