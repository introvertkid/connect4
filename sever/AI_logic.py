import sys
import os
import cProfile
from typing import List, Dict
import time
import pstats
import subprocess

# --- Cấu hình đường dẫn ---
# **** Đảm bảo file Python này nằm ở 'c:\Users\sonle\Documents\Connect4_AI\connect4\' ****
# **** và file exe nằm ở 'c:\Users\sonle\Documents\Connect4_AI\connect4\sever\c4solver.exe' ****
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Xảy ra nếu chạy tương tác hoặc __file__ không được định nghĩa
    SCRIPT_DIR = os.getcwd() # Lấy thư mục làm việc hiện tại làm dự phòng
    print(f"Cảnh báo: Không thể xác định __file__, sử dụng thư mục hiện tại: {SCRIPT_DIR}")

SEVER_DIR = os.path.join(SCRIPT_DIR) # Đường dẫn đến thư mục sever
EXE_NAME = "c4solver.exe"
EXE_PATH = os.path.join(SEVER_DIR, EXE_NAME) # Đường dẫn đầy đủ đến file exe
BOOK_PATH = os.path.join(SEVER_DIR, "7x6.book")

# In ra để kiểm tra đường dẫn được tạo ra
print(f"DEBUG: SCRIPT_DIR = {SCRIPT_DIR}")
print(f"DEBUG: SEVER_DIR = {SEVER_DIR}")
print(f"DEBUG: EXE_PATH = {EXE_PATH}")


# --- Phần Solver Python (tùy chọn) ---
# ... (Giữ nguyên nếu cần)

def convert_board_to_movesequence(board: List[List[int]]) -> str:
    """
    Chuyển đổi trạng thái bàn cờ (board) 2D thành chuỗi nước đi (move_sequence).
    Trả về chuỗi rỗng nếu board không hợp lệ hoặc không thể tái tạo.
    """
    move_sequence = ""
    height = len(board)
    width = len(board[0]) if board and board[0] else 0
    if not width or not height:
        return ""

    col_heights = [0] * width
    flat_board = [[board[r][col] for r in range(height - 1, -1, -1)] for col in range(width)]
    num_pieces_on_board = sum(1 for r in board for cell in r if cell != 0)
    current_player = 1

    for i in range(num_pieces_on_board):
        move_found_for_player = False
        for col in range(width):
            if col_heights[col] < height and flat_board[col][col_heights[col]] == current_player:
                move_sequence += str(col + 1)
                col_heights[col] += 1
                move_found_for_player = True
                break
        if not move_found_for_player:
            print(f"LỖI trong convert_board_to_movesequence: Không thể tái tạo nước đi thứ {i+1} cho người chơi {current_player}.")
            print(f"Board: {board}")
            print(f"Col heights tại thời điểm lỗi: {col_heights}")
            return "" # Trả về chuỗi rỗng báo hiệu lỗi/không hợp lệ

        current_player = 3 - current_player

    return move_sequence

def get_best_move_cpp(board: List[List[int]], valid_moves: List[int]) -> int:
    """
    Lấy nước đi tốt nhất bằng cách gọi file thực thi C++ c4solver.exe.
    """
    if not valid_moves:
        print("Cảnh báo: Không có nước đi hợp lệ nào.")
        return -1

    if not valid_moves:
        print("Cảnh báo: Không có nước đi hợp lệ nào.")
        return -1 # Hoặc raise ValueError

    # --- BEGIN: Xử lý bảng rỗng ---
    # Kiểm tra xem tất cả các ô có bằng 0 không
    is_empty_board = all(cell == 0 for row in board for cell in row)

    if is_empty_board:
        print("DEBUG: Bảng rỗng, trả về nước đi mặc định (cột giữa).")
        # Trả về cột giữa (index 3) nếu hợp lệ
        center_col = 3
        if center_col in valid_moves:
            return center_col
        elif valid_moves: # Nếu cột giữa không hợp lệ (lạ), trả về nước hợp lệ đầu tiên
             print(f"Cảnh báo: Bảng rỗng nhưng cột giữa {center_col} không hợp lệ? Trả về {valid_moves[0]}.")
             return valid_moves[0]
        else:
             # Trường hợp cực hiếm: bảng rỗng nhưng không có nước đi hợp lệ?
             print("LỖI: Bảng rỗng nhưng không có nước đi hợp lệ nào được cung cấp.")
             return -1 # Hoặc raise lỗi
    # --- END: Xử lý bảng rỗng ---

    # 1. Chuyển đổi board sang move_sequence
    move_sequence = convert_board_to_movesequence(board)
    print(f"DEBUG: Board được chuyển thành move_sequence: '{move_sequence}'")

    # *** Xử lý lỗi nếu sequence rỗng nhưng board không rỗng ***
    num_pieces_on_board = sum(1 for r in board for cell in r if cell != 0)
    if not move_sequence and num_pieces_on_board > 0:
        raise ValueError(f"LỖI: Không thể tạo move_sequence hợp lệ từ board cung cấp. Board có thể không hợp lệ.")

    # 2. Kiểm tra sự tồn tại của file exe một lần nữa với đường dẫn đã debug
    if not os.path.exists(EXE_PATH):
        # In lại đường dẫn kiểm tra lần cuối
        print(f"Kiểm tra lại đường dẫn file exe: {EXE_PATH}")
        raise FileNotFoundError(f"LỖI: Không tìm thấy file thực thi tại đường dẫn đã xác định: {EXE_PATH}")

    scores_from_cpp = [-10000] * len(board[0])

    try:
        # 3. Chuẩn bị và thực thi lệnh C++
        command = [EXE_PATH]
        print(f"DEBUG: Đang chạy lệnh: {' '.join(command)}")
        print(f"DEBUG: Input (stdin) cho C++: '{move_sequence}'")
        print(f"DEBUG: Chạy từ thư mục (cwd): {SEVER_DIR}") # Kiểm tra cwd

        result = subprocess.run(
            command,
            input=move_sequence,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            cwd=SEVER_DIR # Rất quan trọng: chạy exe từ thư mục chứa nó
        )
        # ... (Phần phân tích output và chọn nước đi giữ nguyên như trước) ...
        # 4. Phân tích output từ stdout của C++
        print(f"DEBUG: C++ stdout:\n---\n{result.stdout.strip()}\n---")
        if result.stderr:
            print(f"DEBUG: C++ stderr:\n---\n{result.stderr.strip()}\n---")

        output_lines = result.stdout.strip().splitlines()
        if not output_lines:
            # Xử lý trường hợp C++ không trả về gì ngay cả khi chạy thành công (mã 0)
             if move_sequence == "": # Nếu input là rỗng, có thể output cũng rỗng là đúng
                 print("DEBUG: Input sequence rỗng, output từ C++ cũng rỗng.")
                 # Cần quyết định giá trị trả về cho trường hợp board trống
                 # Có thể C++ trả về điểm cho các nước đi đầu tiên?
                 # Giả sử C++ trả về lỗi hoặc output không đúng chuẩn nếu seq rỗng
                 raise ValueError("LỖI: File C++ không trả về output nào cho input rỗng (cần kiểm tra logic C++).")
             else:
                 raise ValueError("LỖI: File C++ không trả về output nào.")


        last_line = output_lines[-1].strip()
        parts = last_line.split()
        expected_parts = 1 + len(board[0])
        if len(parts) < expected_parts:
             # In thêm thông tin debug nếu lỗi phân tích
            print(f"DEBUG: Số phần tử nhận được: {len(parts)}, kỳ vọng: {expected_parts}")
            print(f"DEBUG: Các phần tử: {parts}")
            raise ValueError(f"LỖI: Output từ C++ không đúng định dạng. Kỳ vọng {expected_parts} phần, nhận được {len(parts)}: '{last_line}'")

        score_strings = parts[1:expected_parts]
        scores_from_cpp = [int(s) for s in score_strings]
        print(f"DEBUG: Điểm số phân tích được từ C++: {scores_from_cpp}")

    except FileNotFoundError:
        raise FileNotFoundError(f"LỖI: Không thể chạy. Không tìm thấy file thực thi tại: {EXE_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"\n--- LỖI: Chương trình C++ kết thúc với mã lỗi {e.returncode} ---")
        print(f"Lệnh đã chạy: {' '.join(e.cmd)}")
        print(f"Input gửi đi: '{move_sequence}'")
        if e.stdout: print(f"Output (stdout) khi lỗi:\n{e.stdout.strip()}")
        if e.stderr: print(f"Error Output (stderr) khi lỗi:\n{e.stderr.strip()}")
        raise RuntimeError(f"Solver C++ thất bại với mã lỗi {e.returncode}") from e
    except (ValueError, IndexError) as e:
        output_received = result.stdout.strip() if 'result' in locals() else "(Không có output hoặc lỗi trước đó)"
        print(f"\n--- LỖI: Không thể phân tích output từ C++ ---")
        print(f"Output nhận được: {output_received}")
        print(f"Lỗi chi tiết: {e}")
        raise ValueError(f"Không thể phân tích output của solver C++: {e}") from e
    except Exception as e:
        print(f"\n--- LỖI KHÔNG MONG MUỐN KHI TƯƠNG TÁC VỚI C++ ---")
        print(f"Loại lỗi: {type(e).__name__}")
        print(f"Chi tiết: {e}")
        raise RuntimeError("Lỗi không mong muốn khi tương tác với solver C++") from e

    # 5. Chọn nước đi tốt nhất
    best_score = -float('inf')
    best_col = -1
    for col_index in valid_moves:
        if 0 <= col_index < len(scores_from_cpp):
            current_score = scores_from_cpp[col_index]
            # Thêm debug điểm số cho nước đi hợp lệ
            # print(f"DEBUG: Xét cột {col_index} (hợp lệ), điểm C++: {current_score}")
            if current_score > best_score:
                best_score = current_score
                best_col = col_index
        else:
             print(f"CẢNH BÁO: Nước đi hợp lệ {col_index} nằm ngoài phạm vi điểm trả về từ C++ (0-{len(scores_from_cpp)-1})")

    if best_col == -1:
        print("CẢNH BÁO: Không thể xác định nước đi tốt nhất từ C++ và valid_moves.")
        if valid_moves:
            print("DEBUG: Trả về nước đi hợp lệ đầu tiên làm dự phòng.")
            return valid_moves[0]
        else:
             raise ValueError("Không có nước đi hợp lệ và không thể xác định nước đi tốt nhất.")

    print(f"DEBUG: Nước đi tốt nhất được chọn (cột 0-based): {best_col+1} với điểm {best_score}")
    return best_col


# --- Khối main để kiểm tra ---
if __name__ == "__main__":
    # *** QUAN TRỌNG: Sử dụng một trạng thái bàn cờ HỢP LỆ để kiểm tra ***
    # Ví dụ: Bàn cờ sau các nước đi 4, 4, 5, 3, 6, 5, 7 (1-based)
    # Player 1: 4, 5, 6, 7
    # Player 2: 4, 3, 5
    board_example_valid = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0], # Row 4
        [0, 0, 0, 1, 0, 0, 0]  # Row 5 (bottom)
    ]
    # Nước đi tiếp theo là của Player 2
    # Các cột hợp lệ (chưa đầy): 0, 1, 2, 3, 4, 5, 6 (giả sử chưa cột nào đầy)
    valid_moves_example_valid = [col for col in range(7) if board_example_valid[0][col] == 0]

    print("--- Bắt đầu kiểm tra gọi Solver C++ với board hợp lệ ---")
    start_time_cpp = time.time()
    try:
        # Gọi hàm sử dụng C++ solver với board hợp lệ
        best_move = get_best_move_cpp(board_example_valid, valid_moves_example_valid)
        print(f"\n>>> Kết quả: Nước đi tốt nhất được đề xuất bởi C++ là cột: {best_move}")
    except Exception as e:
        print(f"\n--- LỖI TRONG QUÁ TRÌNH KIỂM TRA ---")
        print(f"Lỗi: {e}")
        # In traceback để biết lỗi chi tiết hơn
        import traceback
        traceback.print_exc()
    end_time_cpp = time.time()
    print(f"--- Kết thúc kiểm tra Solver C++. Thời gian: {end_time_cpp - start_time_cpp:.4f} giây ---")