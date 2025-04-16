# Position.pyx
import cython
import sys

# --- Khai báo kiểu C ---
ctypedef unsigned long long position_t
ctypedef unsigned int move_count_t

# --- Hằng số Module ---
MODULE_WIDTH = 7
MODULE_HEIGHT = 6

# --- Tính toán Mask (mức module) ---
_temp_bottom_mask: position_t = 0
for w in range(MODULE_WIDTH):
    _temp_bottom_mask |= <position_t>1 << (w * (MODULE_HEIGHT + 1))

BOTTOM_MASK_CONST: position_t = _temp_bottom_mask
BOARD_MASK_CONST: position_t = BOTTOM_MASK_CONST * ((<position_t>1 << MODULE_HEIGHT) - 1)

# --- Lớp Position ---
cdef class Position:
    # --- Thuộc tính instance ---
    cdef public position_t current_position
    cdef public position_t mask
    cdef public move_count_t moves
    cdef list _undo_stack 

    # --- Hằng số lớp ---
    WIDTH = MODULE_WIDTH
    HEIGHT = MODULE_HEIGHT

    if WIDTH >= 10:
        raise ValueError("Chiều rộng của bàn cờ phải nhỏ hơn 10")
    if WIDTH * (HEIGHT + 1) > 64:
         print("Cảnh báo: Kích thước bàn cờ yêu cầu > 64 bit, cần thay đổi kiểu position_t")

    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3

    def __init__(self):
        self.current_position = 0
        self.mask = 0
        self.moves = 0
        self._undo_stack = []  

    cpdef push_state(self):
        """Lưu trạng thái hiện tại để có thể undo sau này."""
        # Lưu dưới dạng tuple (current_position, mask, moves)
        self._undo_stack.append((self.current_position, self.mask, self.moves))

    cpdef pop_state(self):
        """Khôi phục trạng thái vừa lưu trước đó."""
        self.current_position, self.mask, self.moves = self._undo_stack.pop()

    # --- Các hàm static (mức module) ---
    @staticmethod
    @cython.returns(position_t) # Giữ kiểu trả về của Cython
    def _column_mask(col: cython.int, height: cython.int) -> position_t:
        return ((<position_t>1 << height) - 1) << (col * (height + 1))

    @staticmethod
    @cython.returns(position_t)
    def _top_mask_col(col: cython.int, height: cython.int) -> position_t:
        return <position_t>1 << (height - 1 + col * (height + 1))

    @staticmethod
    @cython.returns(position_t)
    def _bottom_mask_col(col: cython.int, height: cython.int) -> position_t:
        return <position_t>1 << (col * (height + 1))

    # --- Phương thức instance ---
    @cython.ccall
    def play(self, move: position_t):
        self.current_position ^= self.mask
        self.mask |= move
        self.moves += 1

    def play_seq(self, seq: str) -> cython.int:
        played_moves: cython.int = 0
        col: cython.int
        for i, char in enumerate(seq):
            if not char.isdigit():
                return played_moves
            col = int(char) - 1
            if not (0 <= col < self.WIDTH):
                 return played_moves
            if not self.can_play(col):
                 return played_moves
            if self.is_winning_move(col):
                 return played_moves
            self.play_col(col)
            played_moves += 1
        return played_moves

    @cython.ccall
    @cython.returns(cython.bint)
    def can_win_next(self) -> cython.bint:
        return self._winning_position() & self._possible() != 0

    @cython.ccall
    @cython.returns(move_count_t)
    def nb_moves(self) -> move_count_t:
        return self.moves

    @cython.ccall
    @cython.returns(position_t)
    def key(self) -> position_t:
        return self.current_position + self.mask

    @cython.ccall
    def _partial_key3(self, current_key: cython.longlong, col: cython.int) -> cython.longlong:
        key_local: cython.longlong = current_key
        pos: position_t = <position_t>1 << (col * (self.HEIGHT + 1))
        while pos & self.mask:
            key_local *= 3
            if pos & self.current_position:
                key_local += 1
            else:
                key_local += 2
            pos <<= 1
        key_local *= 3
        return key_local

    def key3(self) -> cython.longlong:
        key_forward: cython.longlong = 0
        key_reverse: cython.longlong = 0
        for i in range(self.WIDTH):
            key_forward = self._partial_key3(key_forward, i)
        for i in range(self.WIDTH - 1, -1, -1):
            key_reverse = self._partial_key3(key_reverse, i)
        return min(key_forward, key_reverse) // 3

    @cython.ccall
    @cython.returns(position_t)
    def possible_non_losing_moves(self) -> position_t:
        possible_mask: position_t = self._possible()
        opponent_win_mask: position_t = self._opponent_winning_position()
        forced_moves: position_t = possible_mask & opponent_win_mask
        if forced_moves != 0:
            if forced_moves & (forced_moves - 1):
                return 0
            else:
                possible_mask = forced_moves
        return possible_mask & ~(opponent_win_mask >> 1)

    @cython.ccall
    @cython.returns(cython.int)
    def move_score(self, move: position_t) -> cython.int:
        new_position: position_t = self.current_position | move
        new_mask: position_t = self.mask | move
        return self._popcount(self._compute_winning_position(new_position, new_mask))

    @cython.ccall
    @cython.returns(cython.bint)
    def can_play(self, col: cython.int) -> cython.bint:
        # Gọi staticmethod bằng self. hoặc Position.
        return (self.mask & self._top_mask_col(col, self.HEIGHT)) == 0

    @cython.ccall
    def play_col(self, col: cython.int):
        # Gọi staticmethod bằng self. hoặc Position.
        move: position_t = (self.mask + self._bottom_mask_col(col, self.HEIGHT)) & self._column_mask(col, self.HEIGHT)
        self.play(move)

    @cython.ccall
    @cython.returns(cython.bint)
    def is_winning_move(self, col: cython.int) -> cython.bint:
         # Gọi staticmethod bằng self. hoặc Position.
        return (self._winning_position() & self._possible() & self._column_mask(col, self.HEIGHT)) != 0

    @cython.ccall
    @cython.returns(position_t)
    def _winning_position(self) -> position_t:
        return self._compute_winning_position(self.current_position, self.mask)

    @cython.ccall
    @cython.returns(position_t)
    def _opponent_winning_position(self) -> position_t:
        opponent_position: position_t = self.mask ^ self.current_position
        return self._compute_winning_position(opponent_position, self.mask)

    @cython.ccall
    @cython.returns(position_t)
    def _possible(self) -> position_t:
        return (self.mask + BOTTOM_MASK_CONST) & BOARD_MASK_CONST

    @cython.ccall
    @cython.returns(cython.int)
    def _popcount(self, m: position_t) -> cython.int:
        c: cython.int = 0
        while m:
            m &= m - 1
            c += 1
        return c

    @cython.cfunc
    @cython.returns(position_t)
    @cython.exceptval(check=False)
    @cython.cdivision(True)
    def _compute_winning_position(self, position: position_t, mask: position_t) -> position_t:
        r: position_t
        p: position_t
        H: cython.int = self.HEIGHT
        H1: cython.int = H + 1
        H2: cython.int = H + 2

        # Vertical
        r = (position << 1) & (position << 2) & (position << 3)

        # Horizontal
        p = (position << H1) & (position << (2 * H1))
        r |= p & (position << (3 * H1))
        r |= p & (position >> H1)
        p = (position >> H1) & (position >> (2 * H1))
        r |= p & (position << H1)
        r |= p & (position >> (3 * H1))

        # Diagonal 1 (\)
        p = (position << H) & (position << (2 * H))
        r |= p & (position << (3 * H))
        r |= p & (position >> H)
        p = (position >> H) & (position >> (2 * H))
        r |= p & (position << H)
        r |= p & (position >> (3 * H))

        # Diagonal 2 (/)
        p = (position << H2) & (position << (2 * H2))
        r |= p & (position << (3 * H2))
        r |= p & (position >> H2)
        p = (position >> H2) & (position >> (2 * H2))
        r |= p & (position << H2)
        r |= p & (position >> (3 * H2))

        return r & (BOARD_MASK_CONST ^ mask)

    @cython.ccall
    def copy(self) -> Position:
        new_pos = Position()
        new_pos.current_position = self.current_position
        new_pos.mask = self.mask
        new_pos.moves = self.moves
        return new_pos