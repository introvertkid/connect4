import struct
import math
import sys
import os
from array import array # Sử dụng array để lưu trữ dữ liệu nhị phân hiệu quả hơn list

# Giả định rằng lớp Position đã được định nghĩa ở đâu đó, ví dụ:
# from position_module import Position
# Tạm thời định nghĩa một lớp giả lập để code chạy được
class Position:
    def nbMoves(self) -> int:
        # Placeholder
        return 0
    def key3(self) -> int:
        # Placeholder - Cần trả về giá trị uint64_t tương ứng
        return 0

class Book:
    """
    Quản lý Opening Book cho Connect4, được tải từ tệp nhị phân.

    Lớp này đọc và ghi các tệp opening book có định dạng cụ thể
    và cung cấp quyền truy cập vào các giá trị được lưu trữ (thường là điểm số
    hoặc thông tin nước đi) cho các thế cờ dựa trên key3 đối xứng của chúng.

    Giả định quan trọng về cấu trúc dữ liệu TranspositionTable gốc của C++
    được sử dụng để đảm bảo tính tương thích của định dạng tệp.
    """

    def __init__(self, width: int, height: int):
        """
        Khởi tạo một OpeningBook trống.

        Args:
            width: Chiều rộng mong đợi của bàn cờ.
            height: Chiều cao mong đợi của bàn cờ.
        """
        self.width: int = width
        self.height: int = height
        self.depth: int = -1 # Độ sâu tối đa của các thế cờ trong book (-1 nghĩa là chưa tải)
        self.log_size: int = 0
        self.size: int = 0
        self.partial_key_bytes: int = 0
        self.value_bytes: int = 1 # Giá trị luôn là 1 byte (uint8_t) theo C++

        # Sử dụng array.array để lưu trữ hiệu quả hơn list thông thường
        # Kiểu dữ liệu sẽ được xác định khi load
        self.partial_keys = None # Sẽ là array('B'), array('H'), hoặc array('L')
        self.values = None       # Sẽ là array('B')

        # Mặt nạ để tính partial key (giả định lấy các byte thấp)
        self._partial_key_mask = 0

    def _calculate_partial_key(self, full_key: int) -> int:
        """
        Tính toán khóa một phần từ khóa đầy đủ (key3).

        *** Giả định quan trọng: ***
        Giả định này là lấy các byte thấp nhất của full_key.
        Logic thực tế của TranspositionTable C++ có thể khác.

        Args:
            full_key: Khóa đầy đủ (ví dụ: P.key3()).

        Returns:
            Khóa một phần được tính toán.
        """
        if self.partial_key_bytes == 0:
            return 0 # Hoặc raise lỗi nếu chưa load
        # Sử dụng mặt nạ đã tính toán trong load()
        return full_key & self._partial_key_mask

    def load(self, filename: str) -> bool:
        """
        Tải opening book từ một tệp nhị phân.

        Định dạng tệp được mong đợi (như trong mã C++):
        - 1 byte: chiều rộng bàn cờ
        - 1 byte: chiều cao bàn cờ
        - 1 byte: độ sâu tối đa được lưu trữ
        - 1 byte: kích thước khóa một phần (tính bằng byte)
        - 1 byte: kích thước giá trị (tính bằng byte, phải là 1)
        - 1 byte: log_size = log2(kích thước bảng)
        - Mảng khóa một phần (size * partial_key_bytes)
        - Mảng giá trị (size * value_bytes)

        Args:
            filename: Đường dẫn đến tệp opening book.

        Returns:
            True nếu tải thành công, False nếu có lỗi.
        """
        self.depth = -1 # Đặt lại trạng thái
        self.partial_keys = None
        self.values = None
        self.size = 0
        self.log_size = 0

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
                if _width != self.width:
                    print(f"Lỗi: Chiều rộng không hợp lệ (tìm thấy: {_width}, mong đợi: {self.width})", file=sys.stderr)
                    return False
                if _height != self.height:
                    print(f"Lỗi: Chiều cao không hợp lệ (tìm thấy: {_height}, mong đợi: {self.height})", file=sys.stderr)
                    return False
                if not (0 <= _depth <= self.width * self.height):
                    print(f"Lỗi: Độ sâu không hợp lệ (tìm thấy: {_depth})", file=sys.stderr)
                    return False
                if _partial_key_bytes not in [1, 2, 4]: # Kích thước khóa hợp lệ C++ hỗ trợ
                    print(f"Lỗi: Kích thước khóa nội bộ không hợp lệ (tìm thấy: {_partial_key_bytes} bytes)", file=sys.stderr)
                    return False
                if _value_bytes != 1:
                    print(f"Lỗi: Kích thước giá trị không hợp lệ (tìm thấy: {_value_bytes}, mong đợi: 1)", file=sys.stderr)
                    return False
                if not (0 < _log_size <= 40): # Giới hạn log_size hợp lý
                    print(f"Lỗi: log2(size) không hợp lệ (tìm thấy: {_log_size})", file=sys.stderr)
                    return False

                # --- Khởi tạo cấu trúc dữ liệu ---
                self.log_size = _log_size
                self.size = 1 << self.log_size # Giả định kích thước là 2^log_size
                self.partial_key_bytes = _partial_key_bytes
                self.value_bytes = _value_bytes # Luôn là 1

                # Chọn kiểu dữ liệu cho mảng partial_keys dựa trên số byte
                if self.partial_key_bytes == 1:
                    pk_typecode = 'B' # unsigned char
                    self._partial_key_mask = 0xFF
                elif self.partial_key_bytes == 2:
                    pk_typecode = 'H' # unsigned short
                    self._partial_key_mask = 0xFFFF
                elif self.partial_key_bytes == 4:
                    pk_typecode = 'L' # unsigned long (thường là 4 byte) hoặc 'I' (unsigned int)
                    # Kiểm tra kích thước thực tế của 'L' trên hệ thống nếu cần độ chính xác cao
                    # Trên hầu hết các hệ thống 64-bit hiện đại, 'L' và 'I' thường là 4 byte
                    pk_typecode = 'I' if array('I').itemsize == 4 else 'L'
                    if array(pk_typecode).itemsize != 4:
                         print(f"Lỗi: Không tìm thấy kiểu unsigned int 4 byte ('I' hoặc 'L')", file=sys.stderr)
                         return False
                    self._partial_key_mask = 0xFFFFFFFF
                else:
                     # Trường hợp này đã được kiểm tra ở trên, nhưng để rõ ràng
                     print(f"Lỗi: partial_key_bytes không được hỗ trợ: {self.partial_key_bytes}", file=sys.stderr)
                     return False


                self.partial_keys = array(pk_typecode)
                self.values = array('B') # unsigned char cho giá trị uint8_t

                # --- Đọc dữ liệu mảng ---
                # Đọc mảng khóa một phần
                pk_data_size = self.size * self.partial_key_bytes
                pk_data = ifs.read(pk_data_size)
                if len(pk_data) < pk_data_size:
                    print(f"Lỗi: Không thể đọc đủ dữ liệu khóa ({len(pk_data)}/{pk_data_size} bytes)", file=sys.stderr)
                    return False
                self.partial_keys.frombytes(pk_data)

                # Đọc mảng giá trị
                v_data_size = self.size * self.value_bytes
                v_data = ifs.read(v_data_size)
                if len(v_data) < v_data_size:
                    print(f"Lỗi: Không thể đọc đủ dữ liệu giá trị ({len(v_data)}/{v_data_size} bytes)", file=sys.stderr)
                    return False
                self.values.frombytes(v_data)

                # Nếu mọi thứ thành công
                self.depth = _depth
                print("xong.", file=sys.stderr)
                return True

        except FileNotFoundError:
             print(f"Lỗi: Không thể tải opening book: Tệp không tồn tại '{filename}'", file=sys.stderr)
             return False
        except struct.error as e:
             print(f"Lỗi: Lỗi giải mã cấu trúc header: {e}", file=sys.stderr)
             return False
        except MemoryError:
             print(f"Lỗi: Không đủ bộ nhớ để tải opening book (size: 2^{self.log_size})", file=sys.stderr)
             return False
        except Exception as e:
             print(f"Lỗi không xác định khi tải opening book: {e}", file=sys.stderr)
             return False

    def save(self, output_file: str) -> bool:
        """
        Lưu opening book hiện tại vào một tệp nhị phân.

        Args:
            output_file: Đường dẫn đến tệp để lưu.

        Returns:
            True nếu lưu thành công, False nếu có lỗi.
        """
        if self.depth == -1 or self.partial_keys is None or self.values is None:
            print("Lỗi: Không có dữ liệu opening book để lưu.", file=sys.stderr)
            return False

        try:
            with open(output_file, 'wb') as ofs:
                # Ghi header
                header_format = 'bbbbbb'
                header_data = struct.pack(header_format,
                                           self.width,
                                           self.height,
                                           self.depth,
                                           self.partial_key_bytes,
                                           self.value_bytes, # Luôn là 1
                                           self.log_size)
                ofs.write(header_data)

                # Ghi mảng khóa một phần
                self.partial_keys.tofile(ofs)

                # Ghi mảng giá trị
                self.values.tofile(ofs)

            print(f"Đã lưu opening book vào: {output_file}", file=sys.stderr)
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

        Args:
            P: Đối tượng Position đại diện cho thế cờ cần tra cứu.

        Returns:
            Giá trị (uint8_t) từ opening book nếu thế cờ nằm trong độ sâu
            và được tìm thấy, ngược lại trả về 0.
        """
        # Kiểm tra xem book đã được tải và thế cờ có nằm trong độ sâu không
        if self.depth == -1 or P.nb_moves() > self.depth or self.size == 0:
            return 0

        full_key = P.key3()

        # Tính chỉ số (giả định đơn giản là modulo size)
        index = full_key % self.size

        # Tính khóa một phần mong đợi từ khóa đầy đủ
        partial_key_expected = self._calculate_partial_key(full_key)

        # Kiểm tra xem khóa một phần tại chỉ số có khớp không
        # Đây là phần xử lý xung đột đơn giản nhất
        if self.partial_keys[index] == partial_key_expected:
            return self.values[index]
        else:
            # Không khớp (có thể là vị trí trống hoặc xung đột chưa được xử lý)
            return 0

    def is_loaded(self) -> bool:
        """Kiểm tra xem opening book đã được tải thành công hay chưa."""
        return self.depth != -1 and self.size > 0

    # Python không cần destructor tường minh như C++,
    # bộ nhớ sẽ được giải phóng tự động khi không còn tham chiếu.


# Ví dụ sử dụng (tùy chọn)
if __name__ == "__main__":
    # --- Ví dụ Tạo và Lưu Book (Cần có dữ liệu thực tế) ---
    # Đoạn mã này chỉ minh họa cách gọi, không tạo dữ liệu book hợp lệ
    print("--- Ví dụ Lưu Book ---")
    book_to_save = Book(width=7, height=6)
    book_to_save.depth = 10 # Độ sâu ví dụ
    book_to_save.log_size = 10 # Kích thước ví dụ (2^10 = 1024)
    book_to_save.size = 1 << book_to_save.log_size
    book_to_save.partial_key_bytes = 2 # Khóa 16-bit ví dụ
    book_to_save.value_bytes = 1

    # Tạo dữ liệu giả
    book_to_save.partial_keys = array('H', [0] * book_to_save.size)
    book_to_save.values = array('B', [0] * book_to_save.size)
    # Điền dữ liệu thực tế vào đây nếu có...
    # Ví dụ: book_to_save.partial_keys[123] = some_partial_key
    #        book_to_save.values[123] = some_value

    save_filename = "dummy_opening.book"
    if book_to_save.size > 0: # Chỉ lưu nếu có dữ liệu (giả)
         book_to_save.save(save_filename)
    else:
        print("Bỏ qua lưu vì kích thước book là 0.")


    # --- Ví dụ Tải và Truy Vấn Book ---
    print("\n--- Ví dụ Tải và Truy Vấn Book ---")
    loaded_book = Book(width=7, height=6)

    # Giả sử tệp 'dummy_opening.book' tồn tại từ bước trên hoặc từ nguồn khác
    if os.path.exists(save_filename):
        if loaded_book.load(save_filename):
            print(f"Book đã tải thành công. Độ sâu: {loaded_book.depth}, Kích thước: 2^{loaded_book.log_size}")

            # Tạo một thế cờ ví dụ (cần lớp Position thực tế)
            example_pos = Position()
            # Giả sử example_pos.key3() trả về một khóa hợp lệ
            # và example_pos.nbMoves() trả về số nước đi

            # Đặt giá trị giả cho key3 và nbMoves để kiểm tra
            example_pos.key3 = lambda: 123456789 # Khóa ví dụ
            example_pos.nb_moves = lambda: 5       # Số nước đi ví dụ (phải <= depth)

            if example_pos.nb_moves() <= loaded_book.depth:
                 value = loaded_book.get(example_pos)
                 print(f"Giá trị cho thế cờ ví dụ (key={example_pos.key3()}): {value}")
            else:
                 print(f"Thế cờ ví dụ (moves={example_pos.nb_moves()}) vượt quá độ sâu của book ({loaded_book.depth})")

        else:
            print("Tải book thất bại.")

        # Clean up dummy file
        # os.remove(save_filename)
        print(f"(Giữ lại tệp {save_filename} để kiểm tra)")
    else:
        print(f"Tệp {save_filename} không tồn tại để tải.")