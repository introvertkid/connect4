import sys
from Position import Position
from TranspositionTable import TranspositionTable
from TranspositionTable import next_prime

class Book:
    def __init__(self, WIDTH = 7, HEIGHT = 6, DEPTH = -1):
        self.width = WIDTH
        self.height = HEIGHT
        self.depth = DEPTH
        self.T = TranspositionTable()

    def load(self, filename: str):
        f = open(filename, mode="rb")

        _width = f.read(1)
        if not _width or _width[0] != self.width:
            print(f"Unable to load opening book: invalid width (found: {int.from_bytes(_width, 'little')}, expected: {self.width})", file=sys.stderr)
            return

        _height = f.read(1)
        if not _height or _height[0] != self.height:
            print(f"Unable to load opening book: invalid height (found: {int.from_bytes(_height, 'little')}, expected: {self.height})", file=sys.stderr)
            return

        _depth = f.read(1)
        if not _depth or _depth[0] > self.width * self.height:
            print(f"Unable to load opening book: invalid depth (found: {int.from_bytes(_depth, 'little')})", file=sys.stderr)
            return

        partial_key_bytes = f.read(1)
        if not partial_key_bytes or partial_key_bytes[0] > 8:
            print(f"Unable to load opening book: invalid internal key size (found: {int.from_bytes(partial_key_bytes, 'little')})", file=sys.stderr)
            return

        value_bytes = f.read(1)
        if not value_bytes or value_bytes[0] != 1:
            print(f"Unable to load opening book: invalid value size (found: {int.from_bytes(value_bytes, 'little')}, expected: 1)", file=sys.stderr)
            return
        
        log_size = f.read(1)
        if not log_size or log_size[0] > 40:
            print(f"Unable to load opening book: invalid log2(size)(found: {int.from_bytes(log_size)})", file=sys.stderr)

        partial_key_bytes = int.from_bytes(partial_key_bytes, "little")
        value_bytes = int.from_bytes(value_bytes, "little")
        log_size = log_size[0]
        size = next_prime(2 ** log_size)
        keys, values = [], []

        for _ in range(size):
            key_byte = f.read(partial_key_bytes)
            if not key_byte or len(key_byte) != partial_key_bytes:
                print(f"Failed to read key", file=sys.stderr)
                return
            keys.append(int.from_bytes(key_byte, "little"))

        for _ in range(size):
            value_byte = f.read(value_bytes)
            if not value_byte or len(value_byte) != value_bytes:
                print(f"Failed to read value", file=sys.stderr)
                return
            keys.append(int.from_bytes(value_byte, "little"))
        
        key_int = int.from_bytes(key_byte, "little")
        value_int = int.from_bytes(value_byte, "little")
        self.T.put(key_int, value_int)

        f.close()

    def get(self, P: Position):
        if P.nb_moves() > self.depth:
            return 0
        else:
            return self.T.get(P.key3())