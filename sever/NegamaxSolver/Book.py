import struct
import sys
import os
from array import array # Sử dụng array để lưu trữ dữ liệu nhị phân hiệu quả hơn list
from .TranspositionTable import med, has_factor, next_prime

class Position:
    # Cần triển khai các phương thức này một cách chính xác
    _nb_moves: int = 0
    _key3: int = 0 # uint64_t

    def nb_moves(self) -> int:
        return self._nb_moves

    def set_nb_moves(self, moves: int):
        self._nb_moves = moves

    def key3(self) -> int:
        # Cần trả về giá trị uint64_t tương ứng với thế cờ
        return self._key3

    def set_key3(self, key: int):
        # Đảm bảo key là số nguyên không âm (mô phỏng uint64_t)
        self._key3 = key & 0xFFFFFFFFFFFFFFFF # Giữ trong giới hạn 64-bit

class Book:
    """
    Quản lý Opening Book cho Connect4, được tải từ tệp nhị phân.

    Lớp này đọc và ghi các tệp opening book có định dạng cụ thể
    và cung cấp quyền truy cập vào các giá trị được lưu trữ.

    *** CHỨC NĂNG GIỐNG HỆT C++ ***
    Phiên bản này được cập nhật để khớp với logic của
    TranspositionTable.hpp đã cung cấp:
    - Kích thước bảng là số nguyên tố >= 2^log_size.
    - Index được tính bằng phép toán modulo (%).
    - Khóa một phần là các bit thấp của khóa đầy đủ, được xác định
      bởi partial_key_bytes.
    """

    def __init__(self, width: int, height: int):
        """ Khởi tạo một OpeningBook trống. """
        self.width: int = width
        self.height: int = height
        self.depth: int = -1
        self.log_size: int = 0  # log_size gốc đọc từ file
        self.size: int = 0      # Kích thước số nguyên tố thực tế của bảng
        self.partial_key_bytes: int = 0
        self.value_bytes: int = 1 # Luôn là 1

        self.partial_keys = None # array.array
        self.values = None       # array.array('B')

        # Mặt nạ để tính/ép kiểu khóa một phần
        self._partial_key_mask = 0

    def _calculate_partial_key(self, full_key: int) -> int:
        """
        Tính toán khóa một phần bằng cách áp dụng mặt nạ.
        Tương đương với việc ép kiểu (partial_key_t)key trong C++.
        """
        return full_key & self._partial_key_mask

    def load(self, filename: str) -> bool:
        """ Tải opening book từ một tệp nhị phân. """
        # Đặt lại trạng thái
        self.depth = -1
        self.partial_keys = None
        self.values = None
        self.size = 0
        self.log_size = 0
        self._partial_key_mask = 0

        if not os.path.exists(filename):
            print(f"Lỗi: Không thể tải opening book: Tệp không tồn tại '{filename}'", file=sys.stderr)
            return False

        try:
            with open(filename, 'rb') as ifs:
                print(f"Đang tải opening book từ tệp: {filename}. ", end="", file=sys.stderr)

                # Đọc header (6 bytes)
                header_format = 'bbbbbb' # width, height, depth, partial_key_bytes, value_bytes, log_size
                header_size = struct.calcsize(header_format)
                header_data = ifs.read(header_size)
                if len(header_data) < header_size:
                    print("Lỗi: Không thể đọc đủ header từ tệp.", file=sys.stderr)
                    return False

                _width, _height, _depth, _partial_key_bytes, _value_bytes, _log_size = struct.unpack(header_format, header_data)

                # --- Xác thực Header ---
                # (Giữ nguyên các kiểm tra width, height, depth, value_bytes)
                if _width != self.width or _height != self.height or \
                   not (0 <= _depth <= self.width * self.height) or _value_bytes != 1:
                    print(f"Lỗi: Header không hợp lệ (w:{_width}, h:{_height}, d:{_depth}, v_bytes:{_value_bytes})", file=sys.stderr)
                    return False # Rút gọn thông báo lỗi

                if _partial_key_bytes not in [1, 2, 4]:
                    print(f"Lỗi: Kích thước khóa nội bộ không hợp lệ: {_partial_key_bytes} bytes (chỉ hỗ trợ 1, 2, 4)", file=sys.stderr)
                    return False

                if not (0 < _log_size <= 40): # Giữ giới hạn tổng quát từ C++
                    print(f"Lỗi: log2(size) không hợp lệ: {_log_size}", file=sys.stderr)
                    return False
                # Optional: Warning nếu log_size ngoài phạm vi C++ init (21-27)
                # if not (21 <= _log_size <= 27):
                #     print(f"Cảnh báo: log_size ({_log_size}) nằm ngoài phạm vi C++ gốc (21-27).", file=sys.stderr)

                # --- Khởi tạo cấu trúc dữ liệu ---
                self.log_size = _log_size # Lưu log_size gốc
                target_power_of_2 = 1 << self.log_size
                # Tính kích thước số nguyên tố thực tế
                print(f"Tính toán kích thước bảng (số nguyên tố >= 2^{self.log_size})...", end="", file=sys.stderr)
                self.size = next_prime(target_power_of_2)
                print(f" size={self.size}. ", end="", file=sys.stderr)

                self.partial_key_bytes = _partial_key_bytes
                self.value_bytes = _value_bytes # Luôn là 1

                # Xác định kiểu dữ liệu và mặt nạ cho partial_keys
                if self.partial_key_bytes == 1:
                    pk_typecode = 'B'; self._partial_key_mask = 0xFF
                elif self.partial_key_bytes == 2:
                    pk_typecode = 'H'; self._partial_key_mask = 0xFFFF
                elif self.partial_key_bytes == 4:
                    pk_typecode = 'I' if array('I').itemsize == 4 else 'L'
                    if array(pk_typecode).itemsize != 4:
                        pk_typecode = 'L' # Thử lại L nếu I sai
                        if array(pk_typecode).itemsize != 4:
                              print(f"Lỗi: Không tìm thấy kiểu unsigned int 4 byte ('I' hoặc 'L')", file=sys.stderr)
                              return False
                    self._partial_key_mask = 0xFFFFFFFF
                else:
                     # Trường hợp này đã được kiểm tra, nhưng để an toàn
                     print(f"Lỗi: partial_key_bytes không hợp lệ: {self.partial_key_bytes}", file=sys.stderr)
                     return False

                # Khởi tạo mảng
                self.partial_keys = array(pk_typecode)
                self.values = array('B')

                # --- Đọc dữ liệu mảng (sử dụng self.size là số nguyên tố) ---
                pk_data_size = self.size * self.partial_key_bytes
                print(f"Đọc {pk_data_size} bytes khóa... ", end="", file=sys.stderr)
                pk_data = ifs.read(pk_data_size)
                if len(pk_data) < pk_data_size:
                    print(f"Lỗi: Không đọc đủ ({len(pk_data)}/{pk_data_size})", file=sys.stderr)
                    return False
                self.partial_keys.frombytes(pk_data)

                v_data_size = self.size * self.value_bytes
                print(f"Đọc {v_data_size} bytes giá trị... ", end="", file=sys.stderr)
                v_data = ifs.read(v_data_size)
                if len(v_data) < v_data_size:
                    print(f"Lỗi: Không đọc đủ ({len(v_data)}/{v_data_size})", file=sys.stderr)
                    return False
                self.values.frombytes(v_data)

                # Kiểm tra lại kích thước mảng sau khi đọc
                if len(self.partial_keys) != self.size or len(self.values) != self.size:
                    print(f"Lỗi: Kích thước mảng không khớp sau khi đọc (keys:{len(self.partial_keys)}, vals:{len(self.values)}, expected:{self.size})", file=sys.stderr)
                    return False

                # Nếu mọi thứ thành công
                self.depth = _depth
                print("Xong.", file=sys.stderr) # In hoa chữ Xong cho đẹp
                return True

        except FileNotFoundError:
             print(f"Lỗi: Không thể tải opening book: Tệp không tồn tại '{filename}'", file=sys.stderr)
             return False
        except struct.error as e:
             print(f"Lỗi: Lỗi giải mã cấu trúc header: {e}", file=sys.stderr)
             return False
        except MemoryError:
             total_bytes = header_size + (self.size * self.partial_key_bytes) + (self.size * self.value_bytes)
             print(f"Lỗi: Không đủ bộ nhớ để tải opening book (ước tính cần {total_bytes / (1024*1024):.2f} MB cho size {self.size})", file=sys.stderr)
             return False
        except EOFError:
             print(f"Lỗi: Kết thúc tệp không mong muốn khi đang đọc dữ liệu.", file=sys.stderr)
             return False
        except Exception as e:
             print(f"Lỗi không xác định khi tải opening book: {e}", file=sys.stderr)
             return False

    def save(self, output_file: str) -> bool:
        """ Lưu opening book hiện tại vào một tệp nhị phân. """
        if not self.is_loaded(): # Dùng is_loaded cho gọn
            print("Lỗi: Không có dữ liệu opening book hợp lệ để lưu.", file=sys.stderr)
            return False

        # Kích thước mảng đã được is_loaded() kiểm tra gián tiếp qua self.size > 0

        try:
            with open(output_file, 'wb') as ofs:
                # Ghi header
                header_format = 'bbbbbb'
                # *** QUAN TRỌNG: Ghi log_size GỐC vào header, không phải log2 của số nguyên tố ***
                # Điều này khớp với cách C++ đọc và ghi (dù hàm log2 trong save C++ hơi lạ)
                header_data = struct.pack(header_format,
                                          self.width,
                                          self.height,
                                          self.depth,
                                          self.partial_key_bytes,
                                          self.value_bytes, # Luôn là 1
                                          self.log_size)     # Ghi log_size gốc
                ofs.write(header_data)

                # Ghi mảng khóa một phần (dùng kích thước số nguyên tố self.size)
                self.partial_keys.tofile(ofs)

                # Ghi mảng giá trị (dùng kích thước số nguyên tố self.size)
                self.values.tofile(ofs)

            print(f"Đã lưu opening book vào: {output_file} (size={self.size}, log_size={self.log_size})", file=sys.stderr)
            return True
        except IOError as e:
            print(f"Lỗi: Không thể ghi vào tệp '{output_file}': {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Lỗi không xác định khi lưu opening book: {e}", file=sys.stderr)
            return False


    def get(self, P: Position) -> int:
        """
        Lấy giá trị được lưu trữ cho một thế cờ từ opening book.
        Sử dụng logic khớp với C++ TranspositionTable:
        - Index = full_key % prime_size
        - So sánh partial_key đã lưu với (partial_key_t)full_key
        """
        if self.depth == -1 or P.nb_moves() > self.depth or self.size == 0:
            return 0

        full_key = P.key3()

        # Tính index bằng modulo với kích thước số nguyên tố
        index = full_key % self.size

        # Tính khóa một phần mong đợi từ khóa đầy đủ (ép kiểu ngầm qua mask)
        partial_key_expected = self._calculate_partial_key(full_key)

        # Kiểm tra xem khóa một phần tại chỉ số có khớp không
        # self.partial_keys đã có kiểu dữ liệu đúng (B, H, I/L)
        if self.partial_keys[index] == partial_key_expected:
            # Khớp cả index và khóa một phần -> trả về giá trị
            return self.values[index]
        else:
            # Không khớp khóa một phần (trống hoặc xung đột) -> Không tìm thấy
            return 0

    def is_loaded(self) -> bool:
        """Kiểm tra xem book đã được tải thành công và có dữ liệu hay chưa."""
        # size > 0 ngụ ý rằng log_size > 0 và next_prime đã chạy
        return self.depth != -1 and self.size > 0 and \
               self.partial_keys is not None and self.values is not None and \
               len(self.partial_keys) == self.size and len(self.values) == self.size
