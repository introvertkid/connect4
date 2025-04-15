import math
import sys
import copy

class Position:
    """
    Lớp lưu trữ một thế cờ Connect 4.
    Các hàm liên quan đến người chơi hiện tại.
    Lớp này không hỗ trợ các thế cờ đã có đường thẳng thắng.

    Sử dụng biểu diễn bitboard nhị phân.
    Mỗi cột được mã hóa trên HEIGHT + 1 bit.

    Ví dụ về thứ tự bit để mã hóa cho bàn cờ 7x6:
     .  .  .  .  .  .  .
    47 40 33 26 19 12  5  (bit cao nhất)
    46 39 32 25 18 11  4
    45 38 31 24 17 10  3
    44 37 30 23 16  9  2
    43 36 29 22 15  8  1
    42 35 28 21 14  7  0  (bit thấp nhất)

    Thế cờ được lưu trữ dưới dạng:
    - Một bitboard "mask" với 1 ở bất kỳ vị trí nào có quân cờ.
    - Một bitboard "current_position" với 1 ở các vị trí quân cờ của người chơi hiện tại.

    Bitboard "current_position" có thể được biến đổi thành một khóa gọn nhẹ và không mơ hồ
    bằng cách thêm một bit phụ vào ô trống trên cùng của mỗi cột.
    Điều này cho phép xác định tất cả các ô trống mà không cần bitboard "mask".

    current_player "x" = 1, opponent "o" = 0
    board       position   mask       key        bottom
                0000000   0000000   0000000   0000000
    .......     0000000   0000000   0001000   0000000  (chỉ có mask thay đổi để đánh dấu ô trống trên cùng)
    ...o...     0000000   0001000   0010000   0000000  (o=0, nên current_position không đổi)
    ..xx...     0011000   0011000   0011000   0000000  (x=1)
    ..ox...     0001000   0011000   0001100   0000000  (x=1)
    ..oox..     0000100   0011100   0000110   0000000  (x=1)
    ..oxxo.     0001100   0011110   1101101   1111111  (x=1)

    current_player "o" = 1, opponent "x" = 0
    board       position   mask       key        bottom
                0000000   0000000   0001000   0000000
    ...x...     0000000   0001000   0000000   0000000  (x=0)
    ...o...     0001000   0001000   0011000   0000000  (o=1)
    ..xx...     0000000   0011000   0000000   0000000  (x=0)
    ..ox...     0010000   0011000   0010100   0000000  (o=1)
    ..oox..     0011000   0011100   0011010   0000000  (o=1)
    ..oxxo.     0010010   0011110   1110011   1111111  (o=1)

    key là một biểu diễn duy nhất của bàn cờ: key = current_position + mask
    (vì bottom là hằng số, nó không cần thiết để phân biệt các thế cờ).
    """

    WIDTH = 7  
    HEIGHT = 6 

    if WIDTH >= 10:
        raise ValueError("Chiều rộng của bàn cờ phải nhỏ hơn 10")
    if WIDTH * (HEIGHT + 1) > 64 and sys.int_info.bits_per_digit < 64:
         print("Cảnh báo: Kích thước bàn cờ có thể vượt quá 64 bit, yêu cầu hỗ trợ số nguyên lớn.")
    if WIDTH * (HEIGHT + 1) > 128:
         raise ValueError("Bàn cờ không vừa với bitmask 128 bit")


    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3

    BOTTOM_MASK = 0
    for w in range(WIDTH):
        BOTTOM_MASK |= 1 << (w * (HEIGHT + 1))

    BOARD_MASK = BOTTOM_MASK * ((1 << HEIGHT) - 1)

    def __init__(self):
        self.current_position = 0  
        self.mask = 0             
        self.moves = 0         

    @staticmethod
    def _top_mask_col(col: int) -> int:
        return 1 << (Position.HEIGHT - 1 + col * (Position.HEIGHT + 1))

    @staticmethod
    def _bottom_mask_col(col: int) -> int:
        return 1 << (col * (Position.HEIGHT + 1))

    @staticmethod
    def _column_mask(col: int) -> int:
        return ((1 << Position.HEIGHT) - 1) << (col * (Position.HEIGHT + 1))

    def play(self, move: int):
        self.current_position ^= self.mask
        self.mask |= move
        self.moves += 1

    def play_seq(self, seq: str) -> int:
        played_moves = 0
        for i, c in enumerate(seq):
            if not c.isdigit():
                return played_moves

            col = int(c) - 1
            if not (0 <= col < self.WIDTH):
                 return played_moves

            if not self.can_play(col):
                 return played_moves 
             
            if self.is_winning_move(col):
                 return played_moves 

            self.play_col(col)
            played_moves += 1
        print(f"Played {played_moves} moves")

        return played_moves

    def can_win_next(self) -> bool:
        return bool(self._winning_position() & self._possible())

    def nb_moves(self) -> int:
        return self.moves

    def key(self) -> int:
        return self.current_position + self.mask

    def _partial_key3(self, current_key: int, col: int) -> int:
        key = current_key
        pos = 1 << (col * (self.HEIGHT + 1))
        while pos & self.mask: 
            key *= 3
            if pos & self.current_position: 
                key += 1
            else: 
                key += 2
            pos <<= 1
        key *= 3 
        return key

    def key3(self) -> int:
        key_forward = 0
        for i in range(self.WIDTH):
            key_forward = self._partial_key3(key_forward, i)

        key_reverse = 0
        for i in range(self.WIDTH - 1, -1, -1):
            key_reverse = self._partial_key3(key_reverse, i)

        return min(key_forward, key_reverse) // 3


    def possible_non_losing_moves(self) -> int:
        assert not self.can_win_next()

        possible_mask = self._possible()
        opponent_win_mask = self._opponent_winning_position()
        forced_moves = possible_mask & opponent_win_mask 

        if forced_moves:
            if forced_moves & (forced_moves - 1):
                return 0
            else:
                possible_mask = forced_moves
        return possible_mask & ~(opponent_win_mask >> 1)


    def move_score(self, move: int) -> int:
        new_position = self.current_position | move
        new_mask = self.mask | move
        return self._popcount(self._compute_winning_position(new_position, new_mask))

    def can_play(self, col: int) -> bool:
        return (self.mask & self._top_mask_col(col)) == 0

    def play_col(self, col: int):
        move = (self.mask + self._bottom_mask_col(col)) & self._column_mask(col)
        self.play(move) 

    def is_winning_move(self, col: int) -> bool:
        return bool(self._winning_position() & self._possible() & self._column_mask(col))

    def _winning_position(self) -> int:
       return self._compute_winning_position(self.current_position, self.mask)

    def _opponent_winning_position(self) -> int:
        opponent_position = self.mask ^ self.current_position
        return self._compute_winning_position(opponent_position, self.mask)

    def _possible(self) -> int:
        return (self.mask + self.BOTTOM_MASK) & self.BOARD_MASK

    @staticmethod
    def _popcount(m: int) -> int:
        if hasattr(m, "bit_count"):
             return m.bit_count()
        c = 0
        while m > 0:
            m &= m - 1 
            c += 1
        return c

    @staticmethod
    def _compute_winning_position(position: int, mask: int) -> int:
        r = (position << 1) & (position << 2) & (position << 3)

        p = (position << (Position.HEIGHT + 1)) & (position << 2 * (Position.HEIGHT + 1))
        r |= p & (position << 3 * (Position.HEIGHT + 1)) # XXXO
        r |= p & (position >> (Position.HEIGHT + 1))     # XXOX
        p = (position >> (Position.HEIGHT + 1)) & (position >> 2 * (Position.HEIGHT + 1))
        r |= p & (position << (Position.HEIGHT + 1))     # XOXX
        r |= p & (position >> 3 * (Position.HEIGHT + 1)) # OXXX

        p = (position << Position.HEIGHT) & (position << 2 * Position.HEIGHT)
        r |= p & (position << 3 * Position.HEIGHT)
        r |= p & (position >> Position.HEIGHT)
        p = (position >> Position.HEIGHT) & (position >> 2 * Position.HEIGHT)
        r |= p & (position << Position.HEIGHT)
        r |= p & (position >> 3 * Position.HEIGHT)

        p = (position << (Position.HEIGHT + 2)) & (position << 2 * (Position.HEIGHT + 2))
        r |= p & (position << 3 * (Position.HEIGHT + 2))
        r |= p & (position >> (Position.HEIGHT + 2))
        p = (position >> (Position.HEIGHT + 2)) & (position >> 2 * (Position.HEIGHT + 2))
        r |= p & (position << (Position.HEIGHT + 2))
        r |= p & (position >> 3 * (Position.HEIGHT + 2))

        return r & (Position.BOARD_MASK ^ mask)
    
    def copy(self):
        return copy.deepcopy(self)